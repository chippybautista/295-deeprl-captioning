import sys

# ye, doing this the CS freshie way yeseeeess
sys.path.append('pycocoevalcap')
sys.path.append('pycocoevalcap/bleu')
sys.path.append('pycocoevalcap/meteor')
sys.path.append('pycocoevalcap/rouge')
sys.path.append('pycocoevalcap/spice')
sys.path.append('pycocoevalcap/cider')


import numpy as np
import torch
from sklearn.metrics import pairwise_distances
from sklearn.metrics.pairwise import cosine_similarity
from torch.nn.utils.rnn import pad_sequence
from cider.cider import Cider

from settings import *


class Environment(object):
    def __init__(self, bert_client=None):
        self.vocabulary = np.load('vocabulary.npy')
        self.cider = Cider()
        self.bert_client = bert_client

    def reset(self, b_img_features, b_captions=None):
        """
        This does all the initialization for a given batch of image features
        and their respective ground truth captions.
        """
        # will need to keep track of current batch size else it's going to
        # throw an error when it's the last iteration and the given batch size
        # is less than the set BATCH_SIZE
        curr_batch_size = b_img_features.shape[0]

        if b_captions:
            # just some preprocessing here for use in supervised learning
            # with XE Loss.
            # convert words to their indeces in the vocabulary
            b_indeces = [self.caption_to_indeces(c) for c in b_captions]
            # then pad them to the max sequence length of the batch
            b_indeces = pad_sequence(b_indeces, batch_first=True)
        else:
            # When using this for the RL setting
            b_indeces = None

        b_pooled_img_features = [
            torch.sum(img_features, 0) / IMAGE_FEATURE_REGIONS
            for img_features in b_img_features
        ]

        # define initial LSTM states
        lstm_states = {
            'language_h': None,
            'language_c': None,
            'attention_h': None,
            'attention_c': None
        }

        state = {
            # shape (b, 1000)
            'language_lstm_h': torch.Tensor(
                np.repeat([np.zeros(LSTM_HIDDEN_UNITS)], curr_batch_size, 0)
            ),
            # shape (b, 1, 2048) stack converts a list of tensors into a tensor
            'pooled_img_features': torch.stack(b_pooled_img_features),
            # shape (b, )
            'prev_word_indeces': torch.zeros(curr_batch_size,
                                             dtype=torch.int64),
            # shape (b, 36, 2048)
            'img_features': torch.Tensor(b_img_features)
        }

        return b_indeces, state, lstm_states

    def get_context_score(self, gt_vectors, predictions):
        curr_batch_size = len(predictions)
        distances = []

        p_ = [s[0].replace(' <EOS>', '')
              for s in predictions]
        p_vectors = self.bert_client.encode(p_)

        for i in range(0, curr_batch_size):
            mean_gt_distance = np.triu(pairwise_distances(
                gt_vectors[i], metric='manhattan'))
            mean_gt_distance = mean_gt_distance[mean_gt_distance > 0].mean()
            mean_pred_dist = pairwise_distances(gt_vectors[i],
                                                p_vectors[i].reshape(1, -1),
                                                'manhattan').mean()
            distances.append(
                1 - (abs(mean_gt_distance - mean_pred_dist) / mean_pred_dist)
            )
        return np.array(distances)

    def probs_to_word(self, probabilities, mode='sample'):
        if mode == 'sample':
            # Get random word, But for finetuning with RL,
            # (Rennie and anderson's paper)
            # references use beam search. Should try implementing later.
            idx = np.random.choice(len(self.vocabulary), p=probabilities)
            return idx, self.vocabulary[idx]

        idx = np.argmax(probabilities)
        return idx, self.vocabulary[idx]

    def caption_to_indeces(self, caption):
        def _to_index(w):
            return np.where(self.vocabulary == w)[0][0]

        words = caption.split()
        try:
            indeces = [_to_index(w) for w in words]
        except IndexError:
            # If the word was not included in the extracted vocab,
            # just ignore it.
            indeces = np.zeros(len(words))

        return torch.LongTensor(indeces)

    def encode_to_one_hot(self, index):
        onehot = np.zeros(VOCABULARY_SIZE)
        onehot[index] = 1
        return onehot

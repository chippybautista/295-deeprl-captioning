# Files
CAPTIONS_DIR = '../data/coco/annotations/captions_{}2014.json'
KARPATHY_SPLIT_DIR = '../data/karpathy_splits/coco2014_cocoid.{}.txt'
FEATURES_DIR = '../data/features/extracts/{}.npy'
MEAN_VEC_DIR = '../data/mean_vectors/{}.npy'

# Hyperparameters
DISCOUNT_FACTOR = 0.99
LEARNING_RATE = 0.01
BATCH_SIZE = 16
DO_SHUFFLE = True

# Environment
MAX_WORDS = 20

# Network dimensions (hardcoding here haha...)
# Follows Bottom-Up Top-Down paper.
LSTM_HIDDEN_UNITS = 1000
ATTENTION_HIDDEN_UNITS = 512
WORD_EMBEDDING_SIZE = 1000
VOCABULARY_SIZE = 10000  # not exact. change this later.

IMAGE_FEATURE_DIM = 2048
IMAGE_FEATURE_REGIONS = 36

ATTENTION_LSTM_INPUT_SIZE = (
    LSTM_HIDDEN_UNITS +
    IMAGE_FEATURE_DIM +
    WORD_EMBEDDING_SIZE
)

LANGUAGE_LSTM_INPUT_SIZE = (
    IMAGE_FEATURE_DIM +
    LSTM_HIDDEN_UNITS
)
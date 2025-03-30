import random

import numpy as np
import tensorflow.random


def set_seed(SEED: int) -> None:
    """
    Set a global random seed for NumPy, Python's 'random' module, and TensorFlow.

    This ensures reproducible results by initializing the random number generators
    for each library with the same seed value.

    Args:
        SEED (int): The seed value to set for all random number generators.
    """
    np.random.seed(SEED)
    random.seed(SEED)
    tensorflow.random.set_seed(SEED)

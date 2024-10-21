import numpy as np
import random

def set_seed(SEED:int):
    np.random.seed(SEED)
    random.seed(SEED)
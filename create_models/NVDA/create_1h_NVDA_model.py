import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from src.Classes.ModelCreator import ModelCreator

creator = ModelCreator("TSLA",  "1h")

creator.train_tune(plot=False)


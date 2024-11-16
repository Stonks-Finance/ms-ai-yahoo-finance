import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from src.Classes.ModelCreator import ModelCreator

creator = ModelCreator("DIS",  "5m")

creator.train_tune(plot=True)


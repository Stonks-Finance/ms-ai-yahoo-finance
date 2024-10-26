from src.Classes.ModelCreator import ModelCreator
from src.SEEDS import set_seed

SEED:int=6
set_seed(SEED)

creator=ModelCreator("AAPL",".h5",["1m","1h"])

creator.train_tune(plot=True)
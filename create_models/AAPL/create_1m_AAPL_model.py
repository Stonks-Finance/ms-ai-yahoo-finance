from src.Classes.ModelCreator import ModelCreator

creator = ModelCreator("AAPL",  "1m")

creator.train_tune(plot=True)


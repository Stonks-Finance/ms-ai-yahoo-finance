from src.Classes.ModelCreator import ModelCreator

creator = ModelCreator("AAPL",  "1h")

creator.train_tune(plot=True)


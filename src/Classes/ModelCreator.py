import os
import keras
from src.Classes.Tuner import Tuner
from typing import  Dict,Optional
from settings import TUNING_HISTORIES_DIRECTORY


class ModelCreator(Tuner):
    def __init__ (self,
                  stock_symbol: str,
                  interval: str,
                  max_trials: int = 10,
                  executions_per_trial: int = 3,
                  directory: str = TUNING_HISTORIES_DIRECTORY,
                  ) -> None:
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        
        tuning_histories_dir = os.path.join(project_root, directory)
        models_dir = os.path.join(project_root, "models")
        
        super().__init__(
            max_trials,
            executions_per_trial,
            tuning_histories_dir,
            models_dir)
        
        self.stock_symbol = stock_symbol
        self.interval = interval
        self.models_dir = models_dir
        self.model = None
    
    def train_tune (self,
                    epochs: int = 10,
                    batch_size: int = 32,
                    metric: str = "val_loss",
                    plot: bool = False,
                    verbose: bool = True) -> keras.Model:
        
        print(f"Tuning for interval: {self.interval}")
        
        model = self._Tuner__tune(self.stock_symbol,
                                  self.interval,
                                  epochs,
                                  batch_size,
                                  metric,
                                  plot,
                                  verbose)
        
        self.model = model
        return model
    
    def get_hps (self) -> Optional[Dict[str, any]]:
        
        if self.hps:
            return {param: self.hps.get(param) for param in self.hps.values}
        else:
            raise ValueError("Hyperparameters have not been tuned yet.")

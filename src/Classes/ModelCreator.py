import os
from typing import Dict, Optional

import keras

from src.Classes.Tuner import Tuner
from settings import TUNING_HISTORIES_DIRECTORY, MODELS_DIRECTORY


class ModelCreator(Tuner):
    """
    ModelCreator is a specialized subclass of Tuner that manages hyperparameter tuning
    and model creation for a specific stock symbol and time interval.
    """

    def __init__(
        self,
        stock_symbol: str,
        interval: str,
        max_trials: int = 10,
        executions_per_trial: int = 3,
        tuning_dir: str = TUNING_HISTORIES_DIRECTORY,
    ) -> None:
        """
        Initialize a ModelCreator instance for a specific stock symbol and time interval.

        Args:
            stock_symbol (str): The ticker symbol of the stock (e.g. 'AAPL').
            interval (str): The data interval (e.g. '1h').
            max_trials (int, optional): Maximum number of hyperparameter trials. Defaults to 10.
            executions_per_trial (int, optional): Number of executions per trial to reduce variance. Defaults to 3.
            tuning_dir (str, optional): Directory where tuning logs are stored. Defaults to TUNING_HISTORIES_DIRECTORY.
        """
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))

        tuning_dir = os.path.join(project_root, tuning_dir)
        models_dir = os.path.join(project_root, MODELS_DIRECTORY)

        super().__init__(
            max_trials,
            executions_per_trial,
            tuning_dir,
            models_dir
        )

        self.stock_symbol = stock_symbol
        self.interval = interval
        self.models_dir = models_dir
        self.model = None

    def train_tune(
        self,
        epochs: int = 10,
        batch_size: int = 32,
        metric: str = "val_loss",
        plot: bool = False,
        verbose: bool = True
    ) -> keras.Model:
        """
        Perform hyperparameter tuning and model training for the given stock symbol and interval.

        Args:
            epochs (int, optional): Number of training epochs. Defaults to 10.
            batch_size (int, optional): Batch size used during training. Defaults to 32.
            metric (str, optional): Metric to monitor (e.g. 'val_loss') for tuning. Defaults to 'val_loss'.
            plot (bool, optional): If True, plot Actual vs Predicted after training. Defaults to False.
            verbose (bool, optional): If True, print progress logs. Defaults to True.

        Returns:
            keras.Model: The best performing model after hyperparameter tuning.
        """
        print(f"Tuning for interval: {self.interval}")

        model = self._Tuner__tune(
            self.stock_symbol,
            self.interval,
            epochs,
            batch_size,
            metric,
            plot,
            verbose
        )

        self.model = model
        return model

    def get_hps(self) -> Optional[Dict[str, any]]:
        """
        Retrieve the best hyperparameters found during the tuning process.

        Returns:
            Optional[Dict[str, any]]: A dictionary mapping hyperparameter names to their best values.

        Raises:
            ValueError: If hyperparameters have not been tuned yet.
        """
        if self.hps:
            return {param: self.hps.get(param) for param in self.hps.values}
        else:
            raise ValueError("Hyperparameters have not been tuned yet.")

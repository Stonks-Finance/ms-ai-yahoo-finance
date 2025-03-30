import os
from typing import Optional

import keras
import matplotlib.pyplot as plt
from keras_tuner import RandomSearch, HyperParameters

from src.get_data import create_sequences, prepare_data, scaler
from settings import TUNING_HISTORIES_DIRECTORY, MODELS_DIRECTORY


class TuningException(Exception):
    """
    Custom exception for Tuning-related errors.
    """
    pass


class Tuner:
    """
    Handles hyperparameter tuning for LSTM models using Keras Tuner with RandomSearch.
    This class defines how the model is built and searched, including model architecture,
    optimization settings, and data preparation routines.
    """

    def __init__(
        self,
        max_trials: int = 10,
        executions_per_trial: int = 3,
        directory: str = TUNING_HISTORIES_DIRECTORY,
        models_directory: str = MODELS_DIRECTORY
    ) -> None:
        """
        Initialize the Tuner with various tuning parameters and directories.

        Args:
            max_trials (int, optional): Maximum number of hyperparameter trials. Defaults to 10.
            executions_per_trial (int, optional): Number of executions per trial to reduce variance. Defaults to 3.
            directory (str, optional): Directory path where tuning logs and trial information will be stored.
                Defaults to TUNING_HISTORIES_DIRECTORY.
            models_directory (str, optional): Directory where best models are saved. Defaults to MODELS_DIRECTORY.
        """
        self.max_trials: int = max_trials
        self.executions_per_trial: int = executions_per_trial
        self.directory: str = directory
        self.models_directory: str = models_directory
        self.project_name: str = ""
        self.tuner: Optional[RandomSearch] = None
        self.hps = None

    @staticmethod
    def __validate_dropout_params(dropout: bool, dropout_deg: float) -> None:
        """
        Validate dropout parameters for the model.

        Args:
            dropout (bool): Whether dropout is enabled.
            dropout_deg (float): Dropout rate (should be between 0 and 1).

        Raises:
            TuningException: If dropout is True but the dropout_deg is not in (0, 1).
        """
        if dropout and not (0 < dropout_deg < 1):
            raise TuningException(
                f"Invalid dropout_deg value: {dropout_deg}. It should be between 0 and 1."
            )

    @staticmethod
    def __build_model(
        hp: HyperParameters,
        dropout: bool = False,
        dropout_deg: float = 0.0
    ) -> keras.Model:
        """
        Build and compile a Keras LSTM model based on hyperparameters.

        Args:
            hp (HyperParameters): Hyperparameter search space from Keras Tuner.
            dropout (bool, optional): Whether to include dropout layers. Defaults to False.
            dropout_deg (float, optional): The dropout rate if dropout is True. Defaults to 0.0.

        Returns:
            keras.Model: A compiled Keras model.

        Raises:
            TuningException: If there is an error building the model.
        """
        try:
            Tuner.__validate_dropout_params(dropout, dropout_deg)

            lstm_units = hp.Int("lstm_units", min_value=32, max_value=128, step=32)
            num_layers = hp.Int("num_layers", min_value=1, max_value=3)
            seq_length = hp.Int("seq_length", min_value=20, max_value=40, step=5)
            learning_rate = hp.Float("learning_rate", min_value=1e-4, max_value=1e-2, sampling="log")

            model = keras.Sequential()
            model.add(keras.layers.Input(shape=(seq_length, 1)))
            model.add(keras.layers.LSTM(lstm_units, return_sequences=(num_layers > 1)))
            for i in range(1, num_layers):
                model.add(keras.layers.LSTM(lstm_units, return_sequences=(i < num_layers - 1)))
                if dropout:
                    model.add(keras.layers.Dropout(dropout_deg))
            model.add(keras.layers.Dense(1))

            model.compile(
                optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
                loss="mean_squared_error"
            )
            return model
        except Exception as e:
            raise TuningException(f"Error building model: {str(e)}")

    @staticmethod
    def __plot(model: keras.Model, X, Y, stock_symbol: str) -> None:
        """
        Plot actual vs. predicted stock prices using the trained model.

        Args:
            model (keras.Model): The trained Keras model.
            X: The input features to generate predictions (numpy array or similar).
            Y: The true target values corresponding to X (numpy array or similar).
            stock_symbol (str): Ticker symbol, used for the plot title.
        """
        y_pred = model.predict(X)
        y_pred_rescaled = scaler.inverse_transform(y_pred.reshape(-1, 1))
        Y_rescaled = scaler.inverse_transform(Y.reshape(-1, 1))

        plt.figure(figsize=(14, 7))
        plt.plot(Y_rescaled, color="blue", label="Actual Price")
        plt.plot(y_pred_rescaled, color="red", label="Predicted Price")
        plt.title(f"Actual vs Predicted Stock Prices ({stock_symbol})")
        plt.xlabel("Time")
        plt.ylabel("Stock Price")
        plt.legend()
        plt.show()

    def __tune(
        self,
        stock_symbol: str,
        interval: str,
        epochs: int = 10,
        batch_size: int = 32,
        metric: str = "val_loss",
        plot: bool = False,
        _verbose: bool = False
    ) -> Optional[keras.Model]:
        """
        Run the hyperparameter search, train the best model, and optionally plot results.

        Args:
            stock_symbol (str): The ticker symbol of the stock (e.g., 'AAPL').
            interval (str): The data interval (e.g., '1h').
            epochs (int, optional): Number of training epochs for each trial. Defaults to 10.
            batch_size (int, optional): Batch size for training. Defaults to 32.
            metric (str, optional): Keras metric to optimize (e.g., 'val_loss'). Defaults to 'val_loss'.
            plot (bool, optional): If True, plot the actual vs. predicted prices after training. Defaults to False.
            _verbose (bool, optional): If True, prints progress. Defaults to False.

        Returns:
            Optional[keras.Model]: The best-performing model found, or None if something fails.

        Raises:
            TuningException: If there's an error during the tuning process or if data is empty.
        """
        try:
            # Define project name/location for KerasTuner logs
            self.project_name = os.path.join(
                self.directory,
                stock_symbol,
                f"{stock_symbol}_{interval}_tuning_hist"
            )

            # Initialize the RandomSearch tuner
            self.tuner = RandomSearch(
                self.__build_model,
                objective=metric,
                max_trials=self.max_trials,
                executions_per_trial=self.executions_per_trial,
                directory=self.directory,
                project_name=self.project_name
            )

            # Prepare data
            train_data_scaled, test_data_scaled = prepare_data(stock_symbol, interval)
            if train_data_scaled.size == 0 or test_data_scaled.size == 0:
                raise TuningException("Training or testing data is empty.")

            # Create sequences for training and validation
            X_train, y_train = create_sequences(train_data_scaled)
            X_val, y_val = create_sequences(test_data_scaled)

            # Define the filepath for saving the best model
            keras_filepath: str = os.path.join(
                self.models_directory,
                stock_symbol,
                f"{interval}_{stock_symbol}_best_model.keras"
            )
            os.makedirs(os.path.dirname(keras_filepath), exist_ok=True)

            # Define callbacks
            callbacks = [
                keras.callbacks.EarlyStopping(
                    monitor=metric,
                    patience=5,
                    restore_best_weights=True,
                    verbose=_verbose
                ),
                keras.callbacks.ReduceLROnPlateau(
                    monitor=metric,
                    factor=0.5,
                    patience=3,
                    min_lr=1e-6,
                    verbose=_verbose
                ),
                keras.callbacks.ModelCheckpoint(
                    filepath=keras_filepath,
                    monitor=metric,
                    save_best_only=True,
                    verbose=_verbose
                ),
            ]

            # Perform hyperparameter search
            self.tuner.search(
                X_train,
                y_train,
                epochs=epochs,
                validation_data=(X_val, y_val),
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=_verbose
            )

            # Retrieve the best hyperparameters
            best_hps = self.tuner.get_best_hyperparameters(num_trials=1)[0]
            self.hps = best_hps
            if _verbose:
                print(f"Best LSTM units: {best_hps.get('lstm_units')}")
                print(f"Best number of layers: {best_hps.get('num_layers')}")
                print(f"Best sequence length: {best_hps.get('seq_length')}")
                print(f"Best learning rate: {best_hps.get('learning_rate')}")

            # Build the best model and train it fully
            best_model = self.tuner.hypermodel.build(best_hps)
            best_model.fit(
                X_train,
                y_train,
                epochs=epochs,
                validation_data=(X_val, y_val),
                batch_size=batch_size,
                callbacks=callbacks,
                verbose=_verbose
            )

            # Save the best model
            best_model.save(keras_filepath)

            # Optional plot
            if plot:
                self.__plot(best_model, X_val, y_val, stock_symbol)

            return best_model

        except Exception as e:
            raise TuningException(f"Error during tuning: {str(e)}")

from typing import Tuple, List, Callable

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

from src.SEEDS import set_seed
from settings import SEED

# Set a global seed for reproducibility across the module
set_seed(SEED)

# A global MinMaxScaler instance for scaling stock price data
scaler = MinMaxScaler()


def scale_data(train_data: pd.DataFrame, test_data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    """
    Scale the training and testing data using a global MinMaxScaler.

    Args:
        train_data (pd.DataFrame): The training dataset (e.g., 'Close' prices).
        test_data (pd.DataFrame): The testing dataset (same columns as train_data).

    Returns:
        Tuple[np.ndarray, np.ndarray]: The scaled versions of train_data and test_data as NumPy arrays.
    """
    global scaler
    train_scaled: np.ndarray = scaler.fit_transform(train_data)
    test_scaled: np.ndarray = scaler.transform(test_data)
    return train_scaled, test_scaled


def prepare_data(stock_name: str, interval: str = "1h") -> Tuple[np.ndarray, np.ndarray]:
    """
    Download and prepare stock data for training and testing.

    - Downloads data from Yahoo Finance for the specified stock over a 2-year period at the given interval.
    - Splits the data into training (80%) and testing (20%) subsets in chronological order (shuffle=False).
    - Scales the 'Close' price column using scale_data().

    Args:
        stock_name (str): The ticker symbol of the stock (e.g. 'AAPL').
        interval (str, optional): The data interval (e.g. '1h'). Defaults to '1h'.

    Returns:
        Tuple[np.ndarray, np.ndarray]: A tuple of (train_data_scaled, test_data_scaled).

    Raises:
        RuntimeError: If there's an error during data downloading or preparation.
        ValueError: If an invalid interval is provided.
    """
    try:
        match interval:
            case "1h":
                data = yf.download(stock_name, period="2y", interval=interval)
            case _:
                raise ValueError(f"Invalid interval {interval}")

        data.index = pd.to_datetime(data.index)
        data.dropna(inplace=True)

        train_data, test_data = train_test_split(
            data[["Close"]],
            test_size=0.2,
            shuffle=False,
            random_state=SEED
        )

        train_data_sc, test_data_sc = scale_data(train_data[["Close"]], test_data[["Close"]])
        return train_data_sc, test_data_sc

    except Exception as e:
        raise RuntimeError(f"Error preparing data: {e}")


def create_sequences(datas: np.ndarray, seq_length: int = 20) -> Tuple[np.ndarray, np.ndarray]:
    """
    Convert a time series array into a supervised learning format, creating (X, y) sequences.

    Each X is a window of 'seq_length' consecutive time steps from 'datas', and y is the value 
    immediately following that window.

    Args:
        datas (np.ndarray): The scaled time series data.
        seq_length (int, optional): Number of time steps to include in each sequence. Defaults to 20.

    Returns:
        Tuple[np.ndarray, np.ndarray]: Arrays (X, y). X has shape (num_sequences, seq_length, features).
                                      y has shape (num_sequences, features).
    """
    x: List = []
    y: List = []
    for i in range(len(datas) - seq_length):
        x.append(datas[i:i + seq_length])
        y.append(datas[i + seq_length])
    return np.array(x), np.array(y)


def __add_price_increase_flag(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add a boolean flag 'is_price_increased' indicating whether the 'Close' price
    increased compared to the previous row.

    Args:
        data (pd.DataFrame): A DataFrame containing a 'Close' price column.

    Returns:
        pd.DataFrame: The same DataFrame with an added 'is_price_increased' column.
    """
    data["is_price_increased"] = data["Close"].diff() > 0
    return data


def __calculate_adj_close_difference(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add a column 'adj_close_diff' representing the day-to-day difference in 'Close' prices.

    Args:
        data (pd.DataFrame): A DataFrame containing a 'Close' price column.

    Returns:
        pd.DataFrame: The same DataFrame with an added 'adj_close_diff' column.
    """
    data["adj_close_diff"] = data["Close"].diff().fillna(0)
    return data


def __calculate_adj_close_percentage_change(data: pd.DataFrame) -> pd.DataFrame:
    """
    Add a column 'adj_close_pct_change' representing the percentage change in 'Close' prices
    compared to the previous row.

    Args:
        data (pd.DataFrame): A DataFrame containing a 'Close' price column.

    Returns:
        pd.DataFrame: The same DataFrame with an added 'adj_close_pct_change' column.
    """
    data["adj_close_pct_change"] = data["Close"].pct_change().fillna(0)
    return data


def pipe(data: pd.DataFrame) -> pd.DataFrame:
    """
    Execute a pipeline of transformations on the given DataFrame. Specifically:
    1. Add a price increase flag.
    2. Calculate day-to-day difference in 'Close' price.
    3. Calculate percentage change in 'Close' price.

    Args:
        data (pd.DataFrame): A DataFrame with a 'Close' column.

    Returns:
        pd.DataFrame: The transformed DataFrame with additional columns:
            - 'is_price_increased'
            - 'adj_close_diff'
            - 'adj_close_pct_change'
    """
    functions: List[Callable] = [
        __add_price_increase_flag,
        __calculate_adj_close_difference,
        __calculate_adj_close_percentage_change
    ]

    for function in functions:
        data = data.pipe(function)
    return data

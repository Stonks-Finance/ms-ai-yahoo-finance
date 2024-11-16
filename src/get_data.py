import pandas as pd
import yfinance as yf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split
from src.SEEDS import set_seed
from typing import Tuple, List, Callable
from settings import SEED

set_seed(SEED)

scaler = MinMaxScaler()


def scale_data (train_data: pd.DataFrame, test_data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
    global scaler
    train_scaled: np.ndarray = scaler.fit_transform(train_data)
    test_scaled: np.ndarray = scaler.transform(test_data)
    return train_scaled, test_scaled


def prepare_data (stock_name: str, interval: str = "1h") -> Tuple[np.ndarray, np.ndarray]:
    try:
        match interval:
            case "1h":
                data = yf.download(stock_name, period="2y", interval=interval)
            case "5m":
                data = yf.download(stock_name, period="1mo", interval=interval)
            case _:
                raise ValueError(f"Invalid interval {interval}")
        
        data.index = pd.to_datetime(data.index)
        data.dropna(inplace=True)
        train_data, test_data = train_test_split(data[["Adj Close"]],
                                                 test_size=0.2,
                                                 shuffle=False,
                                                 random_state=SEED)
        
        train_data_sc, test_data_sc = scale_data(train_data[["Adj Close"]], test_data[["Adj Close"]])
        
        return train_data_sc, test_data_sc
    
    except Exception as e:
        raise RuntimeError(f"Error preparing data: {e}")


def create_sequences (datas: np.ndarray, seq_length: int = 20) -> Tuple[np.ndarray, np.ndarray]:
    x: List = []
    y: List = []
    for i in range(len(datas) - seq_length):
        x.append(datas[i:i + seq_length])
        y.append(datas[i + seq_length])
    return np.array(x), np.array(y)


def __add_price_increase_flag (data: pd.DataFrame) -> pd.DataFrame:
    data["is_price_increased"] = data["Adj Close"].diff() > 0
    return data


def __calculate_adj_close_difference (data: pd.DataFrame) -> pd.DataFrame:
    data["adj_close_diff"] = data["Adj Close"].diff().fillna(0)
    return data


def __calculate_adj_close_percentage_change (data: pd.DataFrame) -> pd.DataFrame:
    data["adj_close_pct_change"] = data["Adj Close"].pct_change().fillna(0)
    return data


def pipe (data: pd.DataFrame) -> pd.DataFrame:
    functions: List[Callable] = [__add_price_increase_flag,
                                 __calculate_adj_close_difference,
                                 __calculate_adj_close_percentage_change
                                 ]
    
    for function in functions:
        data = data.pipe(function)
    return data

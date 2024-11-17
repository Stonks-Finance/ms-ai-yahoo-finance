from fastapi import APIRouter, Query
from typing import List, Dict, Optional
from datetime import timedelta
import yfinance as yf
import pandas as pd
import numpy as np
import keras
import os
from src.get_data import scaler, create_sequences
from cachetools import TTLCache
from src.Enums.MaxDurationLimit import MaxDurationLimit
from src.Enums.DefaultDurations import DefaultDurations
from src.Classes.APIRaisedError import APIRaisedError
from src.Classes.APIResponseModel import PredictResponse


router = APIRouter()
cache = TTLCache(maxsize=100, ttl=600)


def fetch_stock_data(stock_name: str, period: str, interval: str) -> pd.DataFrame:
    """
    Fetch stock data from Yahoo Finance, and cache it for repeated requests.

    Args:
        stock_name (str): The ticker symbol of the stock.
        period (str): The period for which to fetch stock data (e.g. '1d', '2y').
        interval (str): The time interval between data points (e.g. '1h').

    Returns:
        pd.DataFrame: A dataframe containing the stock's adjusted close prices.

    Raises:
        APIRaisedError: If no data is found for the specified stock.
    """
    key = f"{stock_name}_{period}_{interval}"
    if key in cache:
        return cache[key]

    df = yf.download(stock_name, period=period, interval=interval)
    if df.empty:
        raise APIRaisedError(404, "No data found for the specified stock.")

    df.index = pd.to_datetime(df.index)
    df = df[["Adj Close"]].dropna()
    cache[key] = df  # Store in cache
    return df

def predict_data(stock_name: str, interval: str, duration: Optional[str]) -> Dict[str, List]:
    """
    Generate stock price predictions using a pre-trained LSTM model.

    Args:
        stock_name (str): The ticker symbol of the stock.
        interval (str): The time interval between data points (e.g. '5m', 1h').
        duration (Optional[str]): The number of time points to predict. If None, the default duration for the interval is used.

    Returns:
        Dict[str, List]: A dictionary containing predicted prices and their corresponding timestamps.

    Raises:
        APIRaisedError: If the input interval is unsupported or the duration is invalid.
    """
    if interval == "1h":
        max_duration = MaxDurationLimit.ONE_HOUR.get_limit("PREDICT")
        default_duration = DefaultDurations.ONE_HOUR.get_duration("PREDICT")
        period = "2y"
    else:
        raise APIRaisedError(400, f"Unsupported interval '{interval}'.")

    if duration is None:
        duration = default_duration
    else:
        try:
            duration = int(duration)
        except ValueError:
            raise APIRaisedError(422, "Duration should be an integer.")

    if duration > max_duration or duration < 1:
        raise APIRaisedError(400, f"Duration must be between 1 and {max_duration} for interval '{interval}'.")

    df = fetch_stock_data(stock_name, period, interval)

    scaled_data = scaler.fit_transform(df)
    x_seq, _ = create_sequences(scaled_data)
    last_seq = x_seq[-1].reshape(1, x_seq.shape[1], x_seq.shape[2])

    model_path = os.path.join("models", stock_name, f"{interval}_{stock_name}_best_model.keras")
    if not os.path.exists(model_path):
        raise APIRaisedError(404, "Model file not found for specified stock.")

    try:
        model = keras.models.load_model(model_path)
    except Exception as e:
        raise APIRaisedError(500, f"Error loading model: {str(e)}")

    predictions = []
    timestamps = []

    last_timestamp = pd.to_datetime(df.index[-1])

    for i in range(duration):
        pred = model.predict(last_seq)
        last_seq = np.append(last_seq[:, 1:, :], np.expand_dims(pred, axis=1), axis=1)
        predictions.append(pred[0, 0])

        next_timestamp = last_timestamp + timedelta(hours=(i + 1))

        timestamps.append(next_timestamp.isoformat())

    predictions_rescaled = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
    return {"prices": predictions_rescaled.tolist(), "timestamps": timestamps}


@router.post("/predict", response_model=PredictResponse)
async def predict(
    stock_name: str,
    interval: str = Query("1h", enum=["1h"]),
    duration: Optional[str] = Query(None)
):
    """
    API endpoint to predict future stock prices based on historical data.

    Args:
        stock_name (str): The ticker symbol of the stock.
        interval (str): The time interval between data points (e.g. '1h').
        duration (Optional[str]): The number of time points to predict.

    Returns:
        PredictResponse: A response model containing the prediction results.
    """
    try:
        prediction_data = predict_data(stock_name, interval, duration)
        return PredictResponse(
            success=True,
            status=200,
            message="Predictions made successfully.",
            data=prediction_data
        )
    except APIRaisedError as e:
        return PredictResponse(
            success=False,
            status=e.status,
            message=e.message,
            data=None
        )
    except Exception as e:
        return PredictResponse(
            success=False,
            status=500,
            message="Internal server error: " + str(e),
            data=None
        )

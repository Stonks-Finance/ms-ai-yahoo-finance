import os
from datetime import timedelta
from typing import List, Dict, Optional

import numpy as np
import pandas as pd
import keras
import yfinance as yf
from cachetools import TTLCache
from fastapi import APIRouter, Query

from src.get_data import scaler, create_sequences
from src.Enums.MaxDurationLimit import MaxDurationLimit
from src.Enums.DefaultDurations import DefaultDurations
from src.Classes.APIRaisedError import APIRaisedError
from src.Classes.APIResponseModel import PredictResponse

"""
This module defines the `/predict` endpoint for forecasting future stock prices
using a pre-trained LSTM model. It also includes utility functions to fetch
and cache stock data, and run the actual prediction logic.
"""

router = APIRouter()
cache = TTLCache(maxsize=100, ttl=600)


def fetch_stock_data(stock_name: str, period: str, interval: str) -> pd.DataFrame:
    """
    Fetch stock data from Yahoo Finance and cache it for repeated requests.

    Args:
        stock_name (str): The ticker symbol of the stock (e.g. 'AAPL').
        period (str): The period for which to fetch data (e.g., '2y' for 2 years).
        interval (str): The time interval between data points (e.g. '1h').

    Returns:
        pd.DataFrame: A DataFrame containing the 'Close' prices indexed by date/time.

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
    df = df[["Close"]].dropna()

    # Cache the result to avoid repeated downloads
    cache[key] = df
    return df


def predict_data(stock_name: str, interval: str, duration: Optional[str]) -> Dict[str, List]:
    """
    Generate future stock price predictions using a pre-trained LSTM model.

    This function handles:
    1. Validating input parameters and retrieving the correct period for data.
    2. Fetching and caching historical data from Yahoo Finance.
    3. Scaling the data and creating input sequences for the model.
    4. Loading the saved model and performing iterative predictions.
    5. Inversely transforming predictions back to actual price units.

    Args:
        stock_name (str): The ticker symbol of the stock.
        interval (str): The time interval for the data (only '1h' is supported here).
        duration (Optional[str]): Number of future time points to predict. If None, uses a default.

    Returns:
        Dict[str, List]:
            A dictionary with:
            - "prices": The predicted closing prices (list of floats).
            - "timestamps": The corresponding future timestamps (list of ISO-format strings).

    Raises:
        APIRaisedError: If the input interval is unsupported, duration is invalid,
            or if the model file is missing or can't be loaded.
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
        raise APIRaisedError(
            400,
            f"Duration must be between 1 and {max_duration} for interval '{interval}'."
        )

    # Fetch and scale the data
    df = fetch_stock_data(stock_name, period, interval)
    scaled_data = scaler.fit_transform(df)

    # Prepare the last sequence for iterative prediction
    x_seq, _ = create_sequences(scaled_data)
    last_seq = x_seq[-1].reshape(1, x_seq.shape[1], x_seq.shape[2])

    # Load the LSTM model
    model_path = os.path.join("models", stock_name, f"{interval}_{stock_name}_best_model.keras")
    if not os.path.exists(model_path):
        raise APIRaisedError(404, "Model file not found for specified stock.")

    try:
        model = keras.models.load_model(model_path)
    except Exception as e:
        raise APIRaisedError(500, f"Error loading model: {str(e)}")

    # Iteratively predict future points
    predictions = []
    timestamps = []
    last_timestamp = pd.to_datetime(df.index[-1])

    for i in range(duration):
        pred = model.predict(last_seq)
        last_seq = np.append(
            last_seq[:, 1:, :],
            np.expand_dims(pred, axis=1),
            axis=1
        )
        predictions.append(pred[0, 0])

        # Generate future timestamps (1 hour increments)
        next_timestamp = last_timestamp + timedelta(hours=(i + 1))
        timestamps.append(next_timestamp.isoformat())

    # Inverse transform the predicted values to original scale
    predictions_rescaled = scaler.inverse_transform(
        np.array(predictions).reshape(-1, 1)
    ).flatten()

    return {"prices": predictions_rescaled.tolist(), "timestamps": timestamps}


@router.post("/predict", response_model=PredictResponse)
async def predict(
    stock_name: str,
    interval: str = Query("1h", enum=["1h"]),
    duration: Optional[str] = Query(None)
) -> PredictResponse:
    """
    Predict future stock prices based on historical data using a pre-trained LSTM model.

    Args:
        stock_name (str): The ticker symbol of the stock (e.g., 'AAPL').
        interval (str, optional): Interval for the historical data. Defaults to "1h".
        duration (Optional[str], optional): Number of future time points to forecast. If None,
            uses a default duration for the given interval.

    Returns:
        PredictResponse: A structured response containing:
            - success (bool): Whether the operation was successful.
            - status (int): HTTP-like status code.
            - message (str): A message describing the result.
            - data (Optional[Dict[str, Any]]): The prediction results (prices & timestamps).

    Raises:
        APIRaisedError: If the request parameters are invalid or the model file is not found.
        Exception: For any other unexpected errors during the prediction process.
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
            message=f"Internal server error: {e}",
            data=None
        )

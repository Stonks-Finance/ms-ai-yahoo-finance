from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Dict
from datetime import timedelta
import yfinance as yf
import pandas as pd
import numpy as np
import keras
import os
from src.get_data import scaler, create_sequences

router = APIRouter()

class PredictResponse(BaseModel):
    success: bool
    status: int
    message: str
    data: Dict[str, List]

class PredictionError(Exception):
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message

def predict_data(stock_name: str, interval: str, duration: int) -> Dict[str, List]:

    prediction_limits = {"1m": 30, "1h": 10}
    if interval in prediction_limits and (duration > prediction_limits[interval] or duration < 1):
        raise PredictionError(400, f"Duration must be between 1 and {prediction_limits[interval]} for interval '{interval}'.")

    period = "max" if interval == "1m" else "2y" if interval == "1h" else None
    if period is None:
        raise PredictionError(400, f"Unsupported interval '{interval}'.")

    df = yf.download(stock_name, period=period, interval=interval)
    if df.empty:
        raise PredictionError(404, "No data found for the specified stock.")

    df.index = pd.to_datetime(df.index)
    df = df[["Adj Close"]].dropna()

    scaled_data = scaler.fit_transform(df)
    x_seq, _ = create_sequences(scaled_data)
    last_seq = x_seq[-1].reshape(1, x_seq.shape[1], x_seq.shape[2])

    model_path = f"./models/{stock_name}/{interval}_{stock_name}_best_model.keras"
    print(f"Checking model path: {model_path}")
    if not os.path.exists(model_path):
        raise PredictionError(404, "Model file not found for specified stock.")

    try:
        model = keras.models.load_model(model_path)
    except Exception as e:
        raise PredictionError(500, f"Error loading model: {str(e)}")

    predictions = []
    timestamps = []
    for i in range(duration):
        pred = model.predict(last_seq)
        last_seq = np.append(last_seq[:, 1:, :], np.expand_dims(pred, axis=1), axis=1)
        predictions.append(pred[0, 0])

        if interval == "1m":
            next_timestamp = df.index[-1] + timedelta(minutes=(i + 1))
        elif interval == "1h":
            next_timestamp = df.index[-1] + timedelta(hours=(i + 1))

        timestamps.append(next_timestamp.isoformat())

    predictions_rescaled = scaler.inverse_transform(np.array(predictions).reshape(-1, 1)).flatten()
    return {"prices": predictions_rescaled.tolist(), "timestamps": timestamps}

@router.get("/predict", response_model=PredictResponse)
async def predict(
    stock_name: str,
    interval: str = Query("1h", enum=["1m", "1h"]),
    duration: int = 5
):
    try:
        prediction_data = predict_data(stock_name, interval, duration)
        return PredictResponse(
            success=True,
            status=200,
            message="Predictions made successfully.",
            data=prediction_data
        )
    except PredictionError as e:
        return PredictResponse(
            success=False,
            status=e.status,
            message=e.message,
            data={"prices": [], "timestamps": []}
        )
    except Exception as e:
        return PredictResponse(
            success=False,
            status=500,
            message="Internal server error: " + str(e),
            data={"prices": [], "timestamps": []}
        )
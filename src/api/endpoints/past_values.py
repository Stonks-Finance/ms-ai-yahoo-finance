from typing import List, Dict, Optional

import yfinance as yf
from fastapi import APIRouter, Query

from src.Enums.MaxDurationLimit import MaxDurationLimit
from src.Enums.DefaultDurations import DefaultDurations
from src.Classes.APIRaisedError import APIRaisedError
from src.Classes.APIResponseModel import PastValuesResponse

"""
This module defines an endpoint (`/past-values`) to retrieve historical stock values
(timestamps and closing prices) for a specified stock symbol and interval. 
It uses Yahoo Finance data (via yfinance) and includes parameter validation logic.
"""

router = APIRouter()


def fetch_past_stock_data(stock_name: str, interval: str, duration: str) -> Dict[str, List]:
    """
    Fetch past adjusted closing prices and timestamps for a given stock.

    Args:
        stock_name (str): The ticker symbol (e.g., 'AAPL').
        interval (str): Time interval for the data points (currently only '1h' is supported).
        duration (str): Number of data points to retrieve. If None, a default duration is used.

    Returns:
        Dict[str, List]: A dictionary with two keys:
            - "prices": List of float closing prices.
            - "timestamps": List of string timestamps in ISO format.

    Raises:
        APIRaisedError: If the interval is unsupported, duration is invalid, or no data is found.
    """
    if interval == "1h":
        max_duration = MaxDurationLimit.ONE_HOUR.get_limit("PAST_VALUES")
        default_duration = DefaultDurations.ONE_HOUR.get_duration("PAST_VALUES")
        period = "1mo"
    else:
        raise APIRaisedError(400, f"Unsupported interval '{interval}'.")

    if duration is None:
        duration = default_duration
    else:
        try:
            duration = int(duration)
        except ValueError:
            raise APIRaisedError(400, "Duration should be an integer.")

    if duration > max_duration or duration < 1:
        raise APIRaisedError(
            400,
            f"Duration for interval '{interval}' cannot exceed {max_duration}."
        )

    stock_data = yf.download(stock_name, period=period, interval=interval)
    stock_data = stock_data.iloc[-duration:]

    if stock_data.empty:
        raise APIRaisedError(422, f"No data found for stock '{stock_name}'.")

    prices = stock_data["Close"].values.flatten().tolist()
    timestamps = [date.strftime("%Y-%m-%dT%H:%M:%S") for date in stock_data.index]

    return {"prices": prices, "timestamps": timestamps}


@router.get("/past-values", response_model=PastValuesResponse)
async def past_values(
    stock_name: str,
    interval: str = Query("1h", enum=["1h"]),
    duration: Optional[str] = Query(None)
) -> PastValuesResponse:
    """
    Retrieve a specified number of past stock values for the given stock symbol.

    This endpoint fetches the last `duration` data points based on the selected `interval`
    (currently only '1h' is supported). If no duration is provided, the default duration
    for the given interval is used.

    Args:
        stock_name (str): The ticker symbol of the stock.
        interval (str, optional): The time interval for data points. Defaults to "1h".
        duration (Optional[str], optional): Number of data points to retrieve. If None, use defaults.

    Returns:
        PastValuesResponse: A Pydantic response model containing:
            - success (bool): Whether the operation was successful.
            - status (int): HTTP-like status code.
            - message (str): Description of the result.
            - data (Optional[Dict[str, List]]): Dictionary with 'prices' and 'timestamps', or None if there's an error.

    Raises:
        APIRaisedError: If parameters are invalid or data retrieval fails.
        Exception: For any other internal errors.
    """
    try:
        past_data = fetch_past_stock_data(stock_name, interval, duration)
        return PastValuesResponse(
            success=True,
            status=200,
            message="Past values retrieved successfully.",
            data=past_data
        )
    except APIRaisedError as e:
        return PastValuesResponse(
            success=False,
            status=e.status,
            message=e.message,
            data=None
        )
    except Exception as e:
        return PastValuesResponse(
            success=False,
            status=500,
            message=f"Internal server error: {e}",
            data=None
        )

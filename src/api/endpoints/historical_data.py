import yfinance as yf
from fastapi import APIRouter, Query
from typing import List, Dict, Optional

from src.Classes.APIRaisedError import APIRaisedError
from src.Classes.APIResponseModel import HistoricalDataResponse
from src.Enums.MaxDurationLimit import MaxDurationLimit
from src.Enums.DefaultDurations import DefaultDurations

"""
This module provides an endpoint (`/historical-data`) and a supporting function to fetch and return
historical stock data for a given stock symbol, time interval, and duration in days.
"""

router = APIRouter()


def get_historical_data(stock_name: str, interval: str, duration: str) -> List[Dict[str, float]]:
    """
    Fetch historical data for a specified stock symbol, interval, and duration.

    Depending on the chosen interval ('1h', '1d', or '1mo'), the function determines:
    - A maximum allowed duration in days (from MaxDurationLimit).
    - A default duration if none is provided (from DefaultDurations).
    - A corresponding period to request from yfinance (e.g., '3mo', '5y', 'max').

    It then downloads the stock data via yfinance, slices the last `duration` entries,
    and constructs a list of dictionaries with time and price details.

    Args:
        stock_name (str): The ticker symbol of the stock.
        interval (str): The time interval for the data (e.g., '1h', '1d', '1mo').
        duration (str): The duration in days for which to fetch the data.

    Returns:
        List[Dict[str, float]]: A list of dictionaries containing timestamps and OHLC data.

    Raises:
        APIRaisedError: If the interval is unsupported, duration is invalid,
                        or no data is found for the requested stock.
    """
    match interval:
        case "1h":
            max_duration = MaxDurationLimit.ONE_HOUR.get_limit("HISTORICAL_DATA")
            default_duration = DefaultDurations.ONE_HOUR.get_duration("HISTORICAL_DATA")
            period = "3mo"
        case "1d":
            max_duration = MaxDurationLimit.ONE_DAY.get_limit("HISTORICAL_DATA")
            default_duration = DefaultDurations.ONE_DAY.get_duration("HISTORICAL_DATA")
            period = "5y"
        case "1mo":
            max_duration = MaxDurationLimit.ONE_MONTH.get_limit("HISTORICAL_DATA")
            default_duration = DefaultDurations.ONE_MONTH.get_duration("HISTORICAL_DATA")
            period = "max"
        case _:
            raise APIRaisedError(400, f"Unsupported interval '{interval}'.")

    if duration is None:
        duration = default_duration
    else:
        try:
            duration = int(duration)
        except ValueError:
            raise APIRaisedError(400, "Duration should be an integer.")

    if duration > max_duration or duration < 1:
        raise APIRaisedError(400, f"Duration for interval '{interval}' cannot exceed {max_duration}.")

    stock_data = yf.download(stock_name, period=period, interval=interval)
    stock_data = stock_data.iloc[-duration:]

    if stock_data.empty:
        raise APIRaisedError(422, f"No data found for stock '{stock_name}'.")

    past_data = []
    for date, row in stock_data.iterrows():
        past_data.append({
            "timestamp": date.strftime("%Y-%m-%dT%H:%M:%S"),
            "open": float(row['Open'].iloc[0]),
            "high": float(row['High'].iloc[0]),
            "low": float(row['Low'].iloc[0]),
            "close": float(row['Close'].iloc[0]),
        })

    return past_data


@router.get("/historical-data", response_model=HistoricalDataResponse)
async def historical_data(
    stock_name: str,
    interval: str = Query("1d", enum=["1h", "1d", "1mo"]),
    duration: Optional[str] = Query(None)
):
    """
    Retrieve historical stock data for a given stock symbol.

    The data can be fetched in intervals of 1 hour ('1h'), 1 day ('1d'), or 1 month ('1mo'), 
    each with its own maximum duration limit. If `duration` is not provided, a default 
    duration for that interval is used.

    Args:
        stock_name (str): The ticker symbol of the stock.
        interval (str, optional): The data interval. Defaults to '1d'.
        duration (Optional[str], optional): The number of days of data to retrieve. 
                                            Defaults to None, which uses a default duration.

    Returns:
        HistoricalDataResponse: A pydantic model wrapping the success status, message, 
        and the list of historical OHLC data.

    Raises:
        APIRaisedError: If the interval is unsupported, or data retrieval is invalid or empty.
        Exception: For any unexpected errors during the process.
    """
    try:
        past_data = get_historical_data(stock_name, interval, duration)
        return HistoricalDataResponse(
            success=True,
            status=200,
            message="Historical data retrieved successfully.",
            data=past_data
        )
    except APIRaisedError as e:
        return HistoricalDataResponse(
            success=False,
            status=e.status,
            message=e.message,
            data=None
        )
    except Exception as e:
        return {
            "success": False,
            "status": 500,
            "message": "Internal server error: " + str(e),
            "data": None
        }

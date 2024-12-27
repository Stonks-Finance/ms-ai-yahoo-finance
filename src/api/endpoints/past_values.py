from fastapi import APIRouter, Query
from typing import List, Dict, Optional
import yfinance as yf
from src.Enums.MaxDurationLimit import MaxDurationLimit
from src.Enums.DefaultDurations import DefaultDurations
from src.Classes.APIRaisedError import APIRaisedError
from src.Classes.APIResponseModel import PastValuesResponse


router = APIRouter()


def fetch_past_stock_data (stock_name: str, interval: str, duration: str) -> Dict[str, List]:
    """
    Fetch past stock data from Yahoo Finance for a given stock and interval, and return the adjusted closing prices.

    Args:
        stock_name (str): The ticker symbol of the stock.
        interval (str): The time interval between data points (e.g. '1h').
        duration (str): The number of time points to retrieve.

    Returns:
        Dict[str, List]: A dictionary containing lists of past stock prices and their corresponding timestamps.

    Raises:
        APIRaisedError: If the interval is unsupported, the duration is invalid, or no data is found for the stock.
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
        raise APIRaisedError(400, f"Duration for interval '{interval}' cannot exceed {max_duration}.")

    stock_data = yf.download(stock_name, period=period, interval=interval)

    stock_data = stock_data.iloc[-duration:]
    
    if stock_data.empty:
        raise APIRaisedError(422, f"No data found for stock '{stock_name}'.")
    
    prices = stock_data["Close"].values.flatten().tolist()
    timestamps = [date.strftime("%Y-%m-%dT%H:%M:%S") for date in stock_data.index]
    
    return {"prices": prices, "timestamps": timestamps}


@router.get("/past-values", response_model=PastValuesResponse)
async def past_values (
        stock_name: str,
        interval: str = Query("1h", enum=["1h"]),
        duration: Optional[str] = Query(None)
):
    """
    API endpoint to retrieve past stock values for a given stock and interval.

    Args:
        stock_name (str): The ticker symbol of the stock.
        interval (str): The time interval between data points (e.g. '1h').
        duration (Optional[str]): The number of past time points to retrieve (default is based on the interval).

    Returns:
        PastValuesResponse: A response model containing the past stock data with adjusted closing prices and timestamps.
    
    Raises:
        APIRaisedError: If the request has any invalid parameters or if fetching the stock data fails.
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
            message="Internal server error: " + str(e),
            data=None
        )

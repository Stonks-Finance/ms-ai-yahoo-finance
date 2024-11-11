from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
import yfinance as yf
from src.Enums.MaxDurationLimit import MaxDurationLimit
from src.Enums.DefaultDurations import DefaultDurations

router = APIRouter()


class PastValuesResponse(BaseModel):
    success: bool
    status: int
    message: str
    data: Dict[str, List]


def fetch_past_stock_data (stock_name: str, interval: str, duration: int) -> Dict[str, List]:
    period:str=""
    if interval == "1m":
        period = "1d"
    elif interval == "1h":
        period = "1mo"

    stock_data = yf.download(stock_name, period=period, interval=interval)

    stock_data = stock_data.iloc[-duration:]
    
    if stock_data.empty:
        raise ValueError(f"No data found for stock '{stock_name}'.")
    
    prices = stock_data["Adj Close"].values.flatten().tolist()
    timestamps = [date.strftime("%Y-%m-%dT%H:%M:%S") for date in stock_data.index]
    
    return {"prices": prices, "timestamps": timestamps}


@router.get("/past-values", response_model=PastValuesResponse)
async def past_values (
        stock_name: str,
        interval: str = Query("1h", enum=["1m", "1h"]),
        duration: Optional[str] = Query(None)
):
    default_duration=0
    max_duration=0
    if interval == "1m":
        max_duration = MaxDurationLimit.ONE_MINUTE.get_limit("PAST_VALUES")
        default_duration = DefaultDurations.ONE_MINUTE.get_duration("PAST_VALUES")
    elif interval == "1h":
        max_duration = MaxDurationLimit.ONE_HOUR.get_limit("PAST_VALUES")
        default_duration = DefaultDurations.ONE_HOUR.get_duration("PAST_VALUES")

    if duration is None:
        duration = default_duration
    else:
        try:
            duration = int(duration)
        except ValueError:
            return {
                "success": False,
                "status": 422,
                "message": "Duration should be an integer.",
                "data": {"prices": [], "timestamps": []}
            }

    if duration > max_duration or duration < 1:
        return {
            "success": False,
            "status": 400,
            "message": f"Duration for interval '{interval}' cannot exceed {max_duration}.",
            "data": {"prices": [], "timestamps": []}
        }
    
    try:
        past_data = fetch_past_stock_data(stock_name, interval, duration)
        return {
            "success": True,
            "status": 200,
            "message": "Past values retrieved successfully.",
            "data": past_data
        }
    except ValueError as e:
        return {
            "success": False,
            "status": 400,
            "message": str(e),
            "data": {"prices": [], "timestamps": []}
        }
    except Exception as e:
        return {
            "success": False,
            "status": 500,
            "message": "Internal server error: " + str(e),
            "data": {"prices": [], "timestamps": []}
        }

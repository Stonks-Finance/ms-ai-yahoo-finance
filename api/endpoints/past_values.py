import datetime
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Dict
import yfinance as yf
from dateutil.relativedelta import relativedelta
from api.Enums.Duration import MaxDurationLimit

router = APIRouter()


class PastValuesResponse(BaseModel):
    success: bool
    status: int
    message: str
    data: Dict[str, List]


def fetch_past_stock_data (stock_name: str, interval: str, duration: int) -> Dict[str, List]:
    end_date = datetime.datetime.now()
    start_date = None
    
    if interval == "1d":
        start_date = end_date - datetime.timedelta(days=duration)
    elif interval == "1mo":
        start_date = end_date - relativedelta(months=duration - 1)
    
    stock_data = yf.download(stock_name, start=start_date, end=end_date, interval=interval)
    
    if stock_data.empty:
        raise ValueError(f"No data found for stock '{stock_name}'.")
    
    prices = stock_data["Adj Close"].values.flatten().tolist()
    timestamps = [date.strftime("%Y-%m-%dT%H:%M:%S") for date in stock_data.index]
    
    return {"prices": prices, "timestamps": timestamps}


@router.get("/past-values", response_model=PastValuesResponse)
async def past_values (
        stock_name: str,
        interval: str = Query("1d", enum=[d.interval for d in MaxDurationLimit]),
        duration: int = Query(7)
):
    max_duration = next((d.limit for d in MaxDurationLimit if d.interval == interval), float('inf'))
    if duration > max_duration:
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

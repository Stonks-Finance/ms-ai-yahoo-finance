import datetime
from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Dict
import yfinance as yf
from dateutil.relativedelta import relativedelta

router = APIRouter()

class PastValuesResponse(BaseModel):
    success: bool
    status: int
    message: str
    data: Dict[str, List]

MAX_DURATION_LIMIT = {
    "1d": 1500,
    "1mo": 120
}

def fetch_past_stock_data(stock_name: str, interval: str, duration: int) -> Dict[str, List]:
    end_date = datetime.datetime.now()

    if interval == "1d":
        start_date = end_date - datetime.timedelta(days=duration)
    elif interval == "1mo":
        start_date = end_date - relativedelta(months=duration - 1)

    stock_data = yf.download(stock_name, start=start_date, end=end_date, interval=interval)

    if stock_data.empty:
        raise ValueError(f"No data found for stock '{stock_name}'.")

    prices = stock_data['Adj Close'].values.flatten().tolist()
    timestamps = [date.strftime("%Y-%m-%dT%H:%M:%S") for date in stock_data.index]

    return {"prices": prices, "timestamps": timestamps}

@router.get("/past-values", response_model=PastValuesResponse)
async def past_values(stock_name: str, interval: str = Query("1d", enum=["1d", "1mo"]), duration: int = Query(7)):

    if duration > MAX_DURATION_LIMIT.get(interval, float('inf')):
        return {
            "success": False,
            "status": 400,
            "message": f"Duration for interval '{interval}' cannot exceed {MAX_DURATION_LIMIT[interval]}.",
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


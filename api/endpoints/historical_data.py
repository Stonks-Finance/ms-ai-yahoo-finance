from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
import datetime
import yfinance as yf
from dateutil.relativedelta import relativedelta

router = APIRouter()

class StockData(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float

class HistoricalDataResponse(BaseModel):
    success: bool
    status: int
    message: str
    data: List[StockData]

DEFAULT_DURATIONS = {
    "1d": 7,
    "1mo": 12
}

MAX_DURATION_LIMIT = {
    "1d": 1500,
    "1mo": 120
}

def get_stock_debut_date(stock_name: str) -> Optional[datetime.datetime]:
    stock_info = yf.Ticker(stock_name).info
    debut_date = stock_info.get('firstTradeDate')
    return debut_date if debut_date else None

def get_historical_data(stock_name: str, interval: str, duration: int) -> List[Dict[str, float]]:
    end_date = datetime.datetime.now()

    if interval == "1d":
        start_date = end_date - datetime.timedelta(days=duration)
    elif interval == "1mo":
        start_date = end_date - relativedelta(months=duration - 1)

    stock_data = yf.download(stock_name, start=start_date, end=end_date, interval=interval)

    if stock_data.empty:
        debut_date = get_stock_debut_date(stock_name)
        if debut_date:
            start_date = debut_date
            stock_data = yf.download(stock_name, start=start_date, end=end_date, interval=interval)

    if stock_data.empty:
        raise ValueError(f"No data found for stock '{stock_name}'.")

    past_data = []
    for date, row in stock_data.iterrows():
        past_data.append({
            "time": date.strftime("%Y-%m-%d"),
            "open": float(row['Open']),
            "high": float(row['High']),
            "low": float(row['Low']),
            "close": float(row['Close']),
        })

    return past_data

@router.get("/historical-data", response_model=HistoricalDataResponse)
async def past_values(
    stock_name: str,
    interval: str = Query("1d", enum=["1d", "1mo"]),
    duration: int = Query(DEFAULT_DURATIONS["1d"])
):
    if duration > MAX_DURATION_LIMIT.get(interval, float('inf')):
        return {
            "success": False,
            "status": 400,
            "message": f"Duration for interval '{interval}' cannot exceed {MAX_DURATION_LIMIT[interval]}.",
            "data": []
        }

    try:
        past_data = get_historical_data(stock_name, interval, duration)
        return {
            "success": True,
            "status": 200,
            "message": "Historical data retrieved successfully.",
            "data": past_data
        }
    except ValueError as e:
        return {
            "success": False,
            "status": 400,
            "message": str(e),
            "data": []
        }
    except Exception as e:
        return {
            "success": False,
            "status": 500,
            "message": "Internal server error: " + str(e),
            "data": []
        }

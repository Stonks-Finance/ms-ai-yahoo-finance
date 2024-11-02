from fastapi import APIRouter, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
import datetime
import yfinance as yf
from dateutil.relativedelta import relativedelta
from src.Enums.MaxDurationLimit import MaxDurationLimit
from src.Enums.DefaultDurations import DefaultDurations


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



def get_stock_debut_date (stock_name: str) -> Optional[datetime.datetime]:
    stock_info = yf.Ticker(stock_name).info
    debut_date = stock_info.get("firstTradeDate")
    return datetime.datetime.fromtimestamp(debut_date) if debut_date else None


def get_historical_data (stock_name: str, interval: str, duration: int) -> List[Dict[str, float]]:

    end_date = datetime.datetime.now(tz=datetime.timezone.utc)
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
    duration: Optional[str] = Query(None)
):
    if interval == "1d":
        max_duration = MaxDurationLimit.ONE_DAY.get_limit("HISTORICAL_DATA")
        default_duration = DefaultDurations.ONE_DAY.get_duration("HISTORICAL_DATA")
    elif interval == "1mo":
        max_duration = MaxDurationLimit.ONE_MONTH.get_limit("HISTORICAL_DATA")
        default_duration = DefaultDurations.ONE_MONTH.get_duration("HISTORICAL_DATA")

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
                "data": []
            }

    if duration > max_duration or duration < 1:
        return {
            "success": False,
            "status": 400,
            "message": f"Duration for interval '{interval}' cannot exceed {max_duration}.",
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

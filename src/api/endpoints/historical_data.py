from fastapi import APIRouter, Query
from typing import List, Dict, Optional
import datetime
import yfinance as yf
from dateutil.relativedelta import relativedelta
from src.Enums.MaxDurationLimit import MaxDurationLimit
from src.Enums.DefaultDurations import DefaultDurations
from src.Classes.APIRaisedError import APIRaisedError
from src.Classes.APIResponseModel import HistoricalDataResponse


router = APIRouter()


def get_stock_debut_date (stock_name: str) -> Optional[datetime.datetime]:
    stock_info = yf.Ticker(stock_name).info
    debut_date = stock_info.get("firstTradeDate")
    return datetime.datetime.fromtimestamp(debut_date) if debut_date else None


def get_historical_data (stock_name: str, interval: str, duration: str) -> List[Dict[str, float]]:

    if interval == "1d":
        max_duration = MaxDurationLimit.ONE_DAY.get_limit("HISTORICAL_DATA")
        default_duration = DefaultDurations.ONE_DAY.get_duration("HISTORICAL_DATA")
        delta_fn = lambda d: datetime.timedelta(days=d)
    elif interval == "1mo":
        max_duration = MaxDurationLimit.ONE_MONTH.get_limit("HISTORICAL_DATA")
        default_duration = DefaultDurations.ONE_MONTH.get_duration("HISTORICAL_DATA")
        delta_fn = lambda d: relativedelta(month=d-1)
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
    
    end_date = datetime.datetime.now(tz=datetime.timezone.utc)
    start_date = end_date - delta_fn(duration)
    
    stock_data = yf.download(stock_name, start=start_date, end=end_date, interval=interval)
    
    if stock_data.empty:
        debut_date = get_stock_debut_date(stock_name)
        if debut_date:
            start_date = debut_date
            stock_data = yf.download(stock_name, start=start_date, end=end_date, interval=interval)
    
    if stock_data.empty:
        raise APIRaisedError(422, f"No data found for stock '{stock_name}'.")
    
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
async def historical_data(
    stock_name: str,
    interval: str = Query("1d", enum=["1d", "1mo"]),
    duration: Optional[str] = Query(None)
):
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
            data=[]
        )
    except Exception as e:
        return {
            "success": False,
            "status": 500,
            "message": "Internal server error: " + str(e),
            "data": []
        }

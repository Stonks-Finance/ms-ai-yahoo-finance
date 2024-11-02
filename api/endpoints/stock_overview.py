from fastapi import APIRouter
from pydantic import BaseModel
from typing import List, Dict
import yfinance as yf
import os

router = APIRouter()


class StockOverviewResponse(BaseModel):
    success: bool
    status: int
    message: str
    data: List[Dict[str, str]]


@router.get("/stock-overview", response_model=StockOverviewResponse)
async def stock_overview():
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'models'))

    stock_data = []

    try:
        stock_names = [name for name in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, name))]
    except Exception as e:
        return {
            "success": False,
            "status": 500,
            "message": f"Error accessing model directories: {str(e)}",
            "data": []
        }

    for stock_name in stock_names:
        try:
            data = yf.download(stock_name, period="5d", interval="1d")
        except Exception as e:
            stock_data.append({"stock_name": stock_name, "change": "Error retrieving data"})
            continue

        if data.empty or len(data) < 2:
            stock_data.append({"stock_name": stock_name, "change": "N/A"})
            continue

        current_price = float(data["Adj Close"].iloc[-1])
        previous_price = float(data["Adj Close"].iloc[-2])

        change = (current_price - previous_price) / previous_price * 100

        stock_data.append({"stock_name": stock_name, "change": f"{change:.2f}%"})

    return {
        "success": True,
        "status": 200,
        "message": "Stock overview retrieved successfully.",
        "data": stock_data
    }
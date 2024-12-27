from fastapi import APIRouter
import yfinance as yf
import os
from src.Classes.APIResponseModel import StockOverviewResponse
from src.get_data import pipe


router = APIRouter()


@router.get("/stock-overview", response_model=StockOverviewResponse)
async def stock_overview():
    """
    API endpoint to retrieve a stock overview, including the percentage change in adjusted closing prices 
    for stocks listed in the model directory over the past 5 days.

    The function retrieves stock names from the 'models' directory, attempts to fetch the last 5 days 
    of stock data from Yahoo Finance, and calculates the percentage change between the current and previous 
    day's adjusted close price for each stock.

    Returns:
        dict: A response containing success status, message, and a list of stock names with their respective 
              percentage price change (or error message if data retrieval fails).
    """
    
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'models'))
    stock_data = []

    try:
        stock_names = [name for name in os.listdir(models_dir) if os.path.isdir(os.path.join(models_dir, name))]
    except Exception as e:
        return {
            "success": False,
            "status": 500,
            "message": f"Error accessing model directories: {str(e)}",
            "data": None
        }

    for stock_name in stock_names:
        try:
            data = yf.download(stock_name, period="5d", interval="1d")
        except ValueError:
            stock_data.append({"stock_name": stock_name, "current_price": "Error retrieving data", "change": "Error retrieving data"})
            continue

        if data.empty or len(data) < 2:
            stock_data.append({"stock_name": stock_name, "current_price": "N/A", "change": "N/A"})
            continue

        current_price = float(data['Close'].iloc[-1].item())

        processed_data = pipe(data) 
        change = processed_data["adj_close_pct_change"].iloc[-1] * 100

        stock_data.append({"stock_name": stock_name, "current_price": current_price, "change": f"{change:.2f}%"})

    return {
        "success": True,
        "status": 200,
        "message": "Stock overview retrieved successfully.",
        "data": stock_data
    }

import os

import yfinance as yf
from fastapi import APIRouter

from src.Classes.APIResponseModel import StockOverviewResponse
from src.get_data import pipe

"""
This module provides an endpoint (`/stock-overview`) that scans the 'models' directory
to identify which stocks have trained models, then fetches the last 5 days of data
for each stock to compute its recent percentage price change.
"""

router = APIRouter()


@router.get("/stock-overview", response_model=StockOverviewResponse)
async def stock_overview():
    """
    Retrieve a basic overview of stocks with trained models, including the latest price
    and the 5-day percentage change in adjusted closing price.

    Steps:
    1. Find subdirectories (stock names) under the 'models' directory.
    2. For each stock, download the last 5 days of daily data via yfinance.
    3. Compute the current price and the day-to-day percentage change.
    4. Return a list of dictionaries with stock name, current price, and 5-day change.

    Returns:
        dict: A JSON-compatible dictionary with:
            - success (bool): Whether the operation was successful.
            - status (int): HTTP-like status code (200 for success, 500 on error).
            - message (str): Description of the result.
            - data (list): A list of dictionaries for each stock, including:
                * "stock_name" (str)
                * "current_price" (float or str)
                * "change" (str, representing the percentage change or an error indicator)
    """
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'models'))
    stock_data = []

    try:
        stock_names = [
            name
            for name in os.listdir(models_dir)
            if os.path.isdir(os.path.join(models_dir, name))
        ]
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
            stock_data.append({
                "stock_name": stock_name,
                "current_price": "Error retrieving data",
                "change": "Error retrieving data"
            })
            continue

        if data.empty or len(data) < 2:
            stock_data.append({
                "stock_name": stock_name,
                "current_price": "N/A",
                "change": "N/A"
            })
            continue

        current_price = float(data['Close'].iloc[-1].item())

        processed_data = pipe(data)
        change = processed_data["adj_close_pct_change"].iloc[-1] * 100

        stock_data.append({
            "stock_name": stock_name,
            "current_price": current_price,
            "change": f"{change:.2f}%"
        })

    return {
        "success": True,
        "status": 200,
        "message": "Stock overview retrieved successfully.",
        "data": stock_data
    }

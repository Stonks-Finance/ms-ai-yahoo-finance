# __init__.py
from .predict import router as predict_router
from .stock_overview import router as stock_overview_router
from .historical_data import router as historical_data_router
from .past_values import router as past_values_router

__all__ = [
    "predict_router",
    "stock_overview_router",
    "historical_data_router",
    "past_values_router",
]
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Union, Any

from .endpoints import (
    predict,
    stock_overview,
    historical_data,
    past_values,
    create_model,
    market_state
)
from settings import IP, PORT

"""
This module sets up and runs the StonksAPI using FastAPI. It defines the main API
application, a root endpoint, and includes various routers from different endpoints.
"""

api = FastAPI()


class ResponseModel(BaseModel):
    """
    A generic response model used to structure responses returned by various API endpoints.

    Attributes:
        data (Union[Dict[str, Any], List[Any]]): The main payload of the response, which can be
            either a dictionary of key-value pairs or a list of items.
        success (bool): Indicates whether the operation was successful.
        status (int): An HTTP-like status code (e.g., 200 for success).
        message (str): A descriptive message about the operation or error.
    """
    data: Union[Dict[str, Any], List[Any]]
    success: bool
    status: int
    message: str


@api.get("/")
async def read_root():
    """
    API root endpoint that provides a welcome message.

    This endpoint serves as the landing page for the StonksAPI, offering a simple
    message to indicate that the API is operational.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Welcome to the StonksAPI!"}


# Include various endpoint routers, each handling specific routes.
api.include_router(create_model.router, tags=["Create Model"])
api.include_router(market_state.router, tags=["Market State"])
api.include_router(predict.router, tags=["Predict"])
api.include_router(stock_overview.router, tags=["Stock Overview"])
api.include_router(historical_data.router, tags=["Historical Data"])
api.include_router(past_values.router, tags=["Past Values"])


def run_api():
    """
    Run the StonksAPI using uvicorn.

    This function starts the Uvicorn server with the FastAPI application. By default,
    it uses the host and port specified in the global settings, and does not enable
    auto-reload.

    Usage:
        run_api()

    Side Effects:
        Starts a Uvicorn server to listen for incoming HTTP requests on IP:PORT.
    """
    uvicorn.run(api, host=IP, port=PORT, reload=False)

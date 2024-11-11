from fastapi import FastAPI
from .endpoints import predict, stock_overview, historical_data, past_values

api = FastAPI()

@api.get("/")
async def read_root():
    """
    Root endpoint that returns a welcome message for the StonksAPI.

    This endpoint is a simple GET request that serves as the entry point of the API, 
    providing a message indicating that the API is operational.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Welcome to the StonksAPI!"}

api.include_router(predict.router, tags=["Predict"])
api.include_router(stock_overview.router, tags=["Stock Overview"])
api.include_router(historical_data.router, tags=["Historical Data"])
api.include_router(past_values.router, tags=["Past Values"])

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Union, Any
from .endpoints import predict, stock_overview, historical_data, past_values, create_model, market_state
from settings import IP, PORT

api = FastAPI()

class ResponseModel(BaseModel):
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


api.include_router(create_model.router, tags=["Create Model"])
api.include_router(market_state.router, tags=["Market State"])
api.include_router(predict.router, tags=["Predict"])
api.include_router(stock_overview.router, tags=["Stock Overview"])
api.include_router(historical_data.router, tags=["Historical Data"])
api.include_router(past_values.router, tags=["Past Values"])


def run_api():
    uvicorn.run(api, host=IP, port=PORT, reload=False)

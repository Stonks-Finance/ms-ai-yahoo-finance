from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Union, Any
from .endpoints import predict, stock_overview, historical_data, past_values, create_model, market_state

api = FastAPI()

class ResponseModel(BaseModel):
    data: Union[Dict[str, Any], List[Any]]
    success: bool
    status: int
    message: str

@api.get("/")
async def read_root():
    return {"message": "Welcome to the StonksAPI!"}


api.include_router(create_model.router, tags=["Create Model"])
api.include_router(market_state.router, tags=["Market State"])
api.include_router(predict.router, tags=["Predict"])
api.include_router(stock_overview.router, tags=["Stock Overview"])
api.include_router(historical_data.router, tags=["Historical Data"])
api.include_router(past_values.router, tags=["Past Values"])

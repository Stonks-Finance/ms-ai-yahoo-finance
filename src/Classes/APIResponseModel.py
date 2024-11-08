from pydantic import BaseModel
from typing import List, Dict, TypeVar, Generic

DataT = TypeVar("DataT")

class APIResponseModel(BaseModel, Generic[DataT]):
    success: bool
    status: int
    message: str
    data: DataT

class StockData(BaseModel):
    time: str
    open: float
    high: float
    low: float
    close: float

class HistoricalDataResponse(APIResponseModel[List[StockData]]):
    pass

class PredictResponse(APIResponseModel[Dict[str, List]]):
    pass

class PastValuesResponse(APIResponseModel[Dict[str, List]]):
    pass

class StockOverviewResponse(APIResponseModel[List[Dict[str, str]]]):
    pass

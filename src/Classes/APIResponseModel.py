from pydantic import BaseModel
from typing import List, Dict, Optional, TypeVar, Generic

DataT = TypeVar("DataT")

class APIResponseModel(BaseModel, Generic[DataT]):
    """
    A generic model representing the structure of an API response.
    
    This model is used as a base for API responses. It includes a success flag, status code, message, 
    and optionally any data associated with the response. The type of the data is generic and can vary 
    based on the specific response model.

    Attributes:
        success (bool): Indicates whether the API request was successful.
        status (int): The HTTP status code associated with the response.
        message (str): A message describing the result of the API request.
        data (Optional[DataT]): The data returned by the API request, if any.
    """
    success: bool
    status: int
    message: str
    data: Optional[DataT] = None

class StockData(BaseModel):
    """
    Represents a single stock data point in time.
    
    This model contains the stock's price data at a specific timestamp, including the opening, closing,
    highest, and lowest prices for the given time period.

    Attributes:
        timestamp (str): The timestamp for the stock data point (e.g., '2024-11-11T14:30:00').
        open (float): The opening price of the stock at the given timestamp.
        high (float): The highest price of the stock during the time period.
        low (float): The lowest price of the stock during the time period.
        close (float): The closing price of the stock at the given timestamp.
    """
    timestamp: str
    open: float
    high: float
    low: float
    close: float

class StockOverviewData(BaseModel):
    """
    Represents an overview of a stock.

    This model includes the stock's name, current price, and the price change
    percentage or amount.

    Attributes:
        stock_name (str): The name or ticker symbol of the stock.
        current_price (float): The current price of the stock.
        change (str): The price change of the stock, typically as a percentage or a value.
    """
    stock_name: str
    current_price: float
    change: str

class HistoricalDataResponse(APIResponseModel[List[StockData]]):
    """
    Represents the response model for historical stock data.
    
    This class extends the generic `APIResponseModel` and is used specifically for responses containing
    a list of stock data points (historical data) within the defined period.

    Attributes:
        success (bool): Indicates whether the API request was successful.
        status (int): The HTTP status code associated with the response.
        message (str): A message describing the result of the API request.
        data (List[StockData]): A list of `StockData` objects representing historical stock data.
    """
    pass

class PredictResponse(APIResponseModel[Dict[str, List]]):
    """
    Represents the response model for stock prediction data.
    
    This class extends the generic `APIResponseModel` and is used specifically for responses containing
    a dictionary of stock prediction data.

    Attributes:
        success (bool): Indicates whether the API request was successful.
        status (int): The HTTP status code associated with the response.
        message (str): A message describing the result of the API request.
        data (Dict[str, List]): A dictionary containing the prediction results for stock data.
    """
    pass

class PastValuesResponse(APIResponseModel[Dict[str, List]]):
    """
    Represents the response model for past stock values.
    
    This class extends the generic `APIResponseModel` and is used specifically for responses containing
    a dictionary of past stock values.

    Attributes:
        success (bool): Indicates whether the API request was successful.
        status (int): The HTTP status code associated with the response.
        message (str): A message describing the result of the API request.
        data (Dict[str, List]): A dictionary containing the past values of stock data.
    """
    pass

class StockOverviewResponse(APIResponseModel[List[StockOverviewData]]):
    """
    Represents the response model for the stock overview.
    
    This class extends the generic `APIResponseModel` and is used specifically for responses containing
    a list of dictionaries, each representing an individual stock's overview, including its change in price.

    Attributes:
        success (bool): Indicates whether the API request was successful.
        status (int): The HTTP status code associated with the response.
        message (str): A message describing the result of the API request.
        data (List[StockOverviewData]): A list of dictionaries containing stock names, current Adj Close prices, and their price change data.
    """
    pass

class MarketStateResponse(APIResponseModel[bool]):
    """
    Represents the response model for the market state.

    This class extends the generic `APIResponseModel` and is used specifically for responses containing
    the state of the market, such as whether it is open or closed.

    Attributes:
        success (bool): Indicates whether the API request was successful.
        status (int): The HTTP status code associated with the response.
        message (str): A message describing the result of the API request.
        data (bool): A boolean indicating the current market state (True for open, False for closed).
    """
    pass

class CreateModelResponse(APIResponseModel):
    """
    Represents the response model for the model creation process.

    This class extends the generic `APIResponseModel` and is used specifically for responses containing
    information about the initiation of a model creation process.

    Attributes:
        success (bool): Indicates whether the API request was successful.
        status (int): The HTTP status code associated with the response.
        message (str): A message describing the result of the API request.
        data (None): This response does not contain additional data.
    """
    pass
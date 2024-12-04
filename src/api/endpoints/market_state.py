from fastapi import APIRouter
from src.Classes.SchedulerThread import SchedulerThread
from src.Classes.APIResponseModel import MarketStateResponse


router = APIRouter()


@router.get("/market_state", response_model=MarketStateResponse)
async def market_state():
    """
    API endpoint to check the current market status.

    This endpoint determines whether the market is open or closed by invoking a method from
    the `SchedulerThread` class. It returns the market status along with a success message
    if the operation is successful, or an error message if an exception occurs.

    Returns:
        MarketStateResponse: A response model containing the market status, a success flag,
        a status code, and a descriptive message.

    Raises:
        Exception: If an error occurs while determining the market status.
    """
    try:
        is_market_open = not SchedulerThread._is_market_close()

        return MarketStateResponse(
            success=True,
            status=200,
            message="Market status checked successfully.",
            data=is_market_open
        )
    except Exception as e:
        return MarketStateResponse(
            success=False,
            status=500,
            message="Error while checking the market status: " + str(e),
            data=None
        )

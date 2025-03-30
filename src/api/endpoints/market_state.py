from fastapi import APIRouter

from src.Classes.SchedulerThread import SchedulerThread
from src.Classes.APIResponseModel import MarketStateResponse

"""
This module defines an endpoint (`/market_state`) that determines whether the market
is currently open or closed, leveraging a method from SchedulerThread to evaluate
market status.
"""

router = APIRouter()


@router.get("/market_state", response_model=MarketStateResponse)
async def market_state() -> MarketStateResponse:
    """
    Check the current market status.

    This endpoint checks if the market is open by calling the SchedulerThread's
    `_is_market_close()` method. If `_is_market_close()` returns True, it means
    the market is closed, so we invert that to find out if the market is open.

    Returns:
        MarketStateResponse: A response model containing:
            - success (bool): Indicates whether the operation was successful.
            - status (int): HTTP-like status code (200 for success, 500 if error).
            - message (str): A description of the result.
            - data (bool | None): True if the market is open, False if closed, or None on error.

    Raises:
        Exception: If an unexpected error occurs while determining the market status.
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
            message=f"Error while checking the market status: {str(e)}",
            data=None
        )

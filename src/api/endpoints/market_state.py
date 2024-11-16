from fastapi import APIRouter
from src.Classes.SchedulerThread import SchedulerThread
from src.Classes.APIResponseModel import MarketStateResponse


router = APIRouter()


@router.get("/market_state", response_model=MarketStateResponse)
async def market_state():
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

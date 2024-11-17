from fastapi import APIRouter
import yfinance as yf
import os
import stat
from src.Classes.APIResponseModel import CreateModelResponse
from src.Classes.APIRaisedError import APIRaisedError


router = APIRouter()


def create_models_for_stock_name(stock_name: str):
    
    stock_data = yf.download(stock_name, period="3mo", interval="1h")

    if stock_data.empty:
        raise APIRaisedError(404, "No data found for the specified stock.")

    model_path = os.path.join("create_models", stock_name)
    if os.path.exists(model_path):
        raise APIRaisedError(404, "Model file already exists for specified stock.")
    
    base_folder_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "../../../create_models")
    )
    stock_folder_path = os.path.join(base_folder_path, stock_name)
    
    os.makedirs(stock_folder_path, exist_ok=True)

    file_template = """
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from src.Classes.ModelCreator import ModelCreator

creator = ModelCreator("{stock_name}", "1h")

creator.train_tune(plot=False)
"""

    file_name = f"create_1h_{stock_name}_model.py"
    file_path = os.path.join(stock_folder_path, file_name)
    
    with open(file_path, "w") as file:
        file_content = file_template.format(stock_name=stock_name)
        file.write(file_content)
    
    os.chmod(file_path, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)


@router.post("/create_model", response_model=CreateModelResponse)
async def create_model(stock_name: str):
    try:
        create_models_for_stock_name(stock_name)

        return CreateModelResponse(
            success=True,
            status=200,
            message="Training has been started.",
            data=None
        )
    except APIRaisedError as e:
        return CreateModelResponse(
            success=False,
            status=e.status,
            message=e.message,
            data=None
        )
    except Exception as e:
        return CreateModelResponse(
            success=False,
            status=500,
            message="Error while creating model: " + str(e),
            data=None
        )

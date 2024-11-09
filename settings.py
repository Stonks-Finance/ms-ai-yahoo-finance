import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_TUNING_HISTORIES_DIR=str(os.getenv("_TUNING_HISTORIES_DIR"))
_MODELS_DIR=str(os.getenv("_MODELS_DIR"))
CREATE_MODELS_DIR:str="../create_models"

MODELS_DIRECTORY = os.path.join(BASE_DIR, _MODELS_DIR)
TUNING_HISTORIES_DIRECTORY = os.path.join(BASE_DIR, _TUNING_HISTORIES_DIR)

SEED = int(os.getenv("SEED", 6))



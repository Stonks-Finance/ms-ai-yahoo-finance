import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))

_TUNING_HISTORIES_DIR = str(os.getenv("_TUNING_HISTORIES_DIR"))

_MODELS_DIR = str(os.getenv("_MODELS_DIR"))

CREATE_MODELS_DIR: str = "create_models"

MODELS_DIRECTORY: str = os.path.join(BASE_DIR, _MODELS_DIR)

TUNING_HISTORIES_DIRECTORY: str = os.path.join(BASE_DIR, _TUNING_HISTORIES_DIR)

DEBUG: int = os.getenv("DEBUG", "False").lower() == "true"

SEED: int = int(os.getenv("_SEED", 6))

IP: str = os.getenv("_IP", "0.0.0.0")

PORT: int = int(os.getenv("_PORT", "8000"))

import os
from dotenv import load_dotenv

load_dotenv()


BASE_DIR: str = os.path.dirname(os.path.abspath(__file__))

CREATE_MODELS_DIR: str = "create_models"

MODELS_DIRECTORY: str = os.path.join(BASE_DIR, str(os.getenv("MODELS_DIRECTORY")))

TUNING_HISTORIES_DIRECTORY: str = os.path.join(BASE_DIR, str(os.getenv("TUNING_HISTORIES_DIRECTORY")))

DEBUG: int = os.getenv("DEBUG", "False").lower() == "true"

SEED: int = int(os.getenv("SEED", 6))

IP: str = os.getenv("IP", "0.0.0.0")

PORT: int = int(os.getenv("PORT", "8000"))

import os
import platform
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
_TUNING_HISTORIES_DIR=str(os.getenv("_TUNING_HISTORIES_DIR"))
_MODELS_DIR=str(os.getenv("_MODELS_DIR"))

if platform.system() == "Windows":
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles_windows")
    MEDIA_ROOT = os.path.join(BASE_DIR, "media_windows")
elif platform.system() == "Linux":
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles_linux")
    MEDIA_ROOT = os.path.join(BASE_DIR, "media_linux")
elif platform.system() == "Darwin":  # macOS
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles_mac")
    MEDIA_ROOT = os.path.join(BASE_DIR, "media_mac")
else:
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
    MEDIA_ROOT = os.path.join(BASE_DIR, "media")

MODELS_DIRECTORY = os.path.join(BASE_DIR, _MODELS_DIR)
TUNING_HISTORIES_DIRECTORY = os.path.join(BASE_DIR, _TUNING_HISTORIES_DIR)

SEED = int(os.getenv("SEED", 6))



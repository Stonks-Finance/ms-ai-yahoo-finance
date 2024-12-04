import threading
from src.Classes.SchedulerThread import SchedulerThread
from src.api.api import run_api
import os
from settings import DEBUG,CREATE_MODELS_DIR


if DEBUG:
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = '1'
else:
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = '2'

    
if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api, name="APIThread")
    api_thread.start()

    create_thread = SchedulerThread(dur=30, _dir=CREATE_MODELS_DIR, is_refit=False)
    create_thread.start()
    
    api_thread.join()
    create_thread.join()
    
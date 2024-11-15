import threading
import uvicorn
from src.Classes.SchedulerThread import SchedulerThread
from src.api.api import api
import os
from settings import DEBUG,CREATE_MODELS_DIR

if DEBUG:
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = '1'
else:
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = '2'

def run_api():
    uvicorn.run(api, host="127.0.0.1", port=8000, reload=False)
    
if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api, name="APIThread")
    api_thread.start()

    create_thread = SchedulerThread(dur=30, _dir=CREATE_MODELS_DIR, is_refit=False)
    create_thread.start()

    refit_thread = SchedulerThread(dur=10, _dir=CREATE_MODELS_DIR, is_refit=True)
    refit_thread.start()

    api_thread.join()
    create_thread.join()
    refit_thread.join()
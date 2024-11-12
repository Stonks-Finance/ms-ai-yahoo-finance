import threading
import uvicorn
from src.automate_training import run_schedule,run_refit_schedule
import os
from settings import DEBUG,CREATE_MODELS_DIR

if DEBUG:
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = '1'
else:
    os.environ["TF_CPP_MIN_LOG_LEVEL"] = '2'

def run_api():
    uvicorn.run("api.api:api", host="127.0.0.1", port=8000, reload=False)

if __name__ == "__main__":

    api_thread = threading.Thread(target=run_api)
    api_thread.start()
    
    create_thread = threading.Thread(target=run_schedule, args=(30, CREATE_MODELS_DIR))
    create_thread.start()
    
    refit_thread = threading.Thread(target=run_refit_schedule, args=(15, CREATE_MODELS_DIR))
    refit_thread.start()

    api_thread.join()
    create_thread.join()
    refit_thread.join()

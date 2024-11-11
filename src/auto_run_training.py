from automate_training import check_and_run
import schedule
import time
from settings import CREATE_MODELS_DIR

directory_to_run: str = CREATE_MODELS_DIR

schedule.every(30).minutes.do(check_and_run, directory=directory_to_run)

print("Monitoring stock market close...")

while True:
    schedule.run_pending()
    time.sleep(30)

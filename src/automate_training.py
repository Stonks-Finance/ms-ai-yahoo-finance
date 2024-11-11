import schedule
import time
import os
import subprocess
from datetime import datetime
import pytz
from settings import CREATE_MODELS_DIR


def _run_all_files (directory: str) -> None:
    files = [f for f in os.listdir(directory) if f.endswith(".py")]
    for file in files:
        file_path = os.path.join(directory, file)
        print(f"Running {file_path}...")
        subprocess.run(["python", file_path])
        print(f"Finished {file_path} at {datetime.now()}")


def _is_market_close () -> bool:
    azerbaijan_time = pytz.timezone("Asia/Baku")
    eastern_time = pytz.timezone("US/Eastern")
    now_in_azerbaijan = datetime.now(azerbaijan_time)
    now_in_eastern = now_in_azerbaijan.astimezone(eastern_time)
    return now_in_eastern.weekday() < 5 and now_in_eastern.hour >= 16


def check_and_run (directory: str) -> None:
    if _is_market_close():
        _run_all_files(directory)


def run_schedule ():
    directory_to_run = CREATE_MODELS_DIR
    schedule.every(30).minutes.do(check_and_run, directory=directory_to_run)
    print("Monitoring stock market close...")
    while True:
        schedule.run_pending()
        time.sleep(30)

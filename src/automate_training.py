import schedule
import time
import os
import subprocess
from datetime import datetime
import pytz



def _run_all_files (directory: str, filter_1m: bool = False) -> None:
    for subdir in os.listdir(directory):
        subdir_path = os.path.join(directory, subdir)
        if os.path.isdir(subdir_path):
            print(f"Checking directory: {subdir_path}")
            
            if filter_1m:
                files = [f for f in os.listdir(subdir_path) if f.endswith(".py") and '1m' in f]
            else:
                files = [f for f in os.listdir(subdir_path) if f.endswith(".py")]
            
            for file in files:
                file_path = os.path.join(subdir_path, file)
                print(f"Running {file_path}...")
                subprocess.run(["python", file_path])
                print(f"Finished {file_path} at {datetime.now()}")


def _is_market_close () -> bool:
    azerbaijan_time = pytz.timezone("Asia/Baku")
    eastern_time = pytz.timezone("US/Eastern")
    now_in_azerbaijan = datetime.now(azerbaijan_time)
    now_in_eastern = now_in_azerbaijan.astimezone(eastern_time)
    return now_in_eastern.weekday() < 5 and now_in_eastern.hour >= 16


def run_all_files_at_market_close (directory: str) -> None:
    if _is_market_close():
        print("Market is closed. Running all files once...")
        _run_all_files(directory)
        print("All files have been run. Stopping further executions until market opens.")


def run_schedule (dur: int, _dir: str):
    schedule.every(dur).minutes.do(run_all_files_at_market_close, directory=_dir)
    print("Monitoring stock market close...")
    
    while True:
        schedule.run_pending()
        time.sleep(dur * 60)


def run_refit_schedule (dur: int, _dir: str):
    while True:
        if not _is_market_close():
            print("Market is open. Running '1m' refit files every 15 minutes.")
            _run_all_files(_dir, filter_1m=True)
        else:
            print("Market is closed. Stopping '1m' refit process temporarily.")
        time.sleep(dur * 60)

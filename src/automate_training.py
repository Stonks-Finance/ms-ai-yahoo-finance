import subprocess
import os
from datetime import datetime
import pytz


def run_all_files(directory:str)->None:
    files = [f for f in os.listdir(directory) if f.endswith(".py")]
    for file in files:
        file_path = os.path.join(directory, file)
        print(f"Running {file_path}...")
        subprocess.run(["python", file_path])
        print(f"Finished {file_path} at {datetime.now()}")


def _is_market_close()->bool:
    azerbaijan_time = pytz.timezone("Asia/Baku")
    eastern_time = pytz.timezone("US/Eastern")
    now_in_azerbaijan = datetime.now(azerbaijan_time)
    now_in_eastern = now_in_azerbaijan.astimezone(eastern_time)
    if now_in_eastern.weekday() < 5 and now_in_eastern.hour == 16 and now_in_eastern.minute == 0:
        return True
    return False


def check_and_run(directory:str)->None:
    if _is_market_close():
        run_all_files(directory)



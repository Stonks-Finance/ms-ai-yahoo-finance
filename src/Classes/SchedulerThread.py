import schedule
import time
import os
import subprocess
from datetime import datetime
import pytz
import threading


class SchedulerThread(threading.Thread):
    def __init__ (self, dur: int,
                  _dir: str,
                  is_refit: bool = False) -> None:
        
        super().__init__()
        self.dur = dur
        self._dir = _dir
        self.is_refit = is_refit
    
    def run (self):
        if self.is_refit:
            self.run_refit_schedule()
        else:
            self.run_schedule()
    
    @staticmethod
    def _run_all_files (directory: str,filter_5m:bool=False) -> None:
        for subdir in os.listdir(directory):
            subdir_path = os.path.join(directory, subdir)
            if os.path.isdir(subdir_path):
                print(f"Checking directory: {subdir_path}")
                files = [f for f in os.listdir(subdir_path)
                         if f.endswith(".py") and ("5m" in f if filter_5m else True)]
                
                for file in files:
                    file_path = os.path.join(subdir_path, file)
                    print(f"Running {file_path}...")
                    subprocess.Popen(["python", file_path])
                    print(f"Finished {file_path} at {datetime.now()}")
    
    @staticmethod
    def _is_market_close () -> bool:
        azerbaijan_time = pytz.timezone("Asia/Baku")
        eastern_time = pytz.timezone("US/Eastern")
        now_in_azerbaijan = datetime.now(azerbaijan_time)
        now_in_eastern = now_in_azerbaijan.astimezone(eastern_time)
        return now_in_eastern.weekday() < 5 and now_in_eastern.hour >= 16
    
    def run_all_files_at_market_close (self, directory: str) -> None:
        if self._is_market_close():
            print("Market is closed. Running all files once...")
            self._run_all_files(directory)
            print("All files have been run. Stopping further executions until market opens.")
    
    def run_schedule (self):
        schedule.every(self.dur).minutes.do(self.run_all_files_at_market_close, directory=self._dir)
        print("Monitoring stock market close...")
        
        while True:
            schedule.run_pending()
            time.sleep(self.dur * 60)
    
    def run_refit_schedule (self):
        while True:
            if not self._is_market_close():
                print(f"Market is open. Running '5m' refit files every {self.dur} minutes.")
                
                self._run_all_files(self._dir, filter_5m=True)
            else:
                print("Market is closed. Stopping '1m' refit process temporarily.")
            time.sleep(self.dur * 30)

import os
import subprocess
import threading
import time
from datetime import datetime

import pytz
import schedule


class SchedulerThread(threading.Thread):
    """
    A thread-based scheduler that periodically checks whether the market is closed
    and, if so, runs all Python files in a specified directory.

    Attributes:
        dur (int): The interval in minutes at which the scheduler checks the market status.
        _dir (str): The directory containing subdirectories with .py files to be executed.
        is_refit (bool): Flag to indicate if this scheduler is intended for refitting models.
    """

    def __init__(self, dur: int, _dir: str, is_refit: bool = False) -> None:
        """
        Initializes the SchedulerThread.

        Args:
            dur (int): The frequency (in minutes) at which to run the scheduled tasks.
            _dir (str): The root directory containing subfolders with .py scripts.
            is_refit (bool, optional): Whether this schedule is for refitting models. Defaults to False.
        """
        super().__init__()
        self.dur = dur
        self._dir = _dir
        self.is_refit = is_refit

    def run(self):
        """
        Entry point for the thread execution. Starts the schedule
        to continually monitor and run tasks.
        """
        self.run_schedule()

    @staticmethod
    def _run_all_files(directory: str) -> None:
        """
        Executes all Python (.py) files found in each subdirectory of the given directory.

        Args:
            directory (str): The root directory where subdirectories containing .py files are located.
        """
        for subdir in os.listdir(directory):
            subdir_path = os.path.join(directory, subdir)
            if os.path.isdir(subdir_path):
                print(f"Checking directory: {subdir_path}")
                files = [f for f in os.listdir(subdir_path) if f.endswith(".py")]
                for file in files:
                    file_path = os.path.join(subdir_path, file)
                    print(f"Running {file_path}...")
                    subprocess.Popen(["python", file_path])
                    print(f"Finished {file_path} at {datetime.now()}")

    @staticmethod
    def _is_market_close() -> bool:
        """
        Determines whether the current time in US/Eastern indicates that the market is closed.

        Returns:
            bool: True if the market is closed, False otherwise.
        """
        azerbaijan_time = pytz.timezone("Asia/Baku")
        eastern_time = pytz.timezone("US/Eastern")
        now_in_azerbaijan = datetime.now(azerbaijan_time)
        now_in_eastern = now_in_azerbaijan.astimezone(eastern_time)
        return now_in_eastern.weekday() < 5 and now_in_eastern.hour >= 16

    def run_all_files_at_market_close(self, directory: str) -> None:
        """
        Checks if the market is closed and, if true, runs all Python files in the specified directory.

        Args:
            directory (str): The root directory containing subfolders with .py scripts.
        """
        if self._is_market_close():
            print("Market is closed. Running all files once...")
            self._run_all_files(directory)
            print("All files have been run. Stopping further executions until market opens.")

    def run_schedule(self):
        """
        Schedules the market-close check to run every `dur` minutes. When triggered,
        it attempts to run the .py files in the given directory if the market is closed.
        """
        schedule.every(self.dur).minutes.do(self.run_all_files_at_market_close, directory=self._dir)
        print("Monitoring stock market close...")
        while True:
            schedule.run_pending()
            time.sleep(self.dur * 60)

    def run_refit_schedule(self):
        """
        An alternative schedule method to be used for refitting tasks. It continuously checks
        whether the market is closed and can pause model refitting if it is.
        """
        while True:
            if self._is_market_close():
                print("Market is closed. Stopping '1m' refit process temporarily.")
            time.sleep(self.dur * 30)

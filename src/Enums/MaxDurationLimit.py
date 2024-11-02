from enum import Enum

class MaxDurationLimit(Enum):
    ONE_MINUTE = {
        "PREDICT": 30,
        "PAST_VALUES": 60
    }
    ONE_HOUR = {
        "PREDICT": 10,
        "PAST_VALUES": 120
    }
    ONE_DAY = {
        "HISTORICAL_DATA": 1500
    }
    ONE_MONTH = {
        "HISTORICAL_DATA": 120
    }
    
    def get_limit(self, endpoint: str):
        return self.value.get(endpoint)
    
    @property
    def interval(self):
        return self.name.lower()
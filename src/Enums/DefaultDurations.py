from enum import Enum

class DefaultDurations(Enum):
    ONE_MINUTE = {
        "PREDICT": 10,
        "PAST_VALUES": 15
    }
    ONE_HOUR = {
        "PREDICT": 5,
        "PAST_VALUES": 24
    }
    ONE_DAY = {
        "HISTORICAL_DATA": 30
    }
    ONE_MONTH = {
        "HISTORICAL_DATA": 12
    }
    
    def get_duration(self, endpoint: str):
        return self.value.get(endpoint)

    @property
    def interval(self):
        return self.name.lower()

from enum import Enum

class DefaultDurations(Enum):
    ONE_DAY = ("1d", 7)
    ONE_MONTH = ("1mo", 12)
    
    @property
    def interval (self):
        return self.value[0]
    
    @property
    def duration (self):
        return self.value[1]


class MaxDurationLimit(Enum):
    ONE_DAY = ("1d", 1500)
    ONE_MONTH = ("1mo", 120)
    
    @property
    def interval (self):
        return self.value[0]
    
    @property
    def limit (self):
        return self.value[1]
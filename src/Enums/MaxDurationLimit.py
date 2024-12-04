from enum import Enum

class MaxDurationLimit(Enum):
    """
    Enum representing the maximum duration limits for different API endpoints based on time intervals.
    
    This class defines various time intervals (e.g., ONE_MINUTE, ONE_HOUR, etc.) and associates each interval
    with specific maximum duration limits for endpoints like 'PREDICT', 'PAST_VALUES', and 'HISTORICAL_DATA'.
    The class provides a method to retrieve the maximum duration for a given endpoint and a property to get
    the corresponding interval name.

    Attributes:
        ONE_HOUR (dict): Maximum durations for 'PREDICT' (6), 'PAST_VALUES' (120), and 'HISTORICAL_DATA' (1000) for the 1-hour interval.
        ONE_DAY (dict): Maximum duration for 'HISTORICAL_DATA' (1500) for the 1-day interval.
        ONE_MONTH (dict): Maximum duration for 'HISTORICAL_DATA' (120) for the 1-month interval.
    """
    ONE_HOUR = {
        "PREDICT": 6,
        "PAST_VALUES": 120,
        "HISTORICAL_DATA": 1000
    }
    ONE_DAY = {
        "HISTORICAL_DATA": 1500
    }
    ONE_MONTH = {
        "HISTORICAL_DATA": 120
    }
    
    def get_limit(self, endpoint: str):
        """
        Retrieves the maximum duration limit for a given endpoint based on the current interval.
        
        Args:
            endpoint (str): The endpoint name (e.g., 'PREDICT', 'PAST_VALUES', or 'HISTORICAL_DATA').

        Returns:
            int: The maximum duration associated with the given endpoint.

        Raises:
            KeyError: If the endpoint is not found in the duration dictionary for the current interval.
        """
        return self.value.get(endpoint)
    
    @property
    def interval(self):
        """
        Gets the name of the interval in lowercase format.

        This property returns the interval name (e.g., 'one_minute', 'one_hour') in lowercase, 
        which corresponds to the current enum member's name.

        Returns:
            str: The lowercase interval name.
        """
        return self.name.lower()
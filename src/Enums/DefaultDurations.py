from enum import Enum

class DefaultDurations(Enum):
    """
    Enum representing default durations for different API endpoints based on time intervals.
    
    This class defines different time intervals (e.g., ONE_MINUTE, ONE_HOUR, etc.) and associates
    each interval with specific default durations for endpoints like 'PREDICT', 'PAST_VALUES', and 'HISTORICAL_DATA'.
    The class also provides a method to retrieve the default duration for a given endpoint and a property
    to get the corresponding interval name.

    Attributes:
        ONE_MINUTE (dict): Default durations for 'PREDICT' (10) and 'PAST_VALUES' (15) for the 1-minute interval.
        ONE_HOUR (dict): Default durations for 'PREDICT' (5), 'PAST_VALUES' (24), and 'HISTORICAL_DATA' (24) for the 1-hour interval.
        ONE_DAY (dict): Default duration for 'HISTORICAL_DATA' (30) for the 1-day interval.
        ONE_MONTH (dict): Default duration for 'HISTORICAL_DATA' (12) for the 1-month interval.
    """
    ONE_MINUTE = {
        "PREDICT": 10,
        "PAST_VALUES": 15
    }
    ONE_HOUR = {
        "PREDICT": 5,
        "PAST_VALUES": 24,
        "HISTORICAL_DATA": 24
    }
    ONE_DAY = {
        "HISTORICAL_DATA": 30
    }
    ONE_MONTH = {
        "HISTORICAL_DATA": 12
    }
    
    def get_duration(self, endpoint: str):
        """
        Retrieves the default duration for a given endpoint based on the current interval.
        
        Args:
            endpoint (str): The endpoint name (e.g., 'PREDICT', 'PAST_VALUES', or 'HISTORICAL_DATA').

        Returns:
            int: The default duration associated with the given endpoint.

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

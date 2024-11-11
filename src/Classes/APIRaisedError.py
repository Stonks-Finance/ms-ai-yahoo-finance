
class APIRaisedError(Exception):
    """
    Custom exception class for raising errors in the API with a specific status code and message.
    
    This class extends the built-in `Exception` class and is used to raise custom errors in the API
    with additional context: a status code (e.g., HTTP status code) and a message explaining the error.

    Attributes:
        status (int): The HTTP status code associated with the error (e.g., 404 for Not Found).
        message (str): A message describing the error or providing details about the problem.
    """

    def __init__(self, status: int, message: str):
        """
        Initializes the custom exception with a status code and message.
        
        Args:
            status (int): The HTTP status code for the error.
            message (str): A message explaining the error.
        """
        super().__init__(message)
        self.status = status
        self.message = message
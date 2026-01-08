class BusinessLogicError(Exception):
    """Base exception for business logic errors."""
    def __init__(self, message, code=None):
        self.message = message
        self.code = code
        super().__init__(message)

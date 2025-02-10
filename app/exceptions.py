from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST, HTTP_500_INTERNAL_SERVER_ERROR

class NotFoundException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=HTTP_404_NOT_FOUND, detail=detail)

class DatabaseException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)

class InvalidFieldError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=HTTP_400_BAD_REQUEST, detail=detail)

class CustomerNotFoundError(HTTPException):
    """Raised when a customer is not found in the database."""
    def __init__(self, customer_id: int):
        detail = f"Customer with ID {customer_id} not found."
        super().__init__(status_code=HTTP_404_NOT_FOUND, detail=detail)

class DuplicateCustomerError(HTTPException):
    """Raised when a customer with the same user_id already exists."""
    def __init__(self, user_id: int):
        detail = f"Customer with user_id={user_id} already exists."
        super().__init__(status_code=HTTP_400_BAD_REQUEST, detail=detail)

class DatabaseError(HTTPException):
    """Raised when a database operation fails."""
    def __init__(self, message: str):
        super().__init__(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database error: {message}")

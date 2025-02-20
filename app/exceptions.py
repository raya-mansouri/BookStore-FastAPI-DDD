from fastapi import HTTPException
from starlette.status import (
    HTTP_404_NOT_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


# Custom exception for "Not Found" errors
class NotFoundException(HTTPException):
    def __init__(self, detail: str):
        # Initializes the exception with a 404 status code and the provided detail
        super().__init__(status_code=HTTP_404_NOT_FOUND, detail=detail)


# Custom exception for database-related errors
class DatabaseException(HTTPException):
    def __init__(self, detail: str):
        # Initializes the exception with a 500 status code and the provided detail
        super().__init__(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)


# Custom exception for invalid fields provided in the request
class InvalidFieldError(HTTPException):
    def __init__(self, detail: str):
        # Initializes the exception with a 400 status code and the provided detail
        super().__init__(status_code=HTTP_400_BAD_REQUEST, detail=detail)


# Custom exception for when a customer is not found in the database
class CustomerNotFoundError(HTTPException):
    """Raised when a customer is not found in the database."""

    def __init__(self, customer_id: int):
        # Creates a detail message indicating the specific customer ID that was not found
        detail = f"Customer with ID {customer_id} not found."
        super().__init__(status_code=HTTP_404_NOT_FOUND, detail=detail)


# Custom exception for when a customer with the same user_id already exists
class DuplicateCustomerError(HTTPException):
    """Raised when a customer with the same user_id already exists."""

    def __init__(self, user_id: int):
        # Creates a detail message indicating the duplicate customer user ID
        detail = f"Customer with user_id={user_id} already exists."
        super().__init__(status_code=HTTP_400_BAD_REQUEST, detail=detail)


# Custom exception for generic database errors
class DatabaseError(HTTPException):
    """Raised when a database operation fails."""

    def __init__(self, message: str):
        # Initializes the exception with a 500 status code and a detailed error message
        super().__init__(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {message}",
        )

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


# Genre class to represent a book's genre. It's currently a simple data class
class Genre:
    id: int
    name: str


# Book class to represent a book entity with its fields and business logic
class Book:
    id: int
    title: str
    isbn: str
    price: int
    genre_id: int
    units: int
    description: str
    reserved_units: int
    authors: List[int]

    def __init__(
        self,
        title: str,
        isbn: str,
        price: int,
        genre_id: int,
        units: int,
        description: str,
        reserved_units: int,
        authors: List[int],
    ):
        """
        Initializes a new Book instance.

        Args:
        - title (str): The title of the book.
        - isbn (str): The ISBN of the book.
        - price (int): The price of the book in Toman.
        - genre_id (int): The ID of the genre the book belongs to.
        - units (int): The total number of available units of the book.
        - description (str): A brief description of the book.
        - reserved_units (int): The number of units already reserved.
        - authors (List[int]): A list of author IDs associated with the book.
        """
        self.title = title
        self.isbn = isbn
        self.price = price
        self.genre_id = genre_id
        self.units = units
        self.description = description
        self.reserved_units = reserved_units
        self.authors = authors

    def to_dict(self):
        """
        Converts the Book instance to a dictionary format.

        Returns:
        - dict: A dictionary representing the book with its fields.
        """
        return {
            "id": self.id,
            "title": self.title,
            "isbn": self.isbn,
            "price": self.price,
            "genre_id": self.genre_id,
            "units": self.units,
            "description": self.description,
            "reserved_units": self.reserved_units,
            "author_ids": self.author_ids,
        }

    def cancel_reservation(self):
        """
        Cancels one reservation by decreasing the reserved_units.
        """
        self.reserved_units -= 1

    def reserve_book(self):
        """
        Reserves one unit of the book by increasing reserved_units.
        """
        self.reserved_units += 1


# Base schema for book-related models using Pydantic for validation
class BookBase(BaseModel):
    """
    A base schema for all book-related models.
    It contains shared fields and validation rules for book data.
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="The title of the book.",
        example="The Great Gatsby",
    )
    isbn: str = Field(
        ...,
        pattern=r"^\d{13}$",
        description="The ISBN-13 of the book (must be exactly 13 digits and unique).",
        example="9783161484100",
    )
    price: int = Field(
        ...,
        gt=0,
        description="The price of the book in Toman (must be greater than 0).",
        example=29000,
    )
    genre_id: int = Field(
        ..., description="The ID of the genre the book belongs to.", example=1
    )
    description: Optional[str] = Field(
        "No description provided",
        min_length=10,
        max_length=1000,
        description="A brief description of the book (optional).",
        example="A classic novel about the American Dream.",
    )
    units: int = Field(
        ...,
        ge=0,
        description="The number of available units of the book (must be 0 or greater).",
        example=10,
    )
    author_ids: List[int] = Field(
        ...,
        min_items=1,
        description="A list of author IDs for the book (must have at least one author).",
        example=[1, 2],
    )

    @field_validator("title")
    def validate_title(cls, value: str) -> str:
        """
        Validates that the title is not empty and is properly formatted.

        Args:
        - value (str): The title of the book.

        Returns:
        - str: The validated title.

        Raises:
        - HTTPException: If the title is empty or just whitespace.
        """
        if not value.strip():
            raise HTTPException(
                status_code=400, detail="Title cannot be empty or just whitespace."
            )
        return value.strip()

    @field_validator("isbn")
    def validate_isbn(cls, value: str) -> str:
        """
        Validates that the ISBN is exactly 13 digits.

        Args:
        - value (str): The ISBN of the book.

        Returns:
        - str: The validated ISBN.

        Raises:
        - HTTPException: If the ISBN is not exactly 13 digits.
        """
        if not value.isdigit() or len(value) != 13:
            raise HTTPException(
                status_code=400, detail="ISBN must be exactly 13 digits."
            )
        return value

    @field_validator("author_ids")
    def validate_author_ids(cls, value: List[int]) -> List[int]:
        """
        Validates that there is at least one author ID.

        Args:
        - value (List[int]): A list of author IDs.

        Returns:
        - List[int]: The validated list of author IDs.

        Raises:
        - HTTPException: If no author IDs are provided.
        """
        if not value:
            raise HTTPException(
                status_code=400, detail="At least one author ID is required."
            )
        return value

    class Config:
        from_attributes = True


# Represents the data required to create a new book
class BookCreate(BookBase):
    """
    Inherits from BookBase and contains the data required to create a new book.
    """

    pass


# Represents the data that can be updated for a book
class BookUpdate(BookBase):
    """
    Allows partial updates to a book. All fields are optional to allow flexibility in updates.
    """

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="The title of the book.",
        example="The Great Gatsby",
    )
    isbn: Optional[str] = Field(
        None,
        pattern=r"^\d{13}$",
        description="The ISBN-13 of the book.",
        example="9783161484100",
    )
    price: Optional[int] = Field(
        None,
        gt=0,
        description="The price of the book in Toman (must be greater than 0).",
        example=29000,
    )
    genre_id: Optional[int] = Field(
        None, description="The ID of the genre the book belongs to.", example=1
    )
    description: Optional[str] = Field(
        None,
        min_length=10,
        max_length=1000,
        description="A brief description of the book (optional).",
        example="A classic novel about the American Dream.",
    )
    units: Optional[int] = Field(
        None,
        ge=0,
        description="The number of available units of the book.",
        example=10,
    )
    author_ids: Optional[List[int]] = Field(
        None,
        min_items=1,
        description="A list of author IDs for the book.",
        example=[1, 2],
    )


# Output schema for a Book with ID included
class BookOut(BookBase):
    """
    Represents the output data for a book, including its ID.
    """

    id: int

    class Config:
        from_attributes = True

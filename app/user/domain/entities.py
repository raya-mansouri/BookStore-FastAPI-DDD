from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.user.domain.object_values import UserRole


# User entity representing a user in the system
class User:
    id: int  # Unique identifier for the user
    username: str  # Username for the user
    first_name: str  # User's first name
    last_name: str  # User's last name
    phone: str  # User's phone number
    email: str  # User's email address
    role: str  # User's role (e.g., 'customer', 'admin')
    password: str  # User's password
    is_active: bool  # Status indicating if the user is active

    def __str__(self):
        return f"User(id={self.id}, username={self.username})"  # String representation of the User object

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return (
            other.id == self.id
        )  # Comparison method to check equality between two users

    def update_name(self, username: str):
        self.username = username  # Method to update the user's username


# City entity representing a city in the system
class City:
    id: int  # Unique identifier for the city
    name: str  # Name of the city

    def __str__(self):
        return self.name  # String representation of the City object


# Author entity, representing an author with a link to a user and city
class Author:
    id: int  # Unique identifier for the author
    user_id: int  # The ID of the associated user
    city_id: int  # The ID of the associated city
    goodreads_link: str  # Goodreads link for the author
    bank_account_number: str  # Author's bank account number


# Base class for creating and updating users, defines common attributes
class UserBase(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        example="john_doe",
        description="Unique username for login",
    )
    email: EmailStr = Field(
        ..., example="user@example.com", description="Valid email address"
    )
    first_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example="John",
        description="User's first name",
    )
    last_name: str = Field(
        ..., min_length=1, max_length=50, example="Doe", description="User's last name"
    )
    phone: str = Field(
        ...,
        min_length=11,
        max_length=11,
        example="09123456789",
        description="Iranian phone number starting with 09, 11 digits",
    )
    role: UserRole = Field(..., example=UserRole.CUSTOMER, description="User role")

    # Custom validation for phone number to ensure it starts with '09'
    @field_validator("phone")
    def validate_phone(cls, v):
        if not v.startswith("09"):
            raise ValueError("Phone number must start with '09'")
        return v


# Model for creating a new user, extending the base user model
class UserCreate(UserBase):
    password: str = Field(
        ...,
        example="strongpassword123",
        min_length=8,
        max_length=255,
        description="Password with minimum 8 characters",
    )


# Model for updating an existing user, allows optional fields
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, min_length=11, max_length=11)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=255)
    role: Optional[str] = Field(None, pattern="^(admin|customer|author)$")


# Model for outputting user data, including the user ID
class UserOut(UserBase):
    id: int  # Unique identifier for the user

    class Config:
        from_attributes = True  # Allow reading attributes from the model's fields


# Model for login step 1, requesting username and password
class LoginStep1Request(BaseModel):
    username: str = Field(..., example="john_doe")
    password: str = Field(..., example="strongpassword123")


# Model for login step 2, requesting OTP for two-factor authentication
class LoginStep2Request(BaseModel):
    otp: str = Field(..., example="123456", min_length=6, max_length=6)


# Model representing an authentication token
class Token(BaseModel):
    access_token: str  # The access token
    token_type: str  # The type of the token (e.g., 'bearer')


# Model for holding token data, typically used for user identification
class TokenData(BaseModel):
    id: int | None = None  # User's unique ID, or None if not available
    username: str | None = None  # User's username, or None if not available
    role: str | None = (
        None  # User's role (e.g., 'admin', 'customer'), or None if not available
    )

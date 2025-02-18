from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.user.domain.object_values import UserRole


class User:
    id: int
    username: str
    first_name: str
    last_name: str
    phone: str
    email: str
    role: str
    password: str
    is_active: bool

    def __str__(self):
        return f"User(id={self.id}, username={self.username})"

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return other.id == self.id

    def update_name(self, username: str):
        self.username = username


class City:
    id: int
    name: str

    def __str__(self):
        return self.name


class Author:
    id: int
    user_id: int
    city_id: int
    goodreads_link: str
    bank_account_number: str


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

    @field_validator("phone")
    def validate_phone(cls, v):
        if not v.startswith("09"):
            raise ValueError("Phone number must start with '09'")
        return v


class UserCreate(UserBase):
    password: str = Field(
        ...,
        example="strongpassword123",
        min_length=8,
        max_length=255,
        description="Password with minimum 8 characters",
    )


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    first_name: Optional[str] = Field(None, min_length=1, max_length=50)
    last_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone: Optional[str] = Field(None, min_length=11, max_length=11)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, max_length=255)
    role: Optional[str] = Field(None, pattern="^(admin|customer|author)$")


class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True


class LoginStep1Request(BaseModel):
    username: str = Field(..., example="john_doe")
    password: str = Field(..., example="strongpassword123")


class LoginStep2Request(BaseModel):
    otp: str = Field(..., example="123456", min_length=6, max_length=6)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None = None
    username: str | None = None
    role: str | None = None

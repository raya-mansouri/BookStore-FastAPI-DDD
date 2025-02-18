import pytz
from typing import Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, EmailStr, Field, field_validator
from fastapi import HTTPException
from app.domain.user.object_values import SubscriptionModel, UserRole
from app.exceptions import InvalidFieldError


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

class Customer:
    id: int
    user_id: int
    subscription_model: str
    subscription_end_time: datetime
    wallet_money_amount: int

    def __init__(self, user_id: int, subscription_model: str,subscription_end_time: datetime, wallet_money_amount: int):
        self.user_id = user_id
        self.subscription_model = subscription_model
        subscription_end_time = subscription_end_time
        self.wallet_money_amount = wallet_money_amount

    def __validate(self, id: int, user_id: int, subscription_model: str, wallet_money_amount: int):
        if not isinstance(user_id, int) or user_id <= 0:
            raise InvalidFieldError("User ID must be a positive integer.")
        
        if subscription_model not in SubscriptionModel:
            raise InvalidFieldError("subscription_model must be one of: 'free', 'plus', 'premium'.")
        
        if not isinstance(wallet_money_amount, int) or wallet_money_amount < 0:
            raise InvalidFieldError("Wallet money amount must be a non-negative integer.")
    
    def __setattr__(self, name, value):
        # Validate before setting any attribute
        if name == 'user_id' and (not isinstance(value, int) or value <= 0):
            raise InvalidFieldError("User ID must be a positive integer.")
        # elif name == "subscription_model":
        #     if value not in list(SubscriptionModel._value2member_map_):
        #         raise InvalidFieldError("subscription_model must be one of: 'free', 'plus', 'premium'.")
        #     else:
        #         value = SubscriptionModel(value)
        elif name == 'wallet_money_amount' and (not isinstance(value, int) or value < 0):
            raise InvalidFieldError("Wallet money amount must be a non-negative integer.")
        else:
            super().__setattr__(name, value)
    
    def __getattr__(self, name):
        # Handle attribute access if it does not exist
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def validate(self):
        # Re-run the validation logic, could be used for revalidation after changing values
        self.__validate(self.id, self.user_id, self.subscription_model, self.wallet_money_amount)

    def __repr__(self):
        return f"Customer(id={self.id}, user_id={self.user_id}, subscription_model='{self.subscription_model}', wallet_money_amount={self.wallet_money_amount})"
        
    def __eq__(self, other):
        if not isinstance(other, Customer):
            return False
        return self.id == other.id
    
    def charge_wallet(self, amount: int):
        """Increase the wallet balance by the given amount."""
        self.wallet_money_amount += amount

    def upgrade_subscription(self, new_model: str):
        pre_wallet_amount = self.wallet_money_amount
        pre_subscription_model = self.subscription_model
        iran_timezone = pytz.timezone('Asia/Tehran')
        now = datetime.now(iran_timezone)

        cost_mapping = {
            ("free", "plus"): 50000,
            ("plus", "premium"): 150000,
            ("free", "premium"): 200000
        }
        duration = timedelta(days=30)  # Both "plus" and "premium" last for 1 month

        cost = cost_mapping.get((pre_subscription_model, new_model))
        if cost is None:
            raise ValueError("Invalid subscription upgrade path")

        if pre_wallet_amount < cost:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")

        self.wallet_money_amount -= cost
        self.subscription_model = new_model
        self.subscription_end_time = now + duration
    
    def deduct_from_wallet(self, amount):
        self.wallet_money_amount -= amount


from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class SubscriptionModel(str, Enum):
    free = "free"
    plus = "plus"
    premium = "premium"

class CustomerBase(BaseModel):
    user_id: int = Field(..., description="The ID of the user associated with the customer", example=1)
    subscription_model: str = Field(SubscriptionModel.free, description="Subscription model of the customer", example="free")
    subscription_end_time: Optional[datetime] = Field(None, description="End time of the subscription", example="2023-12-31T23:59:59")
    wallet_money_amount: int = Field(0, description="Amount of money in the wallet", example=10000)

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    subscription_model: Optional[str] = Field(None, description="Subscription model of the customer", example="premium")
    subscription_end_time: Optional[datetime] = Field(None, description="End time of the subscription", example="2024-12-31T23:59:59")
    wallet_money_amount: Optional[int] = Field(None, description="Amount of money in the wallet", example=20000)

class CustomerOut(CustomerBase):
    id: int = Field(..., description="The unique identifier for the customer", example=1)

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, example="john_doe", description="Unique username for login")
    email: EmailStr = Field(..., example="user@example.com", description="Valid email address")
    first_name: str = Field(..., min_length=1, max_length=50, example="John", description="User's first name")
    last_name: str = Field(..., min_length=1, max_length=50, example="Doe", description="User's last name")
    phone: str = Field(..., min_length=11, max_length=11, example="09123456789", 
                      description="Iranian phone number starting with 09, 11 digits")
    role: UserRole = Field(..., example=UserRole.CUSTOMER, description="User role")

    @field_validator("phone")
    def validate_phone(cls, v):
        if not v.startswith("09"):
            raise ValueError("Phone number must start with '09'")
        return v

class UserCreate(UserBase):
    password: str = Field(
        ..., example="strongpassword123",
        min_length=8, max_length=255,
        description="Password with minimum 8 characters")

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
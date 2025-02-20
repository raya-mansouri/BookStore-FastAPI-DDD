from fastapi import HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import pytz
from app.exceptions import InvalidFieldError
from app.reservation.domain.object_values import ReservationStatus
from app.user.domain.object_values import SubscriptionModel


class Customer:
    """
    Represents a customer with attributes like user ID, subscription model,
    subscription expiration date, and wallet balance.
    """

    id: int
    user_id: int
    subscription_model: str
    subscription_end_time: datetime
    wallet_money_amount: int

    def __init__(
        self,
        user_id: int,
        subscription_model: str,
        subscription_end_time: datetime,
        wallet_money_amount: int,
    ):
        self.user_id = user_id
        self.subscription_model = subscription_model
        self.subscription_end_time = subscription_end_time
        self.wallet_money_amount = wallet_money_amount

    def __validate(
        self, id: int, user_id: int, subscription_model: str, wallet_money_amount: int
    ):
        """Validates customer attributes to ensure correctness."""
        if not isinstance(user_id, int) or user_id <= 0:
            raise InvalidFieldError("User ID must be a positive integer.")

        if subscription_model not in SubscriptionModel:
            raise InvalidFieldError(
                "Subscription model must be one of: 'free', 'plus', 'premium'."
            )

        if not isinstance(wallet_money_amount, int) or wallet_money_amount < 0:
            raise InvalidFieldError(
                "Wallet money amount must be a non-negative integer."
            )

    def __setattr__(self, name, value):
        """Custom attribute setter to enforce validation on certain fields."""
        if name == "user_id" and (not isinstance(value, int) or value <= 0):
            raise InvalidFieldError("User ID must be a positive integer.")
        elif name == "wallet_money_amount" and (
            not isinstance(value, int) or value < 0
        ):
            raise InvalidFieldError(
                "Wallet money amount must be a non-negative integer."
            )
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name):
        """Handles attribute access for undefined attributes."""
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def validate(self):
        """Triggers validation for customer attributes."""
        self.__validate(
            self.id, self.user_id, self.subscription_model, self.wallet_money_amount
        )

    def charge_wallet(self, amount: int):
        """Increases the wallet balance by the given amount."""
        self.wallet_money_amount += amount

    def upgrade_subscription(self, new_model: str):
        """Handles upgrading the customer's subscription model."""
        pre_wallet_amount = self.wallet_money_amount
        pre_subscription_model = self.subscription_model
        iran_timezone = pytz.timezone("Asia/Tehran")
        now = datetime.now(iran_timezone)

        cost_mapping = {
            ("free", "plus"): 50000,
            ("plus", "premium"): 150000,
            ("free", "premium"): 200000,
        }
        duration = timedelta(days=30)

        cost = cost_mapping.get((pre_subscription_model, new_model))
        if cost is None:
            raise ValueError("Invalid subscription upgrade path")

        if pre_wallet_amount < cost:
            raise HTTPException(status_code=400, detail="Insufficient wallet balance")

        self.wallet_money_amount -= cost
        self.subscription_model = new_model
        self.subscription_end_time = now + duration

    def deduct_from_wallet(self, amount):
        """Deducts a specified amount from the wallet balance."""
        self.wallet_money_amount -= amount


from typing import Optional
from enum import Enum


class CustomerBase(BaseModel):
    """Base schema for customer data."""

    user_id: int = Field(..., description="User ID of the customer", example=1)
    subscription_model: str = Field(
        "free", description="Customer's subscription model", example="free"
    )
    subscription_end_time: Optional[datetime] = Field(
        None, description="Subscription end time", example="2023-12-31T23:59:59"
    )
    wallet_money_amount: int = Field(0, description="Amount in wallet", example=10000)


class CustomerCreate(CustomerBase):
    """Schema for creating a new customer."""

    pass


class CustomerUpdate(BaseModel):
    """Schema for updating customer details."""

    subscription_model: Optional[str] = Field(
        None, description="New subscription model", example="premium"
    )
    subscription_end_time: Optional[datetime] = Field(
        None, description="Updated subscription end time", example="2024-12-31T23:59:59"
    )
    wallet_money_amount: Optional[int] = Field(
        None, description="Updated wallet balance", example=20000
    )


class CustomerOut(CustomerBase):
    """Schema for returning customer data."""

    id: int = Field(..., description="Customer ID", example=1)

    class Config:
        orm_mode = True


class Reservation:
    """Represents a book reservation."""

    id: int
    customer_id: int
    book_id: int
    start_of_reservation: datetime
    end_of_reservation: datetime
    status: ReservationStatus
    price: int

    def __init__(
        self,
        customer_id: int,
        book_id: int,
        start_of_reservation: datetime,
        end_of_reservation: datetime,
        status: ReservationStatus,
        price: int,
    ):
        self.customer_id = customer_id
        self.book_id = book_id
        self.start_of_reservation = start_of_reservation
        self.end_of_reservation = end_of_reservation
        self.status = status
        self.price = price


class ReservationCreateSchema(BaseModel):
    """Schema for creating a book reservation."""

    book_id: int = Field(..., description="ID of the book to reserve")
    days: int = Field(..., gt=0, le=15, description="Number of reservation days")


class ReservationResponseSchema(BaseModel):
    """Schema for reservation response."""

    id: int
    customer_id: int
    book_id: int
    start_of_reservation: datetime
    end_of_reservation: datetime
    status: str


class QueueResponseSchema(BaseModel):
    """Schema for returning queue position in case of unavailable books."""

    customer_id: int
    book_id: int
    queue_position: int

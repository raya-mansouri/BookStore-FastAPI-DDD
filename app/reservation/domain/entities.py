from fastapi import HTTPException
from pydantic import BaseModel, Field
from datetime import datetime, timedelta

import pytz
from app.exceptions import InvalidFieldError
from app.reservation.domain.object_values import ReservationStatus
from app.user.domain.object_values import SubscriptionModel


class Customer:
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
        subscription_end_time = subscription_end_time
        self.wallet_money_amount = wallet_money_amount

    def __validate(
        self, id: int, user_id: int, subscription_model: str, wallet_money_amount: int
    ):
        if not isinstance(user_id, int) or user_id <= 0:
            raise InvalidFieldError("User ID must be a positive integer.")

        if subscription_model not in SubscriptionModel:
            raise InvalidFieldError(
                "subscription_model must be one of: 'free', 'plus', 'premium'."
            )

        if not isinstance(wallet_money_amount, int) or wallet_money_amount < 0:
            raise InvalidFieldError(
                "Wallet money amount must be a non-negative integer."
            )

    def __setattr__(self, name, value):
        # Validate before setting any attribute
        if name == "user_id" and (not isinstance(value, int) or value <= 0):
            raise InvalidFieldError("User ID must be a positive integer.")
        # elif name == "subscription_model":
        #     if value not in list(SubscriptionModel._value2member_map_):
        #         raise InvalidFieldError("subscription_model must be one of: 'free', 'plus', 'premium'.")
        #     else:
        #         value = SubscriptionModel(value)
        elif name == "wallet_money_amount" and (
            not isinstance(value, int) or value < 0
        ):
            raise InvalidFieldError(
                "Wallet money amount must be a non-negative integer."
            )
        else:
            super().__setattr__(name, value)

    def __getattr__(self, name):
        # Handle attribute access if it does not exist
        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'"
        )

    def validate(self):
        # Re-run the validation logic, could be used for revalidation after changing values
        self.__validate(
            self.id, self.user_id, self.subscription_model, self.wallet_money_amount
        )

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
        iran_timezone = pytz.timezone("Asia/Tehran")
        now = datetime.now(iran_timezone)

        cost_mapping = {
            ("free", "plus"): 50000,
            ("plus", "premium"): 150000,
            ("free", "premium"): 200000,
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


class CustomerBase(BaseModel):
    user_id: int = Field(
        ..., description="The ID of the user associated with the customer", example=1
    )
    subscription_model: str = Field(
        "free",
        description="Subscription model of the customer",
        example="free",
    )
    subscription_end_time: Optional[datetime] = Field(
        None, description="End time of the subscription", example="2023-12-31T23:59:59"
    )
    wallet_money_amount: int = Field(
        0, description="Amount of money in the wallet", example=10000
    )


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    subscription_model: Optional[str] = Field(
        None, description="Subscription model of the customer", example="premium"
    )
    subscription_end_time: Optional[datetime] = Field(
        None, description="End time of the subscription", example="2024-12-31T23:59:59"
    )
    wallet_money_amount: Optional[int] = Field(
        None, description="Amount of money in the wallet", example=20000
    )


class CustomerOut(CustomerBase):
    id: int = Field(
        ..., description="The unique identifier for the customer", example=1
    )

    class Config:
        orm_mode = True


class Reservation:
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
    book_id: int = Field(..., description="ID of the book to reserve")
    days: int = Field(..., gt=0, le=15, description="Number of days for reservation")


class ReservationResponseSchema(BaseModel):
    id: int
    customer_id: int
    book_id: int
    start_of_reservation: datetime
    end_of_reservation: datetime
    status: str


class QueueResponseSchema(BaseModel):
    customer_id: int
    book_id: int
    queue_position: int

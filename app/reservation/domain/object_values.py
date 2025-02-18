from enum import Enum


class SubscriptionModel(str, Enum):
    free = "free"
    plus = "plus"
    premium = "premium"


class ReservationStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"

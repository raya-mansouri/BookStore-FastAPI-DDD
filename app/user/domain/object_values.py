from enum import Enum


class SubscriptionModel(Enum):
    FREE = "free"
    PLUS = "plus"
    Premium = "premium"


class UserRole(str, Enum):
    ADMIN = "admin"
    CUSTOMER = "customer"
    AUTHOR = "author"

from enum import Enum

# Enum representing different subscription models
class SubscriptionModel(Enum):
    FREE = "free"  # Free subscription model
    PLUS = "plus"  # Plus subscription model
    PREMIUM = "premium"  # Premium subscription model

# Enum representing different user roles
class UserRole(str, Enum):
    ADMIN = "admin"  # Admin user role
    CUSTOMER = "customer"  # Customer user role
    AUTHOR = "author"  # Author user role

from enum import Enum


# Enum class to define subscription models for users
class SubscriptionModel(str, Enum):
    free = "free"  # Represents the free subscription model
    plus = "plus"  # Represents the plus subscription model
    premium = "premium"  # Represents the premium subscription model


# Enum class to define reservation statuses
class ReservationStatus(Enum):
    PENDING = "pending"  # Represents a reservation that is pending
    ACTIVE = "active"  # Represents a reservation that is currently active
    COMPLETED = "completed"  # Represents a reservation that has been completed

from enum import Enum


class Gender(Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"


class BookingStatus(Enum):
    PENDING = "pending"  # Booking created but not paid yet
    ACTIVE = "active"  # Paid and confirmed
    CANCELLED = "cancelled"  # User cancelled, but maybe not refunded
    REFUNDED = "refunded"  # Cancelled and money returned


class EventStatus(Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class PaymentMethod(Enum):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"

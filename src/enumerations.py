from enum import Enum


class Gender(Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "O"


class BookingStatus(Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class EventStatus(Enum):
    ACTIVE = "active"
    CANCELLED = "cancelled"


class PaymentMethod(Enum):
    CASH = "cash"
    CARD = "card"
    TRANSFER = "transfer"

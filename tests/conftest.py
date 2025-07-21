import pytest


@pytest.fixture(scope="function")
def users():
    return [
        {
            "first_name": "Maria",
            "last_name": "Papadopoulou",
            "password": "mN7bV8cX9zQ1",
            "date_of_birth": "1992-05-17",
            "gender": "F",
            "email": "maria@example.com",
            "phone": "6901234567",
            "user_bookings": None,
            "user_cancellations": None,
            "address": None,
        },
        {
            "first_name": "Giorgos",
            "last_name": "Nikolaidis",
            "password": "q1W2e3R4t5Y6",
            "date_of_birth": "1987-11-03",
            "gender": "M",
            "email": "giorgos@example.gr",
            "phone": "6977654321",
            "user_bookings": None,
            "user_cancellations": None,
            "address": None,
        },
    ]

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
            "address": {
                "street": "45 Thessaloniki Ave",
                "city": "Thessaloniki",
                "postal_code": "54622",
                "country": "Greece",
                "user_id": 2,
            },
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
            "address": {
                "street": "123 Athens St",
                "city": "Athens",
                "postal_code": "10558",
                "country": "Greece",
                "user_id": 1,
            },
        },
    ]


@pytest.fixture(scope="function")
def events():
    return [
        {
            "name": "Beach Getaway",
            "description": "Relaxing weekend trip to the beach.",
            "status": "active",
            "start_location": "Athens",
            "destination": "Santorini",
            "departure_time_to": "2025-08-15T08:00:00+03:00",
            "arrival_time_to": "2025-08-15T12:00:00+03:00",
            "departure_time_return": "2025-08-17T17:00:00+03:00",
            "arrival_time_return": "2025-08-17T21:00:00+03:00",
            "event_start_date": "2025-08-15",
            "event_end_date": "2025-08-17",
            "reserved_seats": 15,
            "total_seats": 30,
            "price_per_seat": "120.00",
        },
        {
            "name": "Mountain Hiking",
            "description": "Explore Mount Olympus with experienced guides.",
            "status": "active",
            "start_location": "Thessaloniki",
            "destination": "Mount Olympus",
            "departure_time_to": "2025-09-10T07:00:00+03:00",
            "arrival_time_to": "2025-09-10T11:00:00+03:00",
            "departure_time_return": "2025-09-12T16:00:00+03:00",
            "arrival_time_return": "2025-09-12T20:00:00+03:00",
            "event_start_date": "2025-09-10",
            "event_end_date": "2025-09-12",
            "reserved_seats": 10,
            "total_seats": 25,
            "price_per_seat": "150.00",
        },
    ]


@pytest.fixture(scope="function")
def bookings():
    return [
        {
            "user_id": 1,
            "event_id": 1,
            "unit_price": "120.00",
            "seats": 2,
            "amount_paid": "240.00",
            "payment_method": "card",
            "status": "active",
        },
        {
            "user_id": 2,
            "event_id": 1,
            "unit_price": "120.00",
            "seats": 1,
            "amount_paid": "120.00",
            "payment_method": "card",
            "status": "active",
        },
        {
            "user_id": 1,
            "event_id": 2,
            "unit_price": "120.00",
            "seats": 3,
            "amount_paid": "360.00",
            "payment_method": "transfer",
            "status": "active",
        },
        {
            "user_id": 2,
            "event_id": 2,
            "unit_price": "150.00",
            "seats": 2,
            "amount_paid": "300.00",
            "payment_method": "card",
            "status": "active",
        },
        {
            "user_id": 3,  # not existing user
            "event_id": 2,
            "unit_price": "150.00",
            "seats": 1,
            "amount_paid": "150.00",
            "payment_method": "cash",
            "status": "active",
        },
        {
            "user_id": 2,
            "event_id": 3,  # not existing event
            "unit_price": "150.00",
            "seats": 1,
            "amount_paid": "150.00",
            "payment_method": "transfer",
            "status": "active",
        },
    ]


@pytest.fixture(scope="function")
def cancellations():
    return [
        {
            "user_id": 1,
            "booking_id": 3,  # it will cancel the booking to the second event(booking 3)
            "cancellation_time": "2025-07-21T15:30:00+03:00",
            "refund_amount": "360.00",
            "reason": "Change of plans",
        }
    ]

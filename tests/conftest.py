# tests/conftest.py
from itertools import cycle

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from database.engine import engine  # adjust import as needed
from database.schema import AddressORM, BookingORM, CancellationORM, EventORM, UserORM
from models.schema import (
    AddressModel,
    BookingModel,
    CancellationModel,
    EventModel,
    UserModel,
)


@pytest.fixture(scope="function")
def session():
    session = Session(engine, autoflush=False, expire_on_commit=True)
    try:
        yield session
        print(
            "Finished inserting users, events and bookings and cancellations...\n"
            "Closing session without commiting transactions..."
        )
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def users():
    return [
        {
            "id": 1,
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
                "user_id": 1,
            },
        },
        {
            "id": 2,
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
                "user_id": 2,
            },
        },
    ]


@pytest.fixture(scope="function")
def users_models(users):
    return [UserModel.model_validate(d) for d in users]


@pytest.fixture(scope="function")
def addresses_models(users):
    return [AddressModel.model_validate(d["address"]) for d in users]


# In reality ids will be provided from the database during insertion.
# If so, Pydantic models exclude them during serialization but for testing purposes are provided hardcoded


@pytest.fixture(scope="function")
def users_orm(users_models):
    orms = []
    for model in users_models:
        orm = UserORM.from_attributes(model)
        orm.id_ = model.id_
        orms.append(orm)
    return orms


@pytest.fixture(scope="function")
def addresses_orm(addresses_models):
    orms = []
    for model in addresses_models:
        orm = AddressORM.from_attributes(model)
        orm.id_ = model.id_
        orms.append(orm)
    return orms


@pytest.fixture(scope="function")
def users_with_address_orm(users_models):
    orms = []
    for model in users_models:
        orm = UserORM.from_attributes(model)
        orm.address = AddressORM.from_attributes(model.address)
        orm.id_ = model.id_
        orms.append(orm)
    return orms


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


@pytest.fixture(scope="function")
def populated_db(users, events, bookings, cancellations):
    session = Session(bind=engine)

    try:
        print("Starting inserting users, events and bookings and cancellations...")
        # Add Users & Addresses
        for u_dict in users:
            model = UserModel.model_validate(u_dict)
            orm = UserORM.from_attributes(model)
            orm.address = AddressORM.from_attributes(model.address)
            session.add(orm)
        session.flush()
        user_ids = cycle(session.scalars(sa.select(UserORM.id_)).all())

        # Add Events
        for e_dict in events:
            model = EventModel.model_validate(e_dict)
            orm = EventORM.from_attributes(model)
            session.add(orm)
        session.flush()
        event_ids = cycle(session.scalars(sa.select(EventORM.id_)).all())

        # Add Bookings
        user_book_id_combs = []
        for b_dict in bookings:
            model = BookingModel.model_validate(b_dict)
            orm = BookingORM.from_attributes(model)
            user_id, event_id = next(user_ids), next(event_ids)
            orm.user_id = user_id
            orm.event_id = event_id
            session.add(orm)
            session.flush()
            user_book_id_combs.append((user_id, orm.id_))

        # Add Cancellations
        for c_dict in cancellations:
            model = CancellationModel.model_validate(c_dict)
            orm = CancellationORM.from_attributes(model)
            user_id, booking_id = user_book_id_combs.pop(0)
            orm.user_id = user_id
            orm.booking_id = booking_id
            session.add(orm)
        session.flush()

        yield session  # Pass control to test

    finally:
        print(
            "Finished inserting users, events and bookings and cancellations...\n"
            "Closing session without commiting transactions..."
        )
        session.rollback()  # Undo all changes
        session.close()

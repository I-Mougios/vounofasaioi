# tests/conftest.py
import pytest
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


# ======== USERS & ADDRESSES========
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


# ======== EVENTS ========
@pytest.fixture(scope="function")
def events():
    return [
        {
            "id": 1,
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
            "id": 2,
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
def events_models(events):
    return [EventModel.model_validate(d) for d in events]


@pytest.fixture(scope="function")
def events_orm(events_models):
    orms = []
    for model in events_models:
        orm = EventORM.from_attributes(model)
        orm.id_ = model.id_
        orms.append(orm)
    return orms


# ======== BOOKINGS ========


@pytest.fixture(scope="function")
def bookings():
    return [
        {
            "id": 1,
            "user_id": 1,
            "event_id": 1,
            "unit_price": "120.00",
            "seats": 2,
            "amount_paid": "240.00",
            "payment_method": "card",
            "status": "active",
        },
        {
            "id": 2,
            "user_id": 2,
            "event_id": 1,
            "unit_price": "120.00",
            "seats": 1,
            "amount_paid": "120.00",
            "payment_method": "cash",
            "status": "active",
        },
        {
            "id": 3,
            "user_id": 1,
            "event_id": 2,
            "unit_price": "120.00",
            "seats": 3,
            "amount_paid": "360.00",
            "payment_method": "transfer",
            "status": "active",
        },
        {
            "id": 4,
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
def bookings_models(bookings):
    return [BookingModel.model_validate(d) for d in bookings]


@pytest.fixture(scope="function")
def bookings_orm(bookings_models):
    orms = []
    for model in bookings_models:
        orm = BookingORM.from_attributes(model)
        orm.id_ = model.id_
        orms.append(orm)
    return orms


# ======== CANCELLATIONS ========
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
def cancellations_models(cancellations):
    return [CancellationModel.model_validate(d) for d in cancellations]


@pytest.fixture(scope="function")
def cancellations_orm(cancellations_models):
    orms = []
    for model in cancellations_models:
        orm = CancellationORM.from_attributes(model)
        orm.id_ = model.id_
        orms.append(orm)
    return orms


@pytest.fixture(scope="function")
def populated_db(session, users_orm, events_orm, bookings_orm, cancellations_orm):
    print("Starting inserting users, events and bookings and cancellations...")
    session.add_all(users_orm)
    session.add_all(events_orm)
    session.add_all(bookings_orm)
    session.add_all(cancellations_orm)

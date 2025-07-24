# tests/test_schema.py
# from datetime import date, datetime, timedelta
# from decimal import Decimal
# from zoneinfo import ZoneInfo
#
# import pytest
# import sqlalchemy as sa
# from sqlalchemy.exc import IntegrityError, OperationalError
# from sqlalchemy.orm import Session
#
# from database.engine import engine
# from database.schema import AddressORM, BookingORM, CancellationORM, EventORM, UserORM
# from models.schema import (
#     AddressModel,
#     BookingModel,
#     CancellationModel,
#     EventModel,
#     UserModel,
# )
# from src.enumerations import Gender


# def test_basic_fields_validation(users):
#     user1, _ = users
#     m1 = UserModel.model_validate(user1)
#     assert isinstance(m1.date_of_birth, date)
#     assert m1.date_of_birth == date(1992, 5, 17)
#     assert isinstance(m1.address, AddressModel)
#     assert m1.address.city == "Thessaloniki"
#     assert m1.gender == Gender.FEMALE
#     assert m1.gender.value == "F"
#     assert isinstance(m1.gender, Gender)
#
#
# def test_enum_and_custom_date_assignment(users):
#     user1, _ = users
#     m1 = UserModel.model_validate(user1)
#     m1.gender = "F"
#     m1.date_of_birth = "July 27, 1995"
#     assert m1.date_of_birth.year == 1995
#     assert m1.date_of_birth.month == 7
#
#
# def test_dayfirst_date_parsing(users):
#     user1, _ = users
#     m1 = UserModel.model_validate(user1)
#     m1.date_of_birth = "07/06/1995"  # dd/mm/yyyy
#     assert m1.date_of_birth.day == 7
#
#
# def test_athens_datetime_conversion_from_naive(users):
#     user1, _ = users
#     m1 = UserModel.model_validate(user1)
#     naive_now = datetime.now()
#     m1.updated_at = naive_now
#     assert m1.updated_at.tzinfo == ZoneInfo("Europe/Athens")
#     assert m1.updated_at.hour == (naive_now + timedelta(hours=3)).hour
#
#
# def test_athens_datetime_accepts_aware_datetime(users):
#     user1, _ = users
#     m1 = UserModel.model_validate(user1)
#     aware_now = datetime.now(tz=ZoneInfo("Europe/Athens"))
#     m1.updated_at = aware_now
#     assert m1.updated_at.hour == aware_now.hour
#
#
# def test_str_str_whitespace_strip(users):
#     user1, _ = users
#     m1 = UserModel.model_validate(user1)
#     m1.first_name = " John\t"
#     assert m1.first_name == "John"
#
#
# # ==========Test Database schema and relationships========
#
#
# def test_add_addresses_via_users(users):
#     user1, user2 = users
#     m1 = UserModel.model_validate(user1)
#     m2 = UserModel.model_validate(user2)
#     # Create the ORMs instances from Pydantic Models
#     u1 = UserORM.from_attributes(m1)
#     u2 = UserORM.from_attributes(m2)
#     a1 = AddressORM.from_attributes(m1.address)
#     a2 = AddressORM.from_attributes(m2.address)
#
#     # Insert addresses via the user
#     with Session(bind=engine) as session:
#         u1.address = a1
#         u2.address = a2
#         session.add(u1)
#         session.add(u2)
#         session.flush()
#         now = datetime.now()
#         addresses = list(session.query(AddressORM).all())
#         assert len(addresses) == 2
#         assert addresses[0].city == m1.address.city
#         assert u1.created_at.minute == now.minute
#
#
# def test_add_users_via_addresses(users):
#     user1, user2 = users
#     m1 = UserModel.model_validate(user1)
#     m2 = UserModel.model_validate(user2)
#     # Create the ORMs instances from Pydantic Models
#     u1 = UserORM.from_attributes(m1)
#     u2 = UserORM.from_attributes(m2)
#     a1 = AddressORM.from_attributes(m1.address)
#     a2 = AddressORM.from_attributes(m2.address)
#     # Let's insert the users through the addresses instances
#     with Session(bind=engine) as session:
#         a1.user = u1
#         a2.user = u2
#         session.add(a1)
#         session.add(a2)
#         session.flush()
#         users_result = list(session.query(UserORM).all())
#         assert len(users_result) == 2
#         assert users_result[0].first_name == m1.first_name
#
#
# def test_users_address_on_delete_cascade(users):
#     user1, user2 = users
#     m1 = UserModel.model_validate(user1)
#     m2 = UserModel.model_validate(user2)
#     # Create the ORMs instances from Pydantic Models
#     u1 = UserORM.from_attributes(m1)
#     u2 = UserORM.from_attributes(m2)
#     a1 = AddressORM.from_attributes(m1.address)
#     a2 = AddressORM.from_attributes(m2.address)
#     # Let's insert the users through the addresses instances
#     # Insert addresses via the user
#     with Session(bind=engine, expire_on_commit=True) as session:
#         u1.address = a1
#         u2.address = a2
#         session.add(u1)
#         session.add(u2)
#         session.commit()
#
#         session.delete(u1)  # it executes before deletion select statement due to expire on commit
#         result = list(session.query(AddressORM).all())
#         assert len(result) == 1
#         session.delete(u2)
#         session.commit()
#
#
# def test_user_bookings_relationship(users, bookings):
#     user1, _ = users
#     booking1, *_ = bookings
#
#     # Create user and address
#     m1 = UserModel.model_validate(user1)
#     u1 = UserORM.from_attributes(m1)
#     a1 = AddressORM.from_attributes(m1.address)
#     u1.address = a1
#
#     # Create booking
#     b1_model = BookingModel.model_validate(booking1)
#     b1 = BookingORM.from_attributes(b1_model)
#     with Session(bind=engine) as session:
#         session.add(u1)
#         session.flush()
#         with pytest.raises(IntegrityError) as exc_info:
#             session.add(b1)
#             session.flush()
#         assert (
#             "CONSTRAINT `test_bookings_ibfk_1` FOREIGN KEY (`user_id`)"
#             " REFERENCES `test_users` (`id`) ON DELETE SET NULL)')"
#         ) in exc_info.value.args[0]
#
#
# def test_user_bookings_event_chain_relationship(users, bookings):
#     user1, _ = users
#     booking1, *_ = bookings
#
#     # Create user and address
#     m1 = UserModel.model_validate(user1)
#     u1 = UserORM.from_attributes(m1)
#     a1 = AddressORM.from_attributes(m1.address)
#     u1.address = a1
#
#     # Create booking
#     b1_model = BookingModel.model_validate(booking1)
#     b1 = BookingORM.from_attributes(b1_model)
#     with Session(bind=engine) as session:
#         session.add(u1)
#         session.flush()
#
#         b1.user_id = u1.id  # Now that my user get id I can associate it with the booking
#         with pytest.raises(IntegrityError) as exc_info:
#             session.add(b1)
#             session.flush()
#
#         assert (
#             "CONSTRAINT `test_bookings_ibfk_2` FOREIGN KEY (`event_id`)"
#             " REFERENCES `test_events` (`id`) ON DELETE CASCADE)')"
#         ) in exc_info.value.args[0]
#
#
# def test_user_event_booking_chain_correct_insertion(users, bookings, events):
#     user1, _ = users
#     booking1, *_ = bookings
#     event1, _ = events
#     # Create user and address
#     m1 = UserModel.model_validate(user1)
#     u1 = UserORM.from_attributes(m1)
#     a1 = AddressORM.from_attributes(m1.address)
#     u1.address = a1
#     # Create booking
#     b1_model = BookingModel.model_validate(booking1)
#     b1 = BookingORM.from_attributes(b1_model)
#     # Create event
#     e1_model = EventModel.model_validate(event1)
#     e1 = EventORM.from_attributes(e1_model)
#     with Session(bind=engine) as session:
#         session.add(u1)
#         session.add(e1)
#         session.flush()
#
#         b1.user_id = u1.id
#         b1.event_id = e1.id
#         session.add(b1)
#         session.flush()
#
#         booking_records = list(session.query(BookingORM).all())
#         assert len(booking_records) == 1
#         assert booking_records[0].event_id == e1.id
#         assert booking_records[0].user_id == u1.id
#
#
# def test_user_event_booking_cancellation_chain(users, bookings, events, cancellations):
#     user1, _ = users
#     booking1, *_ = bookings
#     event1, *_ = events
#     cancellation1, *_ = cancellations
#     # Create user and address
#     m1 = UserModel.model_validate(user1)
#     u1 = UserORM.from_attributes(m1)
#     a1 = AddressORM.from_attributes(m1.address)
#     u1.address = a1
#     # Create event
#     e1_model = EventModel.model_validate(event1)
#     e1 = EventORM.from_attributes(e1_model)
#     # Create cancellation
#     c1_model = CancellationModel.model_validate(cancellation1)
#     c1 = CancellationORM.from_attributes(c1_model)
#     with Session(bind=engine) as session:
#         session.add(u1)
#         session.add(e1)
#         session.flush()
#         with pytest.raises(IntegrityError) as exc_info:
#             session.add(c1)
#             session.flush()
#
#         assert (
#             "CONSTRAINT `test_cancellations_ibfk_2` FOREIGN KEY (`booking_id`)"
#             " REFERENCES `test_bookings` (`id`) ON DELETE CASCADE"
#         ) in exc_info.value.args[0]
#
#
# def test_user_event_booking_cancellation_correct_insertion(users, bookings, events, cancellations):
#     user1, _ = users
#     booking1, *_ = bookings
#     event1, *_ = events
#     cancellation1, *_ = cancellations
#     # Create user and address
#     m1 = UserModel.model_validate(user1)
#     u1 = UserORM.from_attributes(m1)
#     a1 = AddressORM.from_attributes(m1.address)
#     u1.address = a1
#     # Create booking
#     b1_model = BookingModel.model_validate(booking1)
#     b1 = BookingORM.from_attributes(b1_model)
#     # Create event
#     e1_model = EventModel.model_validate(event1)
#     e1 = EventORM.from_attributes(e1_model)
#     # Create cancellation
#     c1_model = CancellationModel.model_validate(cancellation1)
#     c1 = CancellationORM.from_attributes(c1_model)
#     with Session(bind=engine) as session:
#         session.add(u1)
#         session.add(e1)
#         session.flush()
#
#         b1.user_id = u1.id
#         b1.event_id = e1.id
#         session.add(b1)
#         session.flush()
#
#         c1.user_id = u1.id
#         c1.booking_id = b1.id
#         session.add(c1)
#         session.flush()
#
#         cancellation = list(session.query(CancellationORM).all())[0]
#         assert cancellation.booking.event_id == e1.id
#         assert cancellation.booking.id == b1.id
#         assert cancellation.user.id == u1.id
#
#
# def test_chained_on_delete_cascade_when_removing_an_event(users, bookings, events, cancellations):
#     user1, _ = users
#     booking1, *_ = bookings
#     event1, *_ = events
#     cancellation1, *_ = cancellations
#     # Create user and address
#     m1 = UserModel.model_validate(user1)
#     u1 = UserORM.from_attributes(m1)
#     a1 = AddressORM.from_attributes(m1.address)
#     u1.address = a1
#     # Create booking
#     b1_model = BookingModel.model_validate(booking1)
#     b1 = BookingORM.from_attributes(b1_model)
#     # Create event
#     e1_model = EventModel.model_validate(event1)
#     e1 = EventORM.from_attributes(e1_model)
#     # Create cancellation
#     c1_model = CancellationModel.model_validate(cancellation1)
#     c1 = CancellationORM.from_attributes(c1_model)
#     with Session(bind=engine) as session:
#         # Insert the user
#         session.add(u1)
#         session.add(e1)
#         session.flush()
#         # Insert the booking
#         b1.user_id = u1.id
#         b1.event_id = e1.id
#         session.add(b1)
#         session.flush()
#         # Insert the cancellation
#         c1.user_id = u1.id
#         c1.booking_id = b1.id
#         session.add(c1)
#         session.flush()
#
#         # The deletion of the event will cascade the deletion of the booking
#         # which in turn will cascade the deletion of cancellation
#         session.delete(e1)
#
#         assert session.scalar(sa.select(sa.func.count(BookingORM.id_))) == 0
#         assert session.scalar(sa.select(sa.func.count(CancellationORM.id_))) == 0
#
#
# def test_populated_db_inserts(populated_db):
#     session = populated_db
#     # Check users count
#     user_count = session.query(UserORM).count()
#     assert user_count > 0
#
#     # Check events count
#     event_count = session.query(EventORM).count()
#     assert event_count > 0
#
#     # Check bookings count
#     booking_count = session.query(BookingORM).count()
#     assert booking_count > 0
#
#     # Check cancellations count
#     cancellation_count = session.query(CancellationORM).count()
#     assert cancellation_count > 0
#
#     # Verify a booking links to a user and event
#     booking = session.query(BookingORM).first()
#     assert booking.user is not None
#     assert booking.event is not None
#     assert (
#         isinstance(booking.amount_paid, Decimal) and booking.amount_paid.as_tuple().exponent == -2
#     )
#
#     # Verify a cancellation links to a booking and user
#     cancellation = session.query(CancellationORM).first()
#     assert cancellation.booking is not None
#     assert cancellation.user is not None
#
#
# def test_on_delete_set_null_relationships(populated_db):
#     session = populated_db
#
#     cancellations_result = session.query(CancellationORM).all()
#     assert len(cancellations_result) != 0
#     cancellation_user_id = cancellations_result.pop().user_id
#     session.execute(sa.delete(UserORM).where(UserORM.id_ == cancellation_user_id))
#
#     bookings_result = (
#         session.query(BookingORM).filter(BookingORM.user_id == None).all()  # noqa:  E711
#     )
#     cancellations_result = (
#         session.query(CancellationORM).filter(CancellationORM.user_id == None).all()  # noqa:  E711
#     )
#     assert len(bookings_result) != 0
#     assert len(cancellations_result) != 0
#
#
# def test_check_seats_before_insert(populated_db):
#     session = populated_db
#
#     event = session.query(EventORM).first()
#     booking = session.query(BookingORM).first()
#     new_booking = {}
#     for col in booking.columns():
#         new_booking[col.name] = getattr(booking, col.name, None)
#
#     for col in ["id", "created_at", "updated_at"]:
#         del new_booking[col]
#     available_seats = event.total_seats - event.reserved_seats
#     new_booking["seats"] = available_seats + 1
#     with pytest.raises(OperationalError) as operational_error:
#         booking_orm = BookingORM(**new_booking)
#         session.add(booking_orm)
#         session.flush()
#
#     assert "Not enough available seats for this event." in operational_error.value.args[0]

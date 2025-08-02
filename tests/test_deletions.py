# tests/test_deletions.py
import sqlalchemy as sa
from icecream import ic

from configs import DBConfig
from database.schema import BookingORM, CancellationORM, EventORM, PaymentORM, UserORM

if DBConfig.globals.get("icecream_enabled", False):
    ic.enable()
else:
    ic.disable()


def test_user_deletion_sets_user_id_null_in_bookings_and_cancellations(session, populated_db):
    # Arrange: get user, related bookings and cancellations
    user = session.get(UserORM, 1)
    assert user is not None
    # user with id=1 have two bookings where booking.id is(1,3) and one cancellation on booking.id(3)
    session.delete(user)
    session.flush()

    # Assert
    bookings = session.query(BookingORM).filter(BookingORM.user_id.is_(None)).all()
    cancellations = session.query(CancellationORM).filter(CancellationORM.user_id.is_(None)).all()

    assert len(bookings) > 0  # At least one booking was affected
    assert len(cancellations) > 0  # At least one cancellation was affected


def test_booking_deletion_cascades_to_payment_and_cancellation(session, populated_db):
    # booking with id=3 is related to a cancellation(id=1), payment(id=3)
    booking = session.get(BookingORM, 3)
    num_of_cancellations_before_booking_deletion = session.scalar(
        sa.select(sa.func.count(CancellationORM.id_))
    )

    assert booking is not None
    assert booking.payment is not None
    assert booking.cancellation is not None

    # Act
    session.delete(booking)
    session.flush()
    num_of_cancellations_after_booking_deletion = session.scalar(
        sa.select(sa.func.count(CancellationORM.id_))
    )

    # Assert
    assert session.get(PaymentORM, 3) is None
    assert (
        num_of_cancellations_after_booking_deletion < num_of_cancellations_before_booking_deletion
    )


def test_event_deletion_cascades_to_bookings_and_children(session, populated_db):
    # Event with id=2 is associated with booking(3,4) and booking.id=3 with cancellation.id=1
    event = session.get(EventORM, 2)
    assert event is not None

    # Act (two bookings(1,2) are associated with the deleted event)
    session.delete(event)
    session.flush()

    # Assert bookings deleted
    bookings = session.query(BookingORM).filter_by(event_id=2).all()
    assert not bookings

    # Check related payments and cancellations gone too
    payment = session.query(PaymentORM).filter(PaymentORM.booking_id.in_([3, 4])).all()
    assert not payment

    cancellations = (
        session.query(CancellationORM).filter(CancellationORM.booking_id.in_([3, 4])).all()
    )
    assert not cancellations


def test_payment_deletion_does_not_affect_booking(session, populated_db):
    payment = session.get(PaymentORM, 1)
    assert payment is not None
    booking_id = payment.booking_id

    session.delete(payment)
    session.flush()

    booking = session.get(BookingORM, booking_id)
    assert booking is not None


def test_cancellation_deletion_does_not_affect_booking(session, populated_db):
    # Arrange
    cancellation = session.query(CancellationORM).filter_by(booking_id=3).one_or_none()
    assert cancellation is not None
    booking = session.get(BookingORM, cancellation.booking_id)
    assert booking is not None
    booking_id = booking.id

    # Act
    session.delete(cancellation)
    session.flush()

    # Assert
    remaining_booking = session.get(BookingORM, booking_id)
    assert remaining_booking is not None
    assert remaining_booking.id_ == booking_id
    assert remaining_booking.cancellation is None


def test_booking_deletion_does_not_affect_event(session, populated_db):
    # Arrange
    booking = session.get(BookingORM, 1)
    assert booking is not None
    event_id = booking.event_id

    event = session.get(EventORM, event_id)
    assert event is not None

    # Act
    session.delete(booking)
    session.flush()

    # Assert
    remaining_event = session.get(EventORM, event_id)
    assert remaining_event is not None
    assert remaining_event.id_ == event_id

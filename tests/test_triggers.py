# tests/test_deletions.py
import pytest
import sqlalchemy as sa
from icecream import ic

from configs import DBConfig
from database.schema import BookingORM, EventORM

if DBConfig.globals.get("icecream_enabled", False):
    ic.enable()
else:
    ic.disable()


def test_check_seats_before_insert(session, populated_db):
    # Arrange
    available_seats = session.execute(
        sa.select((EventORM.total_seats - EventORM.reserved_seats).label("available_seats")).where(
            EventORM.id_ == 1
        )
    ).scalar_one()

    prev_booking = (
        session.execute(sa.select(BookingORM).where(BookingORM.event_id == 1)).scalars().first()
    )

    new_booking = BookingORM.from_attributes(prev_booking)
    new_booking.seats = available_seats + 1  # force overbooking

    # Act & Assert
    with pytest.raises(sa.exc.OperationalError, match="Not enough available seats for this event."):
        session.add(new_booking)
        session.flush()


def test_increment_reserved_seats_after_insert(session, populated_db, events_orm):
    # Arrange
    reserved_seats_before = sorted(
        [(event.id, event.reserved_seats) for event in events_orm], key=lambda x: x[0]
    )
    reservations_per_event = session.execute(
        sa.select(BookingORM.event_id, sa.func.sum(BookingORM.seats))
        .group_by(BookingORM.event_id)
        .order_by(BookingORM.event_id)
    ).all()

    reserved_seats_after = session.execute(
        sa.select(EventORM.id_, EventORM.reserved_seats).order_by(EventORM.id_)
    ).fetchall()
    print(f"{reservations_per_event}")
    for (_, seats_before), (_, reservations), (_, seats_after) in zip(
        reserved_seats_before, reservations_per_event, reserved_seats_after
    ):
        assert (seats_before + reservations) == seats_after

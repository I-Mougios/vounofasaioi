import pytest
from sqlalchemy.exc import IntegrityError

from configs import DBConfig

bookings_name = DBConfig.tables.bookings
payments_name = DBConfig.tables.payments
cancellations_name = DBConfig.tables.cancellations


def test_bookings_without_users(session, events_orm, bookings_orm):
    session.add_all(events_orm)
    session.flush()

    with pytest.raises(IntegrityError) as e:
        session.add_all(bookings_orm)
        session.flush()

    assert f"CONSTRAINT `{bookings_name}_ibfk_1`" in str(e.value.args[0])


def test_bookings_without_events(session, users_orm, bookings_orm):
    session.add_all(users_orm)
    session.flush()

    with pytest.raises(IntegrityError) as e:
        session.add_all(bookings_orm)
        session.flush()

    assert f"CONSTRAINT `{bookings_name}_ibfk_2" in str(e.value.args[0])


def test_cancellation_without_booking(session, cancellations_orm):
    with pytest.raises(IntegrityError) as e:
        session.add_all(cancellations_orm)
        session.flush()

    assert f"CONSTRAINT `{cancellations_name}_ibfk_2" in str(e.value.args[0])


def test_payment_without_booking(session, payments_orm):
    with pytest.raises(IntegrityError) as e:
        session.add_all(payments_orm)
        session.flush()

    assert f"CONSTRAINT `{payments_name}_ibfk_1`" in str(e.value.args[0])

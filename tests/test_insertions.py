import itertools

from database.schema import BookingORM, EventORM


def test_events_with_id_provided(session, events_orm):
    session.add_all(events_orm)
    session.flush()
    assert events_orm.pop(0).id == 1
    assert events_orm.pop(0).id == 2


def test_events_autoincrement_id(session, events_models):
    events_orm = [EventORM.from_attributes(m) for m in events_models]
    session.add_all(events_orm)
    session.flush()
    event1 = events_orm.pop(0)
    event2 = events_orm.pop(0)
    assert event1.id == event2.id - 1


def test_bookings_with_id_provided(session, events_orm, users_orm, bookings_orm):
    session.add_all(events_orm)
    session.add_all(users_orm)
    session.flush()
    session.add_all(bookings_orm)
    session.flush()
    for i in range(1, len(bookings_orm) + 1):
        assert bookings_orm.pop(0).id == i


def test_bookings_autoincrement_id(session, events_orm, users_orm, bookings_models):
    session.add_all(events_orm)
    session.add_all(users_orm)
    session.flush()
    bookings_orm = [BookingORM.from_attributes(m) for m in bookings_models]
    session.add_all(bookings_orm)
    session.flush()
    for pair in itertools.pairwise(bookings_orm):
        assert pair[0].id == pair[1].id - 1


def test_payments_with_id_provided(session, events_orm, users_orm, bookings_orm, payments_orm):
    session.add_all(events_orm)
    session.add_all(users_orm)
    session.flush()
    session.add_all(bookings_orm)
    session.flush()
    session.add_all(payments_orm)
    session.flush()
    for i in range(1, len(payments_orm) + 1):
        assert payments_orm.pop(0).id == i


def test_payments_autoincrement_id(session, events_orm, users_orm, bookings_orm, payments_orm):
    session.add_all(events_orm)
    session.add_all(users_orm)
    session.flush()
    session.add_all(bookings_orm)
    session.flush()
    session.add_all(payments_orm)
    session.flush()
    for pair in itertools.pairwise(payments_orm):
        assert pair[0].id == pair[1].id - 1

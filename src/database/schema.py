# src/database/schema.py
from __future__ import annotations

import argparse
from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    TIMESTAMP,
    Date,
    Enum,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.base import Base, TimestampBase
from database.engine import DBConfig, engine
from src.enumerations import BookingStatus, EventStatus, Gender, PaymentMethod

users_name = DBConfig.tables.users
bookings_name = DBConfig.tables.bookings
cancellations_name = DBConfig.tables.cancellations
events_name = DBConfig.tables.events
addresses_name = DBConfig.tables.addresses

current_timestamp = text("CURRENT_TIMESTAMP")


class UserORM(TimestampBase):
    __tablename__ = users_name

    id_: Mapped[int] = mapped_column("id", Integer, autoincrement=True, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    date_of_birth: Mapped[datetime] = mapped_column(Date, nullable=False)
    gender: Mapped[Optional[Gender]] = mapped_column(Enum(Gender), nullable=True)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)

    # Aliased relationship attributes
    user_bookings: Mapped[list["BookingORM"]] = relationship(
        back_populates="user", lazy="select", passive_deletes=True
    )
    user_cancellations: Mapped[list["CancellationORM"]] = relationship(
        back_populates="user", lazy="select", passive_deletes=True
    )
    address: Mapped["AddressORM"] = relationship(
        back_populates="user",
        uselist=False,  # Unnecessary as SQLAlchemy can infer it for the annotation of LHS
        lazy="select",
        cascade="all, delete",
        passive_deletes=True,
    )


class BookingORM(TimestampBase):
    __tablename__ = bookings_name

    id_: Mapped[int] = mapped_column("id", Integer, autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{users_name}.id", ondelete="SET NULL"), nullable=True
    )
    event_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{events_name}.id", ondelete="CASCADE"), nullable=False
    )
    unit_price: Mapped[Decimal] = mapped_column(
        Numeric(7, 2, asdecimal=True), nullable=False, default=Decimal("0.00")
    )
    booking_time: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=current_timestamp
    )
    seats: Mapped[int] = mapped_column(Integer, nullable=False)

    # Payment fields
    amount_paid: Mapped[Decimal] = mapped_column(
        Numeric(7, 2, asdecimal=True), nullable=False, default=Decimal("0.00")
    )
    payment_method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), nullable=False)
    payment_time: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=current_timestamp
    )

    # Booking status
    status: Mapped[BookingStatus] = mapped_column(
        Enum(BookingStatus),
        nullable=False,
        default=BookingStatus.ACTIVE,
        server_default=text(f"'{BookingStatus.ACTIVE.value}'"),
    )
    refund_amount: Mapped[Decimal] = mapped_column(
        Numeric(7, 2, asdecimal=True), nullable=False, default=Decimal("0.00")
    )

    # Relationships
    user: Mapped["UserORM"] = relationship(back_populates="user_bookings", lazy="select")
    event: Mapped["EventORM"] = relationship(back_populates="bookings", lazy="select")
    cancellation: Mapped[Optional["CancellationORM"]] = relationship(
        back_populates="booking",
        uselist=False,
        lazy="select",
        cascade="all, delete",
        passive_deletes=True,
    )


class CancellationORM(TimestampBase):
    __tablename__ = DBConfig.tables.cancellations

    id_: Mapped[int] = mapped_column("id", Integer, autoincrement=True, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{users_name}.id", ondelete="SET NULL"), nullable=True
    )
    booking_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(f"{bookings_name}.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    cancellation_time: Mapped[datetime] = mapped_column(
        TIMESTAMP, nullable=False, server_default=current_timestamp
    )
    refund_amount: Mapped[Decimal] = mapped_column(
        Numeric(7, 2, asdecimal=True), nullable=False, default=Decimal("0.00")
    )
    reason: Mapped[str] = mapped_column(String(255), nullable=True)

    # Relationships
    user: Mapped["UserORM"] = relationship(
        back_populates="user_cancellations", lazy="select", passive_deletes=True
    )
    booking: Mapped["BookingORM"] = relationship(
        back_populates="cancellation", lazy="select", cascade="all, delete", passive_deletes=True
    )


class EventORM(TimestampBase):
    __tablename__ = DBConfig.tables.events

    id_: Mapped[int] = mapped_column("id", Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[EventStatus] = mapped_column(
        Enum(EventStatus),
        default=EventStatus.ACTIVE,
        server_default=text(f"'{EventStatus.ACTIVE.value}'"),
    )

    # Locations
    start_location: Mapped[str] = mapped_column(String(50), nullable=False)
    destination: Mapped[str] = mapped_column(String(50), nullable=False)

    # Travel times - to destination
    departure_time_to: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)
    arrival_time_to: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    # Travel times - return
    departure_time_return: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), nullable=False
    )
    arrival_time_return: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True), nullable=False)

    # Event date range
    event_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    event_end_date: Mapped[date] = mapped_column(Date, nullable=False)

    # Seats and pricing(Source of Truth)
    reserved_seats: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    total_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_seat: Mapped[Decimal] = mapped_column(Numeric(7, 2, asdecimal=True), nullable=False)

    # Relationships
    bookings: Mapped[list["BookingORM"]] = relationship(
        back_populates="event", lazy="select", cascade="all, delete", passive_deletes=True
    )


class AddressORM(Base):
    __tablename__ = DBConfig.tables.addresses

    id_: Mapped[int] = mapped_column("id", Integer, primary_key=True, autoincrement=True)
    street: Mapped[str] = mapped_column(String(100), nullable=False)
    city: Mapped[str] = mapped_column(String(50), nullable=False)
    postal_code: Mapped[str] = mapped_column(String(20), nullable=False)
    country: Mapped[str] = mapped_column(String(50), nullable=False)

    user_id: Mapped[int] = mapped_column(
        ForeignKey(f"{users_name}.id", ondelete="CASCADE"), nullable=False, unique=True
    )
    user: Mapped["UserORM"] = relationship(back_populates="address", lazy="select")


def reset_tables(tables_to_reset=None):
    metadata = Base.metadata

    metadata.tables
    if not tables_to_reset:
        # Reset all tables
        tables = list(metadata.tables.values())
    else:
        # Filter tables by name, ignoring invalid ones
        tables = [metadata.tables[t] for t in tables_to_reset if t in metadata.tables]
        if not tables:
            print(f"No matching tables found for: {tables_to_reset}")
            return

    print(f"Resetting tables: {', '.join(t.name for t in tables)}")

    # Drop tables
    metadata.drop_all(engine, tables=tables, checkfirst=True)
    # Create tables
    metadata.create_all(engine, tables=tables, checkfirst=True)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Reset tables by dropping and recreating.")
    parser.add_argument(
        "--tables", nargs="*", help="Names of tables to reset. If omitted, reset all tables."
    )
    args = parser.parse_args()
    reset_tables(args.tables)

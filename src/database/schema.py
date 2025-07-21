# src/database/schema.py
from __future__ import annotations

from sqlalchemy import Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime

from database.engine import engine, DBConfig
from database.base import TimestampBase, Base


class UserORM(TimestampBase):
    __tablename__ = DBConfig.tables.users

    id_: Mapped[int] = mapped_column("id", Integer, autoincrement=True, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    date_of_birth: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    email: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(50), nullable=False)

    # Aliased relationship attributes
    user_bookings: Mapped[list["BookingORM"]] = relationship(back_populates="user", lazy="selectin")
    user_cancellations: Mapped[list["CancellationORM"]] = relationship(
        back_populates="user", lazy="selectin"
    )


class BookingORM():
    pass

class CancellationORM():
    pass

class TripsORM():
    pass

if __name__ == "__main__":
    Base.metadata.drop_all(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine, checkfirst=True)


# src/database.py
from datetime import datetime
from sqlalchemy import event
from sqlalchemy import DDL

from sqlalchemy.dialects.mysql import TIMESTAMP
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """Parent class for all database models."""


class TimestampBase(Base):
    """
    Abstact(Parent class) for tables that have the created_at and updated_at column.
    This class ensures consistent UTC timestamping across all database operations, regardless of the server's local timezone.
    **Notes about the behaviour of the class**
     - All timestamps are automatically converted to UTC before being stored in the database
     - Timezone-aware handling ensures consistent behavior across different geographic locations
    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=func.now(), server_onupdate=func.now(), nullable=False
    )



def _repr(self):
    mapper = self.__class__.__mapper__
    key_values = [
        f"{column.key}={repr(getattr(self, column.key))}" for column in mapper.column_attrs
    ]
    return f"{self.__class__.__name__}({', '.join(key_values)})"


# --- Add ON UPDATE DDL to each concrete subclass ---
@event.listens_for(Base.metadata, "after_create")
def add_on_update_ddl(target, connection, **kw):
    for table in target.tables.values():
        if "updated_at" in table.c:
            ddl = DDL(
                f"ALTER TABLE {table.name} MODIFY updated_at "
                "TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
            )
            connection.execute(ddl)

Base.__repr__ = _repr

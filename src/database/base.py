# src/database.py
from datetime import datetime
from typing import Any

from sqlalchemy import DDL, TIMESTAMP, event, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

current_timestamp = text("CURRENT_TIMESTAMP")


class Base(DeclarativeBase):
    """Parent class for all database models."""

    @classmethod
    def sa_table(cls):
        return cls.__table__

    @classmethod
    def columns(cls):
        return cls.sa_table().c

    @classmethod
    def from_attributes(
        cls,
        obj: Any,
        include: list[str | tuple[str, "Base"] | tuple[str, "Base", dict[str, Any]]] | None = None,
    ) -> "Base":

        data = obj.model_dump() if hasattr(obj, "model_dump") else vars(obj)

        # Get the ORM's mapped column keys
        valid_keys = {col.key for col in cls.columns()}

        # Filter the attributes
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}

        if include:
            for attr in include:
                if isinstance(attr, str):
                    value = getattr(obj, attr, None)
                    filtered_data[attr] = value
                else:
                    value = getattr(obj, attr[0], None)
                    orm_class = attr[1]
                    try:
                        kwargs = attr[2]
                    except IndexError:
                        kwargs = None
                    orm_instance = orm_class.from_attributes(value, **kwargs)
                    filtered_data[attr[0]] = orm_instance

        return cls(**filtered_data)

    def __getattr__(self, attr):
        alt_name = attr + "_"
        return super().__getattribute__(alt_name)

    def __repr__(self):
        key_values = [
            f"{column.key}={repr(getattr(self, column.key))}" for column in self.__class__.columns()
        ]
        return f"{self.__class__.__name__}({', '.join(key_values)})"


class TimestampBase(Base):
    """
    Abstact(Parent class) for tables that have the created_at and updated_at column.
    This class ensures consistent UTC timestamping across all database operations,
    regardless of the server's local timezone.
    **Notes about the behaviour of the class**
     - All timestamps are automatically converted to UTC before being stored in the database
     - Timezone-aware handling ensures consistent behavior across different geographic locations
    """

    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=current_timestamp, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP,
        server_default=current_timestamp,
        server_onupdate=current_timestamp,
        nullable=False,
    )


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

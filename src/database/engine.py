# src/database/engine.py
from icecream import ic
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from configs import DBConfig, bool_
from pyutils.logging import configure_loggers

configure_loggers(directory="configurations", filename="logger_config.yaml")

__all__ = ["engine", "SessionLocal", "async_mysql_uri"]

username = DBConfig.user.get("username")
password = DBConfig.user.get("password")
host = DBConfig.service.get("host")
port = DBConfig.service.get("port", default=3306)
echo = DBConfig.service.get("echo", default=False, cast=bool_)
database = DBConfig.service.get("database")

async_mysql_uri = ic(f"mysql+aiomysql://{username}:{password}@{host}:{port}/{database}")
engine = create_async_engine(async_mysql_uri, echo=echo, pool_pre_ping=True)


SessionLocal: sessionmaker[AsyncSession] = sessionmaker(  # type: ignore
    bind=engine, autoflush=False, expire_on_commit=False, class_=AsyncSession
)

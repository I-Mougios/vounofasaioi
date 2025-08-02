# src/database/engine.py
from pathlib import Path

import sqlalchemy as sa
from icecream import ic

from configs import DBConfig

__all__ = ["engine"]

base_dir = Path(__file__).resolve().parents[0]

username = DBConfig.user.get("username")
password = DBConfig.user.get("password")
host = DBConfig.service.get("host")
port = DBConfig.service.get("port", default=3306)
echo = DBConfig.service.get("echo", default=False, cast=bool)
database = DBConfig.service.get("database")

tmp_mysql_uri = f"mysql+pymysql://{username}:{password}@{host}:{port}"
tmp_engine = sa.create_engine(tmp_mysql_uri, echo=echo)


with tmp_engine.connect() as conn:
    conn.execute(sa.text(f"CREATE DATABASE IF NOT EXISTS {database}"))

mysql_uri = ic(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")
engine = sa.create_engine(mysql_uri, echo=echo)

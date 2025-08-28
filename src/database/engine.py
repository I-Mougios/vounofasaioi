# src/database/engine.py
import sqlalchemy as sa
from icecream import ic

from configs import DBConfig, bool_
from pyutils.logging import configure_loggers

configure_loggers(directory="configurations", filename="logger_config.yaml")

__all__ = ["engine"]

username = DBConfig.user.get("username")
password = DBConfig.user.get("password")
host = DBConfig.service.get("host")
port = DBConfig.service.get("port", default=3306)
echo = DBConfig.service.get("echo", default=False, cast=bool_)
database = DBConfig.service.get("database")

mysql_uri = ic(f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}")
engine = sa.create_engine(mysql_uri, echo=echo)

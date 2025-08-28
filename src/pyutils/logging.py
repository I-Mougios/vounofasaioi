# src/pyutils/logging.py
import json
import logging
import re
from datetime import datetime
from pathlib import Path

from yaml import safe_load


def configure_loggers(
    directory: str | None = None, filename: str = "logger_config.yaml"
) -> dict | None:
    try:
        parents = Path(__file__).resolve().parents
    except NameError:
        parents = Path.cwd().resolve().parents

    for path in parents:
        if directory is not None:
            path = path / directory

        candidate = path / filename

        if candidate.exists():
            with open(candidate, encoding="utf-8") as f:
                config = safe_load(f)

            logging.config.dictConfig(config)
            return config

    raise FileNotFoundError(f"{filename} not found")


def serialize_local_timestamp(t: float) -> str:
    dt = datetime.fromtimestamp(t)
    return dt.strftime("%H:%M:%S")


class SQLAlchemyFormatter(logging.Formatter):

    @staticmethod
    def _extract_query_from_exception(exc_value: str) -> dict:

        exc_str = str(exc_value)
        sql_match = re.search(r"\[SQL:\s*(.*?)\]", exc_str, re.DOTALL)
        params_match = re.search(r"\[parameters:\s*(.*?)\]", exc_str, re.DOTALL)
        return {"query": sql_match.group(1), "params": params_match.group(1)}

    def format(self, record: logging.LogRecord) -> str:  # noqa A003
        if record.exc_info:
            # Get the exception components
            exc_type, exc_value, exc_traceback = record.exc_info
            exception = {
                "exc_type": exc_type.__name__,
                "exc_summary": str(exc_value).split("\n")[0],
            }

            query_dict = self._extract_query_from_exception(exc_value)
            exception.update(query_dict)
            exception_json = json.dumps(exception, indent=2)
            return exception_json

        message = record.getMessage()
        formatted_string = (
            f"[{serialize_local_timestamp(record.created)}.{int(record.msecs)}]: {record.levelname}"
        )
        formatted_string = formatted_string + "\n" + message

        return formatted_string


class SQLAlchemyFilter(logging.Filter):
    SQL_KEYWORDS = ("SELECT", "INSERT", "UPDATE", "CREATE", "DELETE", "ALTER")
    SQL_IGNORE = ("SELECT @@SQL_MODE", "SELECT @@LOWER_CASE_TABLE_NAMES")

    def filter(self, record: logging.LogRecord) -> bool:  # noqa A003
        # Always keep logs with exceptions
        if record.exc_info:
            return True
        # Normalize message to uppercase for comparison
        msg = record.getMessage().strip().upper()

        if any(msg.startswith(pat) for pat in self.SQL_IGNORE):
            return False

        if msg.startswith(self.SQL_KEYWORDS):
            return True

        return False

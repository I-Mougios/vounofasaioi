from icecream import ic

from pyutils import ConfigMeta

__all__ = ["DBConfig", "bool_"]


class DBConfig(
    metaclass=ConfigMeta, config_filename="database.test.ini", config_directory="configurations"
):
    """Database configurations"""


def bool_(value):
    return True if value.casefold() == "true" else False


if DBConfig.globals.get("icecream_enabled", cast=bool_):
    ic.enable()
else:
    ic.disable()

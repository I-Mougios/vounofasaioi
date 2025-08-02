from icecream import ic

from pyutils import ConfigMeta


class DBConfig(
    metaclass=ConfigMeta, config_filename="database.test.ini", config_directory="configurations"
):
    """Database configurations"""


if DBConfig.globals.get("icecream_enabled", False):
    ic.enable()
else:
    ic.disable()

from pydantic.alias_generators import to_snake


def to_snake_alias(in_str: str) -> str:
    """
    Converts a string to snake_case and removing trailing underscores.
    :param in_str(str): the input string to convert to snake_case
    :return: the converted string
    """
    camel_alias = to_snake(in_str)
    return camel_alias.removesuffix("_")

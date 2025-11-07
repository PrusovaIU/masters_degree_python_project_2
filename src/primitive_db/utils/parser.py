from re import match, Match
from typing import Any


class ParserError(Exception):
    pass


class MatchError(ParserError):
    pass


def match_command_data(regex: str, command_data: str) -> Match:
    """
    Проверка формата аргументов команды.

    :param regex: регулярное выражение.
    :param command_data: аргументы команды.
    :return: объект Match, если аргументы соответствуют формату.

    :raises MatchError: если аргументы не соответствуют формату.
    """
    matching = match(regex, command_data)
    if not matching:
        raise MatchError("неверный формат команды")
    return matching


def parse_command_conditions(conditions_str: str) -> dict[str, Any]:
    """
    Парсинг условий команды вида "column1 = value1, column2 = value2".

    :param conditions_str: строка с условиями.
    :return: словарь с условиями вида {колонка: значение}

    :raises MatchError: если строка с условиями не соответствуют формату.

    :raises ValueError: если значение не соответствует формату.
    """
    data = {}
    conditions = [c.strip() for c in conditions_str.split(",")]
    for c in conditions:
        matching = match_command_data(r"(\w+) ?= ?([\w\"]+)", c)
        data[matching.group(1)] = check_value(matching.group(2))
    return data


def check_value(value: str) -> Any:
    """
    Проверка значения для команд insert и update.

    :param value: значение.
    :return: проверенное значение.

    :raises ValueError: если значение не соответствует формату.
    """
    value = value.strip()
    if match(r"^[+-]?\d+(\.\d+)?$", value):
        return value

    if value in ("true", "false"):
        return value

    quoted_match = match(r"^\"(.*)\"$", value) \
                   or match(r"^'(.*)'$", value)
    if quoted_match:
        return quoted_match.group(1)

    raise ValueError(f"неверный формат значения ({value})")

from re import match, Match


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


def parse_command_conditions(conditions_str: str) -> dict:
    """
    Парсинг условий команды.

    :param conditions_str: строка с условиями.
    :return: словарь с условиями вида {колонка: значение}

    :raises MatchError: если строка с условиями не соответствуют формату.
    """
    data = {}
    conditions = [c.strip() for c in conditions_str.split(",")]
    for c in conditions:
        matching = match_command_data(r"(\w+) ?= ?([\w\"]+)", c)
        data[matching.group(1)] = matching.group(2)
    return data

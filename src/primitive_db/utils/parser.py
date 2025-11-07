from re import match, Match
from typing import Any
from src.primitive_db.utils.cache import create_cacher


class ParserError(Exception):
    pass


class MatchError(ParserError):
    pass


@create_cacher()
def match_command_data(regex: str, command_data: str) -> Match:
    """
    Выполняет сопоставление строки с регулярным выражением.

    :param regex: регулярное выражение для поиска совпадения.
    :param command_data: строка, к которой применяется регулярное выражение.
    :return: объект `re.Match`, если совпадение найдено.

    :raises MatchError: если совпадение не найдено.
    """
    matching = match(regex, command_data)
    if not matching:
        raise MatchError("неверный формат команды")
    return matching


@create_cacher()
def parse_command_conditions(conditions_str: str) -> dict[str, Any]:
    """
    Парсит строку условий команды (например, WHERE или SET) в словарь.

    Поддерживает формат: ключ = значение, где значение может быть:
        - числом (int или float)
        - строкой в кавычках ("abc" или 'abc')
        - булевым значением (true/false)
        - не кавычками, если это идентификатор

    :param conditions_str: строка условий, например: "name = 'John', age = 30".

    :return: словарь вида {ключ: значение}, где значения проходят валидацию
        и преобразование через `check_value`.

    :raises ValueError: если формат условия некорректен или значение не
        может быть распознано

    :raises MatchError: если строка не соответствуют формату.
    """
    data = {}
    conditions = [c.strip() for c in conditions_str.split(",")]
    for c in conditions:
        matching = match_command_data(r"(\w+) ?= ?([\w\"]+)", c)
        data[matching.group(1)] = check_value(matching.group(2))
    return data


@create_cacher()
def check_value(value: str) -> Any:
    """
    Проверяет и преобразует строку в соответствующее значение:
        - число (int или float)
        - булево значение (true/false)
        - строку без кавычек, если она в них заключена

    :param value: входная строка.

    :return: преобразованное значение (str для чисел и bool, str без кавычек
        для строк).

    :raises ValueError: если формат некорректен.
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

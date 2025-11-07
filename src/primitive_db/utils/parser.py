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
class CommandError(Exception):
    """
    Тип исключения, возникающего при получении некорректной команды
    """
    pass


class UnknownCommandError(CommandError):
    pass


class CommandSyntaxError(CommandError):
    pass

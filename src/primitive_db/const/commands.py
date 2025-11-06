from enum import Enum
from io import DEFAULT_BUFFER_SIZE
from zlib import DEF_BUF_SIZE


class Commands(Enum):
    create_table = "create_table"
    list_tables = "list_tables"
    drop_table = "drop_table"
    insert = "insert"
    select = "select"
    exit = "exit"
    help = "help"


DB_COMMANDS_DESCRIPTION = {
    Commands.create_table:
        "<имя таблицы> <столбец1:тип> <столбец2:тип> ... - создать таблицу",
    Commands.list_tables: "- показать список всех таблиц",
    Commands.drop_table: "<имя таблицы> - удалить таблицу",
}

CRUD_COMMANDS_DESCRIPTION = {
    Commands.insert:
        "into <имя таблицы> values (<значение1>, <значение2>, ...) - "
        "создать запись"
}

OTHER_COMMANDS_DESCRIPTION = {
    Commands.exit: "- выход из программы",
    Commands.help: "- справочная информация"
}


def _commands_help(commands: dict[Enum, str]) -> list[str]:
    return [
        f"<command> {command.value} {description}"
        for command, description in commands.items()
    ]


COMMANDS_HELP = "\n".join([
    "***База данных***",
    "Функции:",
    *_commands_help(DB_COMMANDS_DESCRIPTION),
    "",
    "***Операции с данными***",
    "Функции:",
    *_commands_help(CRUD_COMMANDS_DESCRIPTION),
    "",
    "***Прочие***",
    "Функции:",
    *_commands_help(OTHER_COMMANDS_DESCRIPTION),
    ""
])

from enum import Enum
from io import DEFAULT_BUFFER_SIZE
from zlib import DEF_BUF_SIZE


class Commands(Enum):
    create_table = "create_table"
    list_tables = "list_tables"
    drop_table = "drop_table"
    insert = "insert"
    exit = "exit"
    help = "help"


DB_COMMANDS_DESCRIPTION = {
    Commands.create_table:
        "<имя таблицы> <столбец1:тип> <столбец2:тип> ... - создать таблицу",
    Commands.list_tables: "- показать список всех таблиц",
    Commands.drop_table: "<имя таблицы> - удалить таблицу",
    Commands.exit: "- выход из программы",
    Commands.help: "- справочная информация"
}

CRUD_COMMANDS_DESCRIPTION = {
    Commands.insert:
        "into <имя таблицы> values (<значение1>, <значени2>, ...) - "
        "создать запись"
}


COMMANDS_HELP = "\n".join([
    "***База данных***",
    "\n",
    "Функции:",
    *[
        f"<command> {command.value} {description}"
        for command, description in DB_COMMANDS_DESCRIPTION.items()
    ],
    "\n",
    "***Операции с данными***",
    "\n",
    "Функции:",
    *[
        f"<command> {command.value} {description}"
        for command, description in CRUD_COMMANDS_DESCRIPTION.items()
    ],
    "\n"
])

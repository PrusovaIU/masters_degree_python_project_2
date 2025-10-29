from enum import Enum


class Commands(Enum):
    create_table = "create_table"
    list_tables = "list_tables"
    drop_table = "drop_table"
    exit = "exit"
    help = "help"


COMMANDS_DESCRIPTION = {
    Commands.create_table:
        "<имя таблицы> <столбец1:тип> <столбец2:тип> ... - создать таблицу",
    Commands.list_tables: "- показать список всех таблиц",
    Commands.drop_table: "<имя таблицы> - удалить таблицу",
    Commands.exit: "- выход из программы",
    Commands.help: "- справочная информация"
}


COMMANDS_HELP = "\n".join([
    "***База данных***",
    "\n",
    "Функции:",
    *[
        f"<command> {command.value} {description}"
        for command, description in COMMANDS_DESCRIPTION.items()
    ],
    "\n"
])

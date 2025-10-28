from collections.abc import Callable

import prompt
from src.primitive_db.core import Core
from src.primitive_db.conf import CONFIG
from src.primitive_db.const.commands import Commands, COMMANDS_HELP
from src.primitive_db.metadata import DatabaseError, Table
from re import match, findall


class CommandError(Exception):
    pass


def simple_handler(func: Callable[[str], None]) -> Callable[[str], None]:
    def wrapper(command_data: str) -> None:
        if command_data:
            raise CommandError("Команда не принимает аргументов")
        else:
            func(command_data)
    return wrapper


class Engine:
    def __init__(self):
        self._core = Core(CONFIG.db_metadata_path)
        self._exit = False
        self._handlers: dict[Commands, Callable[[str], None]] = {
            command: getattr(self, f"_{command.value}")
            for command in Commands
        }

    @staticmethod
    @simple_handler
    def _help(command_data: str) -> None:
        print(COMMANDS_HELP)

    @simple_handler
    def _exit(self, command_data: str) -> None:
        to_exit = prompt.regex(
            r"^(y|n)$",
            "Вы уверены, что хотите выйти? (y/n): "
        )
        if to_exit == "y":
            self._exit = True

    def _create_table(self, command_data: str) -> None:
        command_data = command_data.strip()
        cd_match = match(r"^(\w+) ((\w+ ?: ?\w+ ?)+)$", command_data)
        if not cd_match:
            print("Неверный формат команды")
            return None
        table_name: str = cd_match[0]
        fields: str = cd_match[1]
        columns: list[tuple[str, str]] = []
        for item in findall(r"\w+ ?: ?\w+", fields):
            column_name, column_type = [el.strip() for el in item.split(":")]
            columns.append((column_name, column_type))
        try:
            table: Table = self._core.create_table(table_name, columns)
        except DatabaseError as err:
            print(f"Ошибка: {err}")
        else:
            columns_descr = [
                f"{column.name}:{column.column_type}"
                for column in table.columns
            ]
            print(
                f"Таблица {table_name} успешно создана со столбцами: "
                f"{', '.join(columns_descr)}"
            )

    @simple_handler
    def _list_tables(self) -> None:
        lines = []
        for table in self._core.list_tables():
            lines.append(f"\t- {table.name}")
        data = "\n".join(lines)
        print(data)

    @staticmethod
    def _input_command() -> tuple[Commands, str]:
        data = prompt.string("Введите команду: ")
        command, command_data = data.split(" ", maxsplit=1)
        try:
            return Commands(command), command_data
        except ValueError:
            raise CommandError("Команда не найдена")

    def run(self) -> None:
        while not self._exit:
            try:
                command, command_data = self._input_command()
                handler = self._handlers[command]
                handler(command_data)
            except CommandError as err:
                print(err)
            except KeyError:
                print("Команда не найдена")


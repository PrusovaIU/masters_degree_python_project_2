from collections.abc import Callable

import prompt
from src.primitive_db.core import Core
from src.primitive_db.conf import CONFIG
from src.primitive_db.const.commands import Commands, COMMANDS_HELP
from src.primitive_db.metadata import DatabaseError, Table
from re import match, findall, Match
from typing import ClassVar


class CommandError(Exception):
    """
    Тип исключения, возникающего при получении некорректной команды
    """
    pass


class UnknownCommandError(CommandError):
    pass


class CommandSyntaxError(CommandError):
    pass


CommandDataType = str | None
HandlerType = Callable[[ClassVar], None]


def simple_handler(func: HandlerType) -> HandlerType:
    """
    Декоратор для простых обработчиков команд, которые не принимают
    аргументы.

    Декоратор позволяет принимать аргумент command_data для универсальности
    взаимодействия с обрабочиками. Если аргумент передан, и он не пустой или
    не None, то вызывается исключение.
    """
    def wrapper(self, command_data: CommandDataType = None) -> None:
        if command_data:
            raise CommandError("Команда не принимает аргументов")
        else:
            func(self)
    return wrapper


class Engine:
    """
    Движок для взаимодействия с пользователем.
    """
    def __init__(self):
        self._core = Core(CONFIG.db_metadata_path)
        self._exit_flag = False
        self._handlers: dict[Commands, Callable[[str], None]] = {
            command: getattr(self, f"_{command.value}")
            for command in Commands
        }

    @simple_handler
    def _help(self) -> None:
        """
        Обработчик команды help.

        :return: None.
        """
        print(COMMANDS_HELP)

    @simple_handler
    def _exit(self) -> None:
        """
        Обработчик команды exit.

        :return: None.
        """
        to_exit: Match = prompt.regex(
            r"^(y|n)$",
            "Вы уверены, что хотите выйти? (y/n): "
        )
        if to_exit.string == "y":
            self._exit_flag = True

    def _create_table(self, command_data: str) -> None:
        """
        Обработчик команды create_table.

        :param command_data: аргументы команды.
        :return: None.

        :raises CommandError: если аргументы команды не соответствуют
            требуемому формату.

        :raises DatabaseError: если не удалось создать таблицу.
        """
        table_name, columns = self._create_table_handle_cd(command_data)
        table: Table = self._core.create_table(table_name, columns)
        columns_descr = [
            f"{column.name}:{column.column_type}"
            for column in table.columns
        ]
        print(
            f"Таблица {table_name} успешно создана со столбцами: "
            f"{', '.join(columns_descr)}"
        )

    def _create_table_handle_cd(
            self,
            command_data: str
    ) -> tuple[str, list[tuple[str, str]]]:
        """
        Обработчик аргументов команды create_table.

        :param command_data: аргументы команды.
        :return: имя таблицы, список столбцов вида [имя столбца, тип столбца].

        :raises CommandError: если аргументы команды не соответствуют
            требуемому формату.
        """
        command_data = command_data.strip()
        cd_match = match(r"^(\w+) ((\w+ ?: ?\w+ ?)+)$", command_data)
        if not cd_match:
            raise CommandSyntaxError("Неверный формат команды")
        table_name: str = cd_match.group(1)
        fields: str = cd_match.group(2)
        columns = self._create_table_handle_columns_list(fields)
        return table_name, columns

    @staticmethod
    def _create_table_handle_columns_list(
            columns_str: str
    ) -> list[tuple[str, str]]:
        """
        Конвертирует строку с описанием столбцов в список столбцов вида
        [имя столбца, тип столбца].

        :param columns_str: строка с описанием столбцов.
        :return: None.
        """
        columns: list[tuple[str, str]] = []
        for item in findall(r"\w+ ?: ?\w+", columns_str):
            column_name, column_type = [el.strip() for el in item.split(":")]
            columns.append((column_name, column_type))
        return columns

    @simple_handler
    def _list_tables(self) -> None:
        """
        Обработчик команды list_tables.

        :return: None.
        """
        lines = []
        for table in self._core.list_tables():
            lines.append(f"\t- {table.name}")
        if lines:
            data = "\n".join(lines)
        else:
            data = "Таблицы отсутствуют"
        print(data)

    def _drop_table(self, command_data: str) -> None:
        pass

    @staticmethod
    def _input_command() -> tuple[Commands, str]:
        """
        Получение команды из ввода пользователя.

        :return: команда, аргументы команды.

        :raises CommandError: если команда не найдена.
        """
        data = prompt.string("Введите команду: ")
        command_els = data.split(" ", maxsplit=1)
        command = command_els[0].lower().strip()
        command_data = command_els[1].strip() \
            if len(command_els) > 1 \
            else None
        try:
            return Commands(command), command_data
        except ValueError:
            raise UnknownCommandError("Команда не найдена")

    def run(self) -> None:
        """
        Запуск движка.

        :return: None.
        """
        self._help()
        while not self._exit_flag:
            try:
                command, command_data = self._input_command()
                handler = self._handlers[command]
                handler(command_data)
            except CommandError as err:
                print(err)
            except KeyError:
                print("Команда не найдена")
            except Exception as err:
                print(f"Ошибка: {err}")


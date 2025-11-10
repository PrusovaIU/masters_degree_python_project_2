from collections.abc import Callable
from pathlib import Path
from re import Match, findall
from typing import Any, ClassVar, Optional

import prompt
from prettytable import PrettyTable

from src.primitive_db.const.commands import COMMANDS_HELP, Commands
from src.primitive_db.core import Core
from src.primitive_db.exceptions.cancelled_error import CancelledError
from src.primitive_db.exceptions.command_error import (
    CommandError,
    UnknownCommandError,
)
from src.primitive_db.metadata import Table
from src.primitive_db.utils import parser
from src.primitive_db.utils.decorators import handle_db_errors

CommandDataType = str | None
HandlerType = Callable[[object | CommandDataType], None]


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
            raise CommandError("команда не принимает аргументов")
        else:
            func(self)
    return wrapper


def handler(func: HandlerType) -> HandlerType:
    """
    Декоратор для обработчиков команд, которые принимают аргументы.
    """
    def wrapper(self, command_data: CommandDataType) -> None:
        if command_data:
            func(self, command_data)
        else:
            raise CommandError("не переданы аргументы команды")
    return wrapper


class Engine:
    """
    Движок для взаимодействия с пользователем.
    """
    def __init__(self, database_path: Path):
        self._core = Core(database_path)
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

    @handle_db_errors
    @handler
    def _create_table(self, command_data: str) -> None:
        """
        Обработчик команды create_table.

        :param command_data: аргументы команды.
        :return: None.
        """
        table_name, columns = self._create_table_handle_cd(command_data)
        table: Table = self._core.create_table(table_name, columns)
        columns_descr = [
            f"{column.name}:{column.column_type}"
            for column in table.columns
        ]
        print(
            f"Таблица \"{table_name}\" успешно создана со столбцами: "
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

        :raises src.primitive_db.utils.parser.ParserError: если аргументы
            команды не соответствуют требуемому формату.
        """
        cd_match = parser.match_command_data(
            r"^(\w+) ((\w+ ?: ?\w+ ?)+)$",
            command_data
        )
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

        :raises src.primitive_db.utils.parser.ParserError: если аргументы
            команды не соответствуют требуемому формату.
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
            columns = ", ".join(
                [f"{c.name}: {c.column_type}" for c in table.columns]
            )
            lines.append(f"\t- {table.name} ({columns})")
        if lines:
            data = "\n".join(lines)
        else:
            data = "Таблицы отсутствуют"
        print(data)

    @handle_db_errors
    @handler
    def _drop_table(self, command_data: str) -> None:
        """
        Обработчик команды drop_table.

        :param command_data: аргументы команды.
        :return: None.
        """
        cd_match = parser.match_command_data(r"^(\w+)$", command_data)
        self._core.drop_table(cd_match.group(1))
        print(
            f"Таблица \"{command_data}\" успешно удалена"
        )

    @handle_db_errors
    @handler
    def _insert(self, command_data: str) -> None:
        """
        Обработчик команды insert.

        :param command_data: аргументы команды.
        :return: None.

        :raises src.primitive_db.utils.parser.ParserError: если аргументы
            команды не соответствуют требуемому формату.
        """
        matching = parser.match_command_data(
            r"^into (\w+) values \(([\w\", ]+)\)$",
            command_data
        )
        table_name = matching.group(1)
        values = [
            parser.check_value(el.strip())
            for el in matching.group(2).split(",")
        ]
        row_id: int = self._core.insert(table_name, values)
        print(f"Запись с ID={row_id} добавлена в таблицу \"{table_name}\"")

    @handle_db_errors
    @handler
    def _select(self, command_data: str) -> None:
        """
        Обработчик команды select.

        :param command_data: аргументы команды.
        :return: None.
        """
        matching = parser.match_command_data(
            r"^from (\w+) ?(where ((\w+) ?= ?([\w\"]+)))?$",
            command_data
        )
        table_name: str = matching.group(1)
        where: Optional[str] = matching.group(3)
        values: dict[str, Any] = parser.parse_command_conditions(where) \
            if where else {}
        rows = self._core.select(table_name, values)
        pretty_table = PrettyTable(field_names=rows[0])
        pretty_table.add_rows(rows[1:])
        print(pretty_table)

    @handle_db_errors
    @handler
    def _update(self, command_data: str) -> None:
        """
        Обработчик команды update.

        :param command_data: аргументы команды.
        :return: None.
        """
        matching = parser.match_command_data(
            r"^(\w+) set ((\w+ ?= ?[\w\"]+,? ?)+) where (\w+ ?= ?[\w\"]+)$",
            command_data
        )
        table_name = matching.group(1)
        set_data = parser.parse_command_conditions(matching.group(2))
        where_data = parser.parse_command_conditions(matching.group(4))
        updated_rows_ids: list[int] = self._core.update(
            table_name,
            set_data,
            where_data
        )
        for row_id in updated_rows_ids:
            print(
                f"Запись с ID={row_id} обновлена в таблице \"{table_name}\""
            )

    @handle_db_errors
    @handler
    def _delete(self, command_data: str) -> None:
        """
        Обработчик команды delete.

        :param command_data: аргументы команды.
        :return: None.
        """
        matching = parser.match_command_data(
            r"^from (\w+) where (\w+ ?= ?[\w\"]+)$",
            command_data
        )
        table_name = matching.group(1)
        where = parser.parse_command_conditions(matching.group(2))
        deleted_rows_ids: list[int] = self._core.delete(table_name, where)
        for row_id in deleted_rows_ids:
            print(
                f"Запись с ID={row_id} удалена из таблицы \"{table_name}\""
            )

    @handle_db_errors
    @handler
    def _info(self, command_data: str) -> None:
        matching = parser.match_command_data(r"^(\w+)$", command_data)
        table_name = matching.group(1)
        table = self._core.get_table(table_name)
        columns = ", ".join(
            [f"{c.name}:{c.column_type}" for c in table.columns]
        )
        print(
            f"Таблица: {table.name}\n"
            f"Столбцы: {columns}\n"
            f"Количество записей: {len(table.rows)}"
        )

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
            raise UnknownCommandError("Неизвестная команда")

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
            except CancelledError as err:
                print(err)
            except CommandError as err:
                print(err)
            except KeyError:
                print("Команда не найдена")
            except Exception as err:
                print(f"Ошибка: {err}")

from collections.abc import Callable

import prompt
from src.primitive_db.core import Core
from src.primitive_db.conf import CONFIG
from src.primitive_db.const.commands import Commands, COMMANDS_HELP
from src.primitive_db.metadata import DatabaseError, Table
from re import match, findall, Match
from typing import ClassVar, Any, Optional
from prettytable import PrettyTable


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
        self._core = Core(CONFIG.database_path)
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

        :raises metadata.db_object.DatabaseError: если не удалось удалить
            таблицу.

        :raises utils.metadata.MetadataError: если не удалось сохранить
            метаданные.
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

        :raises CommandError: если аргументы команды не соответствуют
            требуемому формату.
        """
        cd_match = self._match_command_data(
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

    def _drop_table(self, command_data: str) -> None:
        """
        Обработчик команды drop_table.

        :param command_data: аргументы команды.
        :return: None.

        :raises CommandError: если аргументы команды не соответствуют
            требуемому формату.

        :raises metadata.db_object.DatabaseError: если не удалось удалить
            таблицу.

        :raises utils.metadata.MetadataError: если не удалось сохранить
            метаданные.
        """
        cd_match = self._match_command_data(r"^(\w+)$", command_data)
        self._core.drop_table(command_data)
        print(
            f"Таблица \"{command_data}\" успешно удалена"
        )

    def _insert(self, command_data: str) -> None:
        """
        Обработчик команды insert.

        :param command_data: аргументы команды.
        :return: None.

        :raises CommandError: если аргументы команды не соответствуют
            требуемому формату.

        :raises src.primitive_db.metadata.db_object.DatabaseError: если не
            удалось добавить строку.

        :raises ValueError: если введены некорректные значения.
        """
        matching = self._match_command_data(
            r"^into (\w+) values \(([\w\", ]+)\)$",
            command_data
        )
        table_name = matching.group(1)
        values = [el.strip() for el in matching.group(2).split(",")]
        for i, value in enumerate(values):
            values[i] = self._check_value(value)
        row_id: int = self._core.insert(table_name, values)
        print(f"Запись с ID={row_id} добавлена в таблицу \"{table_name}\"")

    def _select(self, command_data: str) -> None:
        """
        Обработчик команды select.

        :param command_data: аргументы команды.
        :return: None.

        :raises CommandError: если аргументы команды не соответствуют
            требуемому формату.

        :raises src.primitive_db.metadata.db_object.DatabaseError: если не
            удалось получить строки.

        :raises ValueError: если введены некорректные значения.
        """
        matching = self._match_command_data(
            r"^from (\w+) ?(where ((\w+) ?= ?([\w\"]+)))?$",
            command_data
        )
        table_name: str = matching.group(1)
        column_name: Optional[str] = matching.group(4)
        value: Optional[str] = matching.group(5)
        if value is not None:
            value = self._check_value(value)
        rows = self._core.select(table_name, column_name, value)
        pretty_table = PrettyTable(field_names=rows[0])
        pretty_table.add_rows(rows[1:])
        print(pretty_table)

    def _update(self, command_data: str) -> None:
        """

        :param command_data:
        :return:

        :raises CommandError: если аргументы команды не соответствуют
            требуемому формату.

        :raises src.primitive_db.metadata.db_object.DatabaseError: если не
            удалось обновить строки.

        :raises ValueError: если введены некорректные значения.
        """
        matching = self._match_command_data(
            r"^(\w+) set (\w+) ?= ?([\w\"]+) where (\w+) ?= ?([\w\"]+)$",
            command_data
        )
        table_name = matching.group(1)
        set_column_name = matching.group(2)
        set_value = self._check_value(matching.group(3))
        where_column_name = matching.group(4)
        where_value = self._check_value(matching.group(5))
        updated_rows_ids: list[int] = self._core.update(
            table_name,
            set_column_name,
            set_value,
            where_column_name,
            where_value
        )
        for row_id in updated_rows_ids:
            print(
                f"Запись с ID={row_id} обновлена в таблице \"{table_name}\""
            )

    @staticmethod
    def _check_value(value: str) -> Any:
        """
        Проверка значения для команд insert и update.

        :param value: значение.
        :return: проверенное значение.

        :raises ValueError: если значение не соответствует формату.
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

        raise ValueError(f"Неверный формат значения ({value})")

    @staticmethod
    def _match_command_data(regex: str, command_data: str) -> Match:
        """
        Проверка формата аргументов команды.

        :param regex: регулярное выражение.
        :param command_data: аргументы команды.
        :return: объект Match, если аргументы соответствуют формату.

        :raises CommandSyntaxError: если аргументы не соответствуют формату.
        """
        matching = match(regex, command_data)
        if not matching:
            raise CommandSyntaxError("Неверный формат команды")
        return matching

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


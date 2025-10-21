# from dataclasses import dataclass
#
# from src.primitive_db.const.column_types import ColumnTypes
# from enum import Enum
# from json import dumps
# from typing import TypeVar, Type, Any
#
#
# class DatabaseError(Exception):
#     pass
#
#
# class DatabaseParseJsonError(DatabaseError):
#     pass
#
#
# class TableParseJsonError(DatabaseError):
#     pass
#
#
# class ColumnParseJsonError(DatabaseError):
#     pass
#
#
# class ColumnJsonTag(Enum):
#     name = "name"
#     type = "type"
#
#
# class TableJsonTag(Enum):
#     name = "name"
#     columns = "columns"
#
#
# class DatabaseJsonTag(Enum):
#     name = "name"
#     tables = "tables"
#
#
# class DBObjectJsonTag(Enum):
#     name = "name"
#
#
# T = TypeVar("T")
#
#
# class DBObject:
#     def __init__(self, name: str, *args, **kwargs):
#         self._name = name
#
#     @property
#     def name(self) -> str:
#         return self._name
#
#     @staticmethod
#     def _parse_kwargs(json_data: dict) -> dict[str, Any]:
#         return {}
#
#     @classmethod
#     def from_json(cls: Type[T], json_data: dict) -> T:
#         if not isinstance(json_data, dict):
#             raise DatabaseParseJsonError(
#                 f"Database object metadata must be a dict, not "
#                 f"{json_data.__class__.__name__}: {dumps(json_data)}"
#             )
#         try:
#             name = json_data[DatabaseJsonTag.name.value]
#             kwargs: dict[str, Any] = cls._parse_kwargs(json_data)
#         except KeyError as err:
#             raise DatabaseParseJsonError(
#                 f"There is tag \"{err}\" in json data: {dumps(json_data)}"
#             )
#         return cls(name, **kwargs)
#
#
# class Column:
#     """
#     Описание колонки таблицы.
#
#     :param name: имя колонки.
#     :param coltype: тип колонки.
#     """
#     def __init__(self, name: str, coltype: ColumnTypes):
#         self._name = name
#         self._type = coltype
#
#     @property
#     def name(self) -> str:
#         return self._name
#
#     @property
#     def type(self) -> ColumnTypes:
#         return self._type
#
#     @classmethod
#     def from_json(cls, json_data: dict) -> "Column":
#         """
#         Создание нового экземпляра класса из описания в json.
#
#         :param json_data: json объект с описанием колонки.
#         :return: новый экземпляр класса Column.
#
#         :raises ColumnParseJsonError: если json_data имеет неверный формат.
#         """
#         if not isinstance(json_data, dict):
#             raise ColumnParseJsonError(
#                 f"Column must be a dict, not "
#                 f"{json_data.__class__.__name__}"
#             )
#         try:
#             name = json_data[ColumnJsonTag.name.value]
#             _type = json_data[ColumnJsonTag.type.value]
#         except KeyError as err:
#             raise ColumnParseJsonError(
#                 f"There is tag \"{err}\" for column in json data"
#             )
#         return cls(name, _type)
#
#
# class Table:
#     """
#     Описание таблицы.
#
#     :param name: имя таблицы.
#     :param columns: список колонок таблицы.
#     """
#     def __init__(self, name: str, columns: list[Column]):
#         self._name = name
#         self._columns = columns
#
#     @property
#     def name(self) -> str:
#         return self._name
#
#     @property
#     def columns(self) -> list[Column]:
#         return self._columns
#
#     @staticmethod
#     def _parse_columns(json_data: dict) -> list[Column]:
#         """
#         Формирование списка колонок из описания в json.
#
#         :param json_data: json объект с описанием колонок.
#         :return: список колонок.
#
#         :raises TableParseJsonError: если json_data имеет неверный формат.
#         """
#         if not isinstance(json_data, list):
#             raise TableParseJsonError(
#                 f"Columns must be a list, not "
#                 f"{json_data.__class__.__name__}"
#             )
#         if len(json_data) == 0:
#             raise TableParseJsonError("Columns must be not empty")
#
#         try:
#             columns = [Column.from_json(column) for column in json_data]
#         except ColumnParseJsonError as err:
#             raise TableParseJsonError(
#                 f"Cannot parse column {i}: {err}"
#             )
#         return columns
#
#
#     @classmethod
#     def from_json(cls, json_data: dict) -> "Table":
#         """
#         Создание нового экземпляра класса из описания в json.
#
#         :param json_data: json объект с описанием таблицы.
#         :return: новый экземпляр класса Table.
#
#         :raises TableParseJsonError: если json_data имеет неверный формат.
#         """
#         if not isinstance(json_data, dict):
#             raise DatabaseParseJsonError(
#                 f"Table must be a dict, not "
#                 f"{json_data.__class__.__name__}"
#             )
#         try:
#             name = json_data[TableJsonTag.name.value]
#             json_columns = json_data[TableJsonTag.columns.value]
#             columns = cls._parse_columns(json_columns)
#             return cls(name, columns)
#         except KeyError as err:
#             raise TableParseJsonError(
#                 f"There is tag \"{err}\" for table in json data"
#             )
#
#
# class Schema:
#     """
#     Описание схемы базы данных.
#
#     :param tables: список таблиц базы данных.
#     """
#     def __init__(self, name: str, tables: list[Table]):
#         self._name = name
#         self._tables = tables
#
#     @property
#     def name(self) -> str:
#         return self._name
#
#     @property
#     def tables(self) -> list[Table]:
#         return self._tables
#
#     @staticmethod
#     def _parse_tables(json_data: dict) -> list[Table]:
#         """
#         Формирование списка таблиц из описания в json.
#
#         :param json_data: json объект с описанием таблиц.
#         :return: список таблиц.
#
#         :raises DatabaseParseJsonError: если json_data имеет неверный формат.
#         """
#         i = 0
#         try:
#             json_tables = json_data["tables"]
#             if not isinstance(json_tables, list):
#                 raise DatabaseParseJsonError(
#                     f"Tables must be a list, not "
#                     f"{json_tables.__class__.__name__}"
#                 )
#             tables = []
#             for i, table in enumerate(json_tables):
#                 tables.append(Table.from_json(table))
#         except KeyError as err:
#             raise DatabaseParseJsonError(
#                 f"There is tag \"{err}\" in json data"
#             )
#         except TableParseJsonError as err:
#             raise DatabaseParseJsonError(f"Cannot parse table {i}: {err}")
#         return tables
#
#     @classmethod
#     def from_json(cls, json_data: dict) -> "Database":
#

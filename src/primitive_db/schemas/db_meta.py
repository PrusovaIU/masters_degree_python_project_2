from dataclasses import dataclass
from typing import Self

from src.primitive_db.const.column_types import ColumnTypes
from enum import Enum


class DatabaseError(Exception):
    pass


class DatabaseParseJsonError(DatabaseError):
    pass


class TableParseJsonError(DatabaseError):
    pass


class TableJsonTag(Enum):
    name = "name"
    columns = "columns"


@dataclass
class Column:
    name: str
    type: ColumnTypes


class Table:
    def __init__(self, name: str, columns: list[Column]):
        self._name = name
        self._columns = columns

    @property
    def name(self) -> str:
        return self._name

    @property
    def columns(self) -> list[Column]:
        return self._columns

    @staticmethod
    def _parse_columns(json_data: dict) -> list[Column]:
        if not isinstance(json_data, list):
            raise TableParseJsonError(
                f"Columns must be a list, not "
                f"{json_data.__class__.__name__}"
            )
        try:
            for i, column in enumerate(json_data):
        except


    @classmethod
    def from_json(cls, json_data: dict) -> Self:
        """

        :param json_data:
        :return:

        :raises TableParseJsonError: если json_data имеет неверный формат.
        """
        if not isinstance(json_data, dict):
            raise DatabaseParseJsonError(
                f"Table must be a dict, not "
                f"{json_data.__class__.__name__}"
            )
        try:
            name = json_data[TableJsonTag.name.value]
            json_columns = json_data[TableJsonTag.columns.value]
            columns = cls._parse_columns(json_columns)
            return cls(name, columns)
        except KeyError as err:
            raise TableParseJsonError(
                f"There is tag \"{err}\" for table in json data"
            )




class Database:
    tables: list[Table]

    @staticmethod
    def _parse_tables(json_data: dict) -> list[Table]:
        i = 0
        try:
            json_tables = json_data["tables"]
            if not isinstance(json_tables, list):
                raise DatabaseParseJsonError(
                    f"Tables must be a list, not "
                    f"{json_tables.__class__.__name__}"
                )
            tables = []
            for i, table in enumerate(json_tables):

        except KeyError as err:
            raise DatabaseParseJsonError(
                f"There is tag \"{err}\" in json data"
            )
        except TableParseJsonError as err:
            raise DatabaseParseJsonError(f"Cannot parse table {i}: {err}")


    @classmethod
    def from_json(cls, json_data: dict) -> Self:
        return cls()

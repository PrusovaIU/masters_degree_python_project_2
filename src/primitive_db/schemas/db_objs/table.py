from dataclasses import dataclass

from src.primitive_db.const.column_types import ColumnTypes
from enum import Enum
from json import dumps
from typing import TypeVar, Type, Any
from .db_object import DBObject, IncludedObject
from .column import Column


class TableJsonTag(Enum):
    columns = "columns"


class Table(DBObject):
    def __init__(self, name: str, columns: list[Column]):
        super().__init__(name)
        self._columns = columns

    def __str__(self):
        columns = ", ".join([column.name for column in self._columns])
        return f"<Table {self._name}: {columns}>"

    @property
    def columns(self) -> list[Column]:
        return self._columns

    @classmethod
    def included_objs(cls) -> list[IncludedObject]:
        return [
            IncludedObject(
                "columns",
                TableJsonTag.columns.value,
                Column,
                True
            )
        ]


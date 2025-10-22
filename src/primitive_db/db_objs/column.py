from enum import Enum
from typing import Any

from .db_object import BaseDBObject, DBObjectParam, DBObjectJsonTag
from src.primitive_db.const.column_types import ColumnTypes



class ColumnJsonTag(Enum):
    type = "type"


class Column(BaseDBObject):
    def __init__(self, name: str, column_type: ColumnTypes):
        super().__init__(name)
        self._type = column_type

    def __str__(self):
        return f"<Column {self._name}: {self._type}>"

    @property
    def column_type(self) -> ColumnTypes:
        return self._type

    @classmethod
    def parameters(cls) -> list[DBObjectParam]:
        return [
            DBObjectParam(
                "column_type",
                ColumnJsonTag.type.value,
                ColumnTypes,
                True
            )
        ]

    def to_json(self) -> dict:
        return {
            DBObjectJsonTag.name.value: self._name,
            ColumnJsonTag.type.name: self._type.value
        }

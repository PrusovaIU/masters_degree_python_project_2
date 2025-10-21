from enum import Enum
from typing import Any

from .db_object import BaseDBObject, DBObjectParam
from src.primitive_db.const.column_types import ColumnTypes



class ColumnJsonTag(Enum):
    type = "type"


class Column(BaseDBObject):
    def __init__(self, name: str, coltype: ColumnTypes):
        super().__init__(name)
        self._type = coltype

    def __str__(self):
        return f"<Column {self._name}: {self._type}>"

    @property
    def type(self) -> ColumnTypes:
        return self._type

    @classmethod
    def parameters(cls) -> list[DBObjectParam]:
        return [
            DBObjectParam(
                "coltype",
                ColumnJsonTag.type.value,
                ColumnTypes,
                True
            )
        ]

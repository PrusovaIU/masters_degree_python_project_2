from enum import Enum
from typing import Type

from .db_object import BaseDBObject, DBObjectParam, DBObjectJsonTag, DatabaseError



class ColumnJsonTag(Enum):
    type = "type"


class ColumnError(DatabaseError):
    """
    Класс ошибок для работы с колонками.
    """
    pass


class ColumnTypeError(ColumnError):
    """
    Класс ошибок, возникающий при попытке создать колонку с несуществующим
    типом.
    """
    pass


_COLUMN_TYPE = {
    "int": int,
    "str": str,
    "bool": bool
}


class Column(BaseDBObject):
    def __init__(self, name: str, column_type: str):
        super().__init__(name)
        self._type = column_type
        try:
            self._column_class = _COLUMN_TYPE[column_type]
        except KeyError:
            raise ColumnTypeError(
                f"Invalid type \"{column_type}\" for column \"{name}\""
            )

    def __str__(self):
        return f"<Column {self._name}: {self._type}>"

    @property
    def type(self) -> str:
        return self._type

    def column_class(self) -> Type:
        return self._column_class

    @classmethod
    def parameters(cls) -> list[DBObjectParam]:
        return [
            DBObjectParam(
                "column_type",
                ColumnJsonTag.type.value,
                str,
                True
            )
        ]

    def to_json(self) -> dict:
        return {
            DBObjectJsonTag.name.value: self._name,
            ColumnJsonTag.type.name: self._type
        }

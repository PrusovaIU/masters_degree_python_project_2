from enum import Enum
from typing import Type, Any

from .db_object import Model, Field, DatabaseError



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


class Column(Model):
    column_type: str = Field(str, required=True, alias="type")
    column_class: type

    def __str__(self):
        return f"<Column {self.name}: {self.column_type}>"

    # def to_json(self) -> dict:
    #     return {
    #         DBObjectJsonTag.name.value: self.name,
    #         ColumnJsonTag.type.name: self.column_type
    #     }

from enum import Enum
from .db_object import DBObject, IncludedObject, DatabaseError, DuplicatesError
from .column import Column


class TableJsonTag(Enum):
    columns = "columns"


class TableError(DatabaseError):
    """
    Класс ошибок, возникающих при работе с таблицами.
    """
    pass


class Table(DBObject):
    columns = IncludedObject(
        TableJsonTag.columns.value,
        Column,
        True
    )
    # def __init__(self, name: str, columns: list[Column]):
    #     super().__init__(name)
    #     if self._check_duplicates(columns):
    #         raise DuplicatesError("Cannot create table with duplicate columns")
    #     self._columns = columns

    def __str__(self):
        columns = ", ".join([column.name for column in self._columns])
        return f"<Table {self._name}: {columns}>"

    # @property
    # def columns(self) -> list[Column]:
    #     return self._columns

    # @classmethod
    # def included_objs(cls) -> list[IncludedObject]:
    #     return [
    #         IncludedObject(
    #             "columns",
    #             TableJsonTag.columns.value,
    #             Column,
    #             True
    #         )
    #     ]


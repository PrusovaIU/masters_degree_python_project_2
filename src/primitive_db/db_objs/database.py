from enum import Enum
from typing import Optional

from .db_object import DBObject, IncludedObject
from .table import Table

class DatabaseJsonTag(Enum):
    tables = "tables"


class Database(DBObject):
    def __init__(self, name: str, tables: Optional[list[Table]] = None):
        super().__init__(name)
        self._tables = tables if tables is not None else []

    def __str__(self):
        tables = ", ".join([t.name for t in self.tables])
        return f"<Database {self._name}: {tables}>"

    @property
    def tables(self) -> list[Table]:
        return self._tables

    @classmethod
    def included_objs(cls) -> list[IncludedObject]:
        return [
            IncludedObject(
                "tables",
                DatabaseJsonTag.tables.value,
                Table,
                False
            )
        ]

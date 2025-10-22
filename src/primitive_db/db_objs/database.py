from enum import Enum
from typing import Optional

from .db_object import DBObject, IncludedObject, DatabaseError
from .table import Table


class DatabaseJsonTag(Enum):
    tables = "tables"


class DatabaseObjectExistsError(DatabaseError):
    """
    Класс ошибки, возникающей при попытке добавить в базу данных объект,
    который уже существует.
    """
    pass


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

    def add_table(self, table: Table) -> None:
        """
        Добавление таблицы в базу данных.

        :param table: таблица.
        :return: None.

        :raises AddTableError: если таблица с таким именем уже существует.
        """
        duplicates = [t for t in self._tables if t.name == table.name]
        if duplicates:
            raise DatabaseObjectExistsError(
                f"Table {table.name} already exists"
            )
        self._tables.append(table)

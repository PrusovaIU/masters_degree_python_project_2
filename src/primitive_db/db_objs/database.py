from collections import Counter
from enum import Enum
from typing import Optional

from pkg_resources import require

from .db_object import Model, Field, DatabaseError, ValidationError
from .validator import field_validator
from .table import Table


class DatabaseJsonTag(Enum):
    tables = "tables"


class DatabaseObjectExistsError(DatabaseError):
    """
    Класс ошибки, возникающей при попытке добавить в базу данных объект,
    который уже существует.
    """
    pass


class DatabaseObjectNotFoundError(DatabaseError):
    """
    Класс ошибки, возникающей при попытке получить из базы данных объект,
    который не существует.
    """
    pass


class Database(Model):
    tables: list[Table] = Field(
        list[Table],
        default_factory=list
    )

    def __str__(self):
        tables = ", ".join([t.name for t in self.tables])
        return f"<Database {self.name}: {tables}>"

    @field_validator("tables")
    def tables_validator(self, tables: list | None) -> list:
        name_counts = Counter(obj.name for obj in tables)
        duplicates = [name for name, count in name_counts.items() if count > 1]
        if len(duplicates) > 0:
            raise ValidationError(
                f"duplicate table names ({', '.join(duplicates)})"
            )
        return tables

    # @param_validator("tables")
    # def tables_validator(self, tables: list | None) -> list:
    #     return tables or []

    # def add_table(self, table: Table) -> None:
    #     """
    #     Добавление таблицы в базу данных.
    #
    #     :param table: таблица.
    #     :return: None.
    #
    #     :raises AddTableError: если таблица с таким именем уже существует.
    #     """
    #     duplicates = [t for t in self.tables if t.name == table.name]
    #     if duplicates:
    #         raise DatabaseObjectExistsError(
    #             f"Table {table.name} already exists"
    #         )
    #     self.tables.append(table)
    #
    # def drop_table(self, table_name: str) -> None:
    #     """
    #     Удаление таблицы из базы данных.
    #
    #     :param table_name: имя таблицы.
    #     :return: None.
    #     """
    #     tables = [t for t in self.tables if t.name == table_name]
    #     try:
    #         table = tables[0]
    #         self.tables.remove(table)
    #     except IndexError:
    #         raise DatabaseObjectNotFoundError(
    #             f"Table {table_name} not found"
    #         )

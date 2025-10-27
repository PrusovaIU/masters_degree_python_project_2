from src.primitive_db.utils.duplicates import get_duplicates

from .db_object import Model, Field, DatabaseError, ValidationError
from .validator import field_validator
from .table import Table


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
        duplicates = get_duplicates(tables)
        if duplicates:
            raise ValidationError(
                f"duplicate names of tables ({', '.join(duplicates)})"
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

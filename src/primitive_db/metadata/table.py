from .db_object import DatabaseError, Model, Field, ValidationError
from .column import Column
from .validator import field_validator
from src.primitive_db.utils.duplicates import get_duplicates


class TableError(DatabaseError):
    """
    Класс ошибок, возникающих при работе с таблицами.
    """
    pass


class Table(Model):
    columns: list[Column] = Field(list[Column], required=True)

    def __str__(self):
        columns = ", ".join([column.name for column in self.columns])
        return f"<Table {self.name}: {columns}>"

    @field_validator("columns")
    def tables_validator(self, columns: list | None) -> list:
        duplicates = get_duplicates(columns)
        if duplicates:
            raise ValidationError(
                f"duplicate names of columns ({', '.join(duplicates)})"
            )
        return columns

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


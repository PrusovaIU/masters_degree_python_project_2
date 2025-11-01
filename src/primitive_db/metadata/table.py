from typing import Any

from .db_object import DatabaseError, Model, Field, ValidationError
from .column import Column
from .validator import field_validator
from src.primitive_db.utils.duplicates import get_duplicates


class TableError(DatabaseError):
    """
    Класс ошибок, возникающих при работе с таблицами.
    """
    pass


class TableRowError(TableError):
    pass


class Table(Model):
    columns: list[Column] = Field(list[Column], required=True)
    _rows: list[dict] | None = None

    def __str__(self):
        columns = ", ".join([column.name for column in self.columns])
        return f"<Table {self.name}: {columns}>"

    @field_validator("columns")
    def tables_validator(self, columns: list | None) -> list:
        duplicates = get_duplicates(columns)
        if duplicates:
            raise ValidationError(
                f"колонки с дублирующимися именами ({', '.join(duplicates)})"
            )
        return columns

    @property
    def rows(self) -> list[dict]:
        return self._rows

    @rows.setter
    def rows(self, rows: list[dict]) -> None:
        self._rows = [self._validate_row(row) for row in rows]

    def _validate_row(self, row: dict) -> dict[str, Any]:
        """
        Валидация строки таблицы.

        :param row: строка таблицы вида {имя_колонки: значение}
        :return: валидированная строка.

        :raises TableRowError: если строка не соответствует формату таблицы.
        """
        data = {}
        try:
            for column in self.columns:
                if column.name not in row:
                    raise TableRowError(
                        f"в строке {row} не указано значение для колонки "
                        f"{column.name}"
                    )
                data[column.name] = column.validate_value(row[column.name])
        except ValueError as err:
            raise TableRowError(
                f"в строке {row} указано некорректное значение для колонки "
                f"{column.name} ({err})"
            ) from err
        return data



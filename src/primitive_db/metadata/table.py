from typing import Any, Optional

from .db_object import DatabaseError, Model, Field, ValidationError
from .column import Column
from .validator import field_validator
from src.primitive_db.utils.duplicates import get_duplicates
from src.primitive_db.const.auto_column_names import AutoColumnNames


class TableError(DatabaseError):
    """
    Класс ошибок, возникающих при работе с таблицами.
    """
    pass


class TableRowError(TableError):
    pass


class TableSelectError(TableError):
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

    def add_row(self, values: dict) -> int:
        """
        Добавить строку в таблицу.

        :param values: значения колонок.
        :return: ID добавленной строки.

        :raises TableRowError: если строка не соответствует формату таблицы.
        """
        max_id: int = max(
            [row[AutoColumnNames.ID.value] for row in self._rows],
            default=0
        )
        row_id = max_id + 1
        values[AutoColumnNames.ID.value] = row_id
        row = self._validate_row(values)
        self._rows.append(row)
        return row_id

    def select(
            self,
            column_name: Optional[str],
            value: Any
    ) -> list[dict]:
        """
        Получить строки таблицы.

        :param column_name: колонка для фильтрации.
        :param value: значение для фильтрации.
        :return: список строк таблицы.

        :raises ValueError: некорректное данные для фильтрации.
        """
        if column_name is None and value is None:
            # вернуть все строки
            return self._rows
        elif column_name is None:
            raise ValueError("не указано имя колонки для фильтрации")
        elif value is None:
            raise ValueError("не указано значение для фильтрации")
        else:
            # вернуть строки, соответствующие фильтру
            column = [c for c in self.columns if c.name == column_name]
            if not column:
                raise ValueError(f"колонка {column_name} не найдена")
            value = column[0].validate_value(value)
            return [
                row for row in self._rows
                if row.get(column_name) == value
            ]

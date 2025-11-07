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
    """
    Класс ошибок, возникающих при работе с строками таблиц.
    """
    pass


class UnknownColumnError(TableError):
    """
    Класс ошибок, возникающих при обращении к неизвестной колонке.
    """
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

    def get_column(self, column_name: str) -> Column:
        """
        Получить колонку таблицы по имени.

        :param column_name: имя колонки.
        :return: колонка таблицы.

        :raises UnknownColumnError: если колонка не найдена.
        """
        column = [c for c in self.columns if c.name == column_name]
        try:
            return column[0]
        except IndexError:
            raise UnknownColumnError(f"колонка \"{column_name}\" не найдена")

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
            where: Optional[dict]
    ) -> list[dict]:
        """
        Получить строки таблицы.

        :param where: условия фильтрации вида {колонка: значение}.
        :return: список строк таблицы.

        :raises ValueError: некорректное данные для фильтрации.

        :raises UnknownColumnError: если колонка не найдена.
        """
        if not where:
            return self._rows
        else:
            return self._filter_rows(where)

    def _filter_rows(self, conditions: dict) -> list[dict]:
        """
        Фильтрация строк таблицы по значению в колонке.

        :param conditions: словарь условий фильтрации вида {колонка: значение}
        :return: список строк, удовлетворяющих фильтру.

        :raises UnknownColumnError: если колонка не найдена.
        """
        conditions = {
            key: self._validate_value(key, value)
            for key, value in conditions.items()
        }
        return [
            row for row in self._rows
            if all(row.get(col) == val for col, val in conditions.items())
        ]

    def update_row(
            self,
            set_data: dict,
            where_data: dict
    ) -> list[int]:
        """
        Обновить строки таблицы.

        :param set_data: данные для обновления вида {колонка: значение}.
        :param where_data: название колонки для обновления.
        :return: список ID обновленных строк.

        :raises UnknownColumnError: если колонка не найдена.

        :raises ValueError: переданы некорректные данные.
        """
        validated_set = {
            col: self._validate_value(col, val)
            for col, val in set_data.items()
        }
        validated_where = {
            col: self._validate_value(col, val)
            for col, val in where_data.items()
        }
        updated_rows = self._filter_rows(validated_where)
        updated_rows_ids: list[int] = []
        for row in updated_rows:
            for set_column_name, set_value in validated_set.items():
                row[set_column_name] = set_value
            updated_rows_ids.append(row[AutoColumnNames.ID.value])
        return updated_rows_ids

    def _validate_value(self, column_name: str, value: Any) -> Any:
        """
        Валидация значения для колонки.

        :param column_name: название колонки.
        :param value: значение.
        :return: валидированное значение.

        :raises UnknownColumnError: если колонка не найдена.

        :raises ValueError: переданы некорректные данные.
        """
        column = self.get_column(column_name)
        return column.validate_value(value)

    def delete_row(
            self,
            where: dict
    ) -> list[int]:
        """
        Удалить строки таблицы.

        :param where: условия фильтрации вида {колонка: значение}.
        :return: список ID удаленных строк.
        """
        validated_where = {
            col: self._validate_value(col, val)
            for col, val in where.items()
        }
        deleted_rows = self._filter_rows(validated_where)
        self._rows = [row for row in self._rows if row not in deleted_rows]
        return [row[AutoColumnNames.ID.value] for row in deleted_rows]

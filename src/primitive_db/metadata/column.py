from typing import Any

from src.primitive_db.const.columns_type import ColumnsType

from .db_object import Field, Model, ValidationError
from .validator import field_validator


class ColumnTypeError(ValidationError):
    """
    Класс ошибок, возникающий при попытке создать колонку с несуществующим
    типом.
    """
    pass


_COLUMN_TYPE = {
    type_name.value: python_type
    for type_name, python_type in {
        ColumnsType.int: int,
        ColumnsType.str: str,
        ColumnsType.bool: bool
    }.items()
}


class Column(Model):
    column_type: str = Field(str, required=True, alias="type")
    column_class: type

    _python_type: type | None = None

    def __str__(self):
        return f"<Column {self.name}: {self.column_type}>"

    @field_validator("column_type")
    def column_type_validator(self, value: str):
        try:
            self._python_type = _COLUMN_TYPE[value]
        except KeyError:
            raise ColumnTypeError(f"Тип колонки {value} не поддерживается")

    @property
    def python_type(self) -> type:
        return self._python_type

    def validate_value(self, value: Any) -> _python_type:
        """
        Приведение значения к типу колонки.

        :param value: значение.
        :return: значение, приведенное к типу колонки.

        :raises ValueError: если значение не может быть приведено к типу
            колонки.
        """
        if self._python_type is bool:
            match value:
                case "true" | "True" | True | 1:
                    return True
                case "false" | "False" | False | 0:
                    return False
                case _:
                    raise ValueError("неверное значение для типа bool")
        return self._python_type(value)

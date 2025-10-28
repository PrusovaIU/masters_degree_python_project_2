from .db_object import Model, Field, ValidationError
from .validator import field_validator


class ColumnTypeError(ValidationError):
    """
    Класс ошибок, возникающий при попытке создать колонку с несуществующим
    типом.
    """
    pass


_COLUMN_TYPE = {
    "int": int,
    "str": str,
    "bool": bool
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
            raise ColumnTypeError(f"Column type {value} is not supported")

    @property
    def python_type(self) -> type:
        return self._python_type


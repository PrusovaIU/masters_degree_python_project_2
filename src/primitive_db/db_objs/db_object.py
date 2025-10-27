from collections.abc import Callable
from typing import TypeVar, Type, Any, ParamSpec
from typing import get_origin, get_args
from .validator import FieldValidator, FieldValidatorType


class DatabaseError(Exception):
    pass


class FieldValueUndefined(DatabaseError):
    pass


class ValidationError(DatabaseError):
    pass


class _NotSet:
    """
    Класс для обозначения, что значение аргумента не задано.
    """
    pass


T = TypeVar("T")


# Не стала использовать pydantic, т.к. его нет в условиях задания, и
# реализовала примитивную модель, удовлетворяющую условиям задачи:
class Field:
    """
    Описание параметра объекта базы данных.

    :param field_type: тип параметра.

    :param required: является ли параметр обязательным.

    :param default: значение по умолчанию.

    :param default_factory: фабрика значения по умолчанию.

    :param alias: имя параметра в json описании объекта. Если не задано,
        то используется имя параметра, в модели Model.
    """
    def __init__(
            self,
            field_type: Type[T],
            required: bool = False,
            default: T | None | _NotSet = _NotSet,
            default_factory: Callable[[], T] | None = None,
            alias: str | None = None
    ):
        if required and default is not _NotSet and default_factory is not None:
            raise ValueError(
                "Cannot user required and default/default_factory together."
            )
        if default is not _NotSet and default_factory is not None:
            raise ValueError(
                "Cannot user default and default_factory together."
            )
        self.field_type = field_type
        self.required = required
        self.default = default
        self.default_factory = default_factory
        self.alias = alias

    def types(self) -> tuple[ParamSpec, type] | tuple[type, None]:
        """
        Получение типов параметра.

        :return: тип параметра и тип аргумента, если параметр
            является UnionType. Иначе возвращает тип параметра и None.
        """
        origin = get_origin(self.field_type)
        if origin is None:
            return self.field_type, None
        else:
            args = get_args(self.field_type)
            return origin, args[0]


class Model:
    """
    Класс для описания объектов базы данных.

    :param name: имя объекта.
    :param kwargs: параметры объекта.
    """
    def __init__(self, name, **kwargs):
        self.name = name
        self._parse_kwargs(kwargs)

    def __str__(self):
        return f"{self.__class__.__name__}: {self.name}"

    @classmethod
    def fields(cls) -> dict[str, Field]:
        """
        :return: список полей объекта.
        """
        return {
            name: field for name, field in cls.__dict__.items()
            if isinstance(field, Field)
        }

    def _parse_kwargs(self, kwargs: dict) -> None:
        """
        Заполнение полей объекта данными из словаря.

        :param kwargs: параметры для заполнения.
        :return: None.

        :raises FieldValueUndefined: если в словаре нет требуемых параметров.

        :raises ValidationError: если в словаре некорректные параметры.
        """
        fields = self.fields()
        for key, field in fields.items():
            value = self._get_value(key, field, kwargs)
            setattr(self, key, value)


    def _get_value(self, key: str, field: Field, kwargs: dict) -> Any:
        """
        Получение значения параметра.

        :param key: имя параметра из словаря.
        :param field: описание параметра.
        :param kwargs: словарь с параметрами.
        :return: значение параметра.

        :raises FieldValueUndefined: если в словаре нет требуемых параметров.

        :raises ValidationError: если в словаре некорректные параметры.
        """
        tag = field.alias or key
        value = kwargs.get(tag)
        if value is None:
            value = self._get_default_value(key, field)
        else:
            value = self._format_custom_value(value, field)
        self._validate(value, key)
        return value

    def _get_default_value(self, key: str, field: Field) -> Any:
        """
        Получение значения по умолчанию, если значение параметра не задано в
        словаре, но задано значение по умолчанию в описании параметра.

        :param key: имя параметра.
        :param field: описание параметра.
        :return: значение параметра.

        :raises FieldValueUndefined: если в словаре нет требуемого параметра,
            и значение параметра не задано по умолчанию.
        """
        value = None
        if field.default is not _NotSet:
            value = field.default
        elif field.default_factory is not None:
            value = field.default_factory()
        elif field.required:
            raise FieldValueUndefined(
                f"Parameter \"{key}\" is required "
                f"for object \"{self.name}\"."
            )
        return value

    def _format_custom_value(self, value: Any, field: Field) -> Any:
        """
        Форматирование значения параметра.

        :param value: значение параметра.
        :param field: описание параметра.
        :return: форматированное значение параметра.

        :raises ValidationError: если значение параметра некорректно.
        """
        try:
            field_types = field.types()
            if field_types[0] is list:
                value = [field_types[1](**item) for item in value]
            else:
                value = field_types[0](value)
        except (ValueError, TypeError) as err:
            raise ValidationError(
                f"Parameter \"{err}\" for object \"{self.name}\" "
                f"is invalid: {err}"
            )
        return value

    def _validate(self, value: Any, field_name: str) -> Any:
        """
        Валидация значения параметра.

        :param value: значение параметра.
        :param field_name: имя параметра.
        :return: валидированное значение параметра.

        :raises ValidationError: если значение параметра не прошло валидацию.
        """
        class_name = self.__class__.__name__
        validator: FieldValidatorType = \
            FieldValidator.validator(class_name, field_name)
        if validator:
            try:
                value = validator(self, value)
            except Exception as err:
                raise ValidationError(
                    f"Parameter \"{field_name}\" for object \"{self.name}\" "
                    f"is invalid: {err}"
                )
        return value

from collections.abc import Callable
from re import match
from typing import Any, ParamSpec, Type, TypeVar, get_args, get_origin

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
        if not match(r"^\w+$", name):
            raise ValidationError(f"Некорректное имя объекта: {name}")
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
            value = self._get_kwargs_value(key, field, kwargs)
            setattr(self, key, value)

    def _get_kwargs_value(self, key: str, field: Field, kwargs: dict) -> Any:
        """
        Получение значения параметра из kwargs.

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
                f"Параметр \"{key}\"  обязателен"
                f"для объекта \"{self.name}\"."
            )
        return value

    def _format_custom_value(self, value: Any, field: Field) -> Any:
        """
        Приведение значения параметра к требуемому типу.

        :param value: значение параметра.
        :param field: описание параметра.
        :return: форматированное значение параметра.

        :raises ValidationError: если значение параметра некорректно.
        """
        try:
            field_types = field.types()
            if field_types[0] is list:
                value = self._handle_list(value, field_types[1])
            else:
                value = field_types[0](value)
        except (ValueError, TypeError) as err:
            raise ValidationError(
                f"Невалидный параметр \"{err}\" для объекта \"{self.name}\": "
                f"{err}"
            )
        return value

    def _handle_list(self, value: list, list_arg: Type[T]) -> list[T]:
        """
        Обработка списка значений.

        :param value: Список значений.
        :param list_arg: Требуемый тип элементов списка.
        :return: Обработанный список значений.

        :raises ValidationError: если в списке присутствуют некорректные
            значения.
        """
        handled_values = []
        for i, item in enumerate(value):
            if isinstance(item, dict):
                handled_values.append(list_arg(**item))
            elif isinstance(item, list_arg):
                handled_values.append(item)
            else:
                raise ValidationError(
                    f"Параметр [\"{i}\"] для объекта \"{self.name}\" "
                    f"должен быть экземпляром класса \"{list_arg}\"."
                )
        return handled_values

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
                    f"Невалидный параметр \"{field_name}\" для объекта "
                    f"\"{self.name}\": {err}"
                )
        return value

    def dumps(self) -> dict:
        """
        Получение словаря с описанием объекта.

        :return: словарь с описанием объекта.
        """
        data = {"name": self.name}
        for name, field in self.fields().items():
            tag = field.alias or name
            value = getattr(self, name)
            if isinstance(value, list):
                value = [self._dumps_value(item) for item in value]
            else:
                value = self._dumps_value(value)
            data[tag] = value
        return data

    @staticmethod
    def _dumps_value(value: Any) -> Any:
        """
        Форматирование значения параметра для json.

        :param value: значение параметра.
        :return: форматированное значение параметра.
        """
        if isinstance(value, Model):
            return value.dumps()
        else:
            return value

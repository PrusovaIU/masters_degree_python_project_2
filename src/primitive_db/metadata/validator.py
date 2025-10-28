from collections.abc import Callable
from typing import Any, TypeVar


T = TypeVar('T')

FieldValidatorType = Callable[[T, Any], Any]
_ClassValidatorsType = dict[str, FieldValidatorType]
_ValidatorsType = dict[str, _ClassValidatorsType]


class FieldValidator:
    """
    Класс для регистрации валидаторов полей.

    :param field_name: имя поля для валидации.

    Пример использования:

        from metadata.db_object import Model

        class MyClass(Model):

            @field_validator('field_name')
            def validate_field(self, value: Any) -> Any:
                if isinstance(value, int):
                    return value + 1
                return value
    """
    # список валидаторов:
    _validators: _ValidatorsType = {}

    def __init__(self, field_name: str):
        self._field_name = field_name

    def __call__(self, func: FieldValidatorType):
        """
        Регистрация валидатора.

        :param func: функция-валидатор.
        :return: func без изменений.
        """
        class_name = func.__qualname__.split('.')[0]
        self._validators.setdefault(class_name, {})
        self._validators[class_name][self._field_name] = func
        return func

    @classmethod
    def validator(
            cls,
            class_name: str,
            field_name: str
    ) -> FieldValidatorType | None:
        """
        Получить валидатор для поля класса.

        :param class_name: имя класса.
        :param field_name: имя поля.
        :return: валидатор для поля, если он определен, иначе None.
        """
        if class_name in cls._validators:
            return cls._validators[class_name].get(field_name)
        else:
            return None

field_validator = FieldValidator

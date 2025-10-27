from collections import Counter
from collections.abc import Callable
from enum import Enum
from json import dumps
from typing import TypeVar, Type, Any, ParamSpec
from dataclasses import dataclass
from typing import get_origin, get_args
from types import UnionType


class DatabaseError(Exception):
    pass


class FieldValueUndefined(DatabaseError):
    pass


class ValidationError(DatabaseError):
    pass


class _NotSet:
    pass


# Не стала использовать pydantic, т.к. его нет в условиях задания:
class Field:
    """
    Описание параметра объекта базы данных.

    :param field_type: тип параметра.
    :param required: является ли параметр обязательным.
    """
    def __init__(
            self,
            field_type,
            required: bool = False,
            default: Any = _NotSet,
            default_factory: Callable[[], Any] | None = None,
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
        tag = field.alias or key
        value = kwargs.get(tag)
        if value is None:
            value = self._get_default_value(key, field)
        else:
            value = self._format_custom_value(value, field)
        return value

    def _get_default_value(self, key: str, field: Field) -> Any:
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
        try:
            field_types = field.types()
            if field_types[0] is list:
                value = [field_types[1](**item) for item in value]
            else:
                value = field_types[0](value)
        except (ValueError, TypeError) as err:
            raise ValidationError(
                f"Parameter \"{err}\" for object \"{self.name}\" is invalid."
            )
        return value



# class DBObjectParseJsonError(DatabaseError):
#     """
#     Базовый класс для ошибок, связанных с парсингом json описания объекта.
#     """
#     pass
#
#
# class JsonTagAbsentError(DatabaseError):
#     """
#     Ошибка, возникающая при отсутствии тега в json описании объекта.
#     """
#     pass
#
#
# class JsonValueError(DatabaseError):
#     """
#     Ошибка, возникающая при некорректном значении тега в json описании объекта.
#     """
#     pass
#
#
# class DuplicatesError(JsonValueError):
#     """
#     Ошибка, возникающая при наличии дубликатов имен объектов.
#     """
#     pass
#
#
# class DBObjectJsonTag(Enum):
#     """
#     Теги, используемые для описания объектов базы данных в json.
#     """
#     name = "name"
#
#
# T = TypeVar("T")

# @dataclass
# class Field:
#     """
#     Описание параметра объекта базы данных.
#
#     :param kwarg_name: имя параметра в методе __init__.
#     :param json_tag: имя тега в json описании объекта.
#     :param field_type: тип параметра.
#     :param required: является ли параметр обязательным.
#     """
#     json_tag: str
#     field_type: type
#     required: bool
#
#     def types(self) -> tuple[type, ...]:
#         origin = get_origin(self.field_type)
#         if origin is None:
#             return (self.field_type,)
#         else:
#             args = get_args(self.field_type)
#             return (origin, args[0])
#
#
# VALIDATORS: dict[str, dict[str, Callable]] = {}
#
#
# def param_validator(param_name: str):
#     def decorator(func: Callable[[Any], Any]):
#         class_name = func.__qualname__.split(".")[0]
#         VALIDATORS.setdefault(class_name, {})
#         VALIDATORS[class_name][param_name] = func
#         return func
#     return decorator
#
#
# class BaseDBObject:
#     """
#     Базовый класс для всех объектов базы данных.
#
#     :param name: Название объекта.
#     """
#     def __init__(self, name: str, **kwargs):
#         self._name = name
#         for name, value in kwargs.items():
#             if name in VALIDATORS.get(self.__class__.__name__, {}):
#                 value = VALIDATORS[self.__class__.__name__][name](self, value)
#             setattr(self, name, value)
#
#     @property
#     def name(self) -> str:
#         return self._name
#
#     @classmethod
#     def parameters(cls) -> dict[str, Field]:
#         return {
#             name: param for name, param in cls.__dict__.items()
#             if isinstance(param, Field)
#         }
#
#     @staticmethod
#     def _check_duplicates(
#             objs: list["BaseDBObject"]
#     ) -> bool:
#         """
#         Проверка на дубликаты имен объектов.
#
#         :param objs: список объектов.
#         :return: True, если есть дубликаты имен объектов, иначе False.
#         """
#         name_counts = Counter(obj.name for obj in objs)
#         duplicates = [name for name, count in name_counts.items() if count > 1]
#         return len(duplicates) > 0
#
#
#     @classmethod
#     def _list_included_objs(
#             cls,
#             json_data: list[dict],
#             field: Field
#     ) -> list["BaseDBObject"]:
#         """
#         Парсинг списка сущностей для конкретного объекта из cls.included_objs.
#
#         :param json_data: json описание сущностей.
#         :param obj: описание сущности.
#         :return: список сущностей.
#
#         :raises JsonValueError: если в json_data некорректное значение
#             какого-либо тега.
#
#         :raises DuplicatesError: если в json_data есть сущности с одинаковым
#             именем.
#         """
#         if not isinstance(json_data, list):
#             raise JsonValueError(
#                 f"Tag \"{field.json_tag}\" must be a list, not "
#                 f"{json_data.__class__.__name__}: {dumps(json_data)}"
#             )
#         if len(json_data) == 0 and field.required:
#             raise JsonValueError(
#                 f"Tag \"{field.json_tag}\" must not be empty: "
#                 f"{dumps(json_data)}"
#             )
#         objs = [obj.type.from_json(item) for item in json_data]
#         if cls._check_duplicates(objs):
#             raise DuplicatesError(
#                 f"Tag \"{obj.json_tag}\" must not contain duplicates: "
#                 f"{dumps(json_data)}"
#             )
#         return objs
#
#     def _parse_param(self, name: str, param: Field, value: Any) -> Any:
#         param_types = param.types()
#         if param_types[0] is list:
#
#
#     @classmethod
#     def _parse_kwargs(cls, json_data: dict) -> dict[str, Any]:
#         """
#         Парсинг параметров, перечисленных в методе parameters, из json
#         описания объекта.
#
#         :param json_data: описание объекта в json.
#         :return: список пар "имя_параметра": "значение_параметра".
#
#         :raises JsonTagAbsentError: если в json_data отсутствует тег,
#             описанный в методе parameters.
#
#         :raises JsonValueError: если в json_data некорректное значение
#             какого-либо тега.
#         """
#         kwargs = {}
#         try:
#             for name, param in cls.parameters().items():
#                 if param.json_tag not in json_data and param.required:
#                     raise JsonTagAbsentError(
#                         f"There is no tag \"{param.json_tag}\" in json data: "
#                         f"{dumps(json_data)}"
#                     )
#                 value = json_data.get(param.json_tag)
#                 kwargs[name] = param.field_type(value)
#         except ValueError:
#             raise JsonValueError(
#                 f"Tag \"{param.json_tag}\" must be a {param.field_type.__name__}: "
#                 f"{dumps(json_data)}"
#             )
#         return kwargs
#
#     @classmethod
#     def from_json(cls: Type[T], json_data: dict) -> T:
#         """
#         Создание экземпляра класса из json описания объекта.
#
#         :param json_data: описание объекта в json.
#         :return: новый экземпляр класса.
#
#         :raises DBObjectParseJsonError: если не удалось создать объект из
#             json описания.
#         """
#         if not isinstance(json_data, dict):
#             raise JsonValueError(
#                 f"Database object metadata must be a dict, not "
#                 f"{json_data.__class__.__name__}: {dumps(json_data)}"
#             )
#         try:
#             name = json_data[DBObjectJsonTag.name.value]
#             kwargs: dict[str, Any] = cls._parse_kwargs(json_data)
#         except KeyError as err:
#             raise JsonTagAbsentError(
#                 f"There is tag \"{err}\" in json data: {dumps(json_data)}"
#             )
#         return cls(name, **kwargs)
#
#     def to_json(self) -> dict:
#         """
#         Формирование словаря с описанием объекта.
#
#         :return: описание объекта.
#         """
#         params = {
#             param.json_tag: getattr(self, name, None)
#             for name, param in self.parameters().items()
#         }
#         params[DBObjectJsonTag.name.value] = self._name
#         return params
#
#
# class IncludedObject(Field):
#     """
#     Описание объекта, который может быть включен в другой объект.
#
#     Например, описание колонки таблицы.
#     """
#     field_type: Type[BaseDBObject]
#
#
# class DBObject(BaseDBObject):
#     """
#     Базовый класс для объектов базы данных, которые могут включать в себя
#     другие объекты.
#
#     Например, описание таблицы базы данных.
#
#     """
#     @classmethod
#     def included_objs(cls) -> dict[str, IncludedObject]:
#         return {
#             name: obj for name, obj in cls.__dict__.items()
#             if isinstance(obj, IncludedObject)
#         }
#
#     @staticmethod
#     def _check_duplicates(
#             objs: list[BaseDBObject]
#     ) -> bool:
#         """
#         Проверка на дубликаты имен объектов.
#
#         :param objs: список объектов.
#         :return: True, если есть дубликаты имен объектов, иначе False.
#         """
#         name_counts = Counter(obj.name for obj in objs)
#         duplicates = [name for name, count in name_counts.items() if count > 1]
#         return len(duplicates) > 0
#
#
#     @classmethod
#     def _list_included_objs(
#             cls,
#             json_data: list[dict],
#             obj: IncludedObject
#     ) -> list[BaseDBObject]:
#         """
#         Парсинг списка сущностей для конкретного объекта из cls.included_objs.
#
#         :param json_data: json описание сущностей.
#         :param obj: описание сущности.
#         :return: список сущностей.
#
#         :raises JsonValueError: если в json_data некорректное значение
#             какого-либо тега.
#
#         :raises DuplicatesError: если в json_data есть сущности с одинаковым
#             именем.
#         """
#         if not isinstance(json_data, list):
#             raise JsonValueError(
#                 f"Tag \"{obj.json_tag}\" must be a list, not "
#                 f"{json_data.__class__.__name__}: {dumps(json_data)}"
#             )
#         if len(json_data) == 0 and obj.required:
#             raise JsonValueError(
#                 f"Tag \"{obj.json_tag}\" must not be empty: {dumps(json_data)}"
#             )
#         objs = [obj.type.from_json(item) for item in json_data]
#         if cls._check_duplicates(objs):
#             raise DuplicatesError(
#                 f"Tag \"{obj.json_tag}\" must not contain duplicates: "
#                 f"{dumps(json_data)}"
#             )
#         return objs
#
#     @classmethod
#     def _parse_included_objs(cls, json_data: dict) -> dict[str, Any]:
#         """
#         Парсинг сущностей, перечисленных в методе included_objs, из json
#         описания объекта.
#
#         :param json_data: json описание объекта.
#         :return: список пар "имя_сущности": "значение_сущности".
#
#         :raises DBObjectParseJsonError: если не удалось создать объект из
#             json описания.
#         """
#         objects = {}
#         for name, obj in cls.included_objs().items():
#             if obj.json_tag not in json_data and obj.required:
#                 raise JsonTagAbsentError(
#                     f"There is no tag \"{obj.json_tag}\" in json data: "
#                     f"{dumps(json_data)}"
#                 )
#             tag_value = json_data.get(obj.json_tag)
#             if tag_value is not None:
#                 objects[name] = cls._list_included_objs(tag_value, obj)
#         return objects
#
#     @classmethod
#     def _parse_kwargs(cls, json_data: dict) -> dict[str, Any]:
#         """
#         Парсинг параметров, перечисленных в методе parameters, из json
#         описания объекта и параметров, перечисленных в методе included_objs.
#
#         :param json_data: json описание объекта.
#         :return: список пар "имя_параметра": "значение_параметра".
#         """
#         kwargs = super()._parse_kwargs(json_data)
#         kwargs.update(cls._parse_included_objs(json_data))
#         return kwargs
#
#     def to_json(self) -> dict:
#         params = super().to_json()
#         for name, obj in self.included_objs().items():
#             params[obj.json_tag] = [
#                 i.to_json() for i in getattr(self, name, [])
#             ]
#         return params

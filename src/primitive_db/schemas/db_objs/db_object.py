from collections import Counter
from enum import Enum
from json import dumps
from typing import TypeVar, Type, Any
from dataclasses import dataclass


class DatabaseError(Exception):
    pass


class DBObjectParseJsonError(DatabaseError):
    """
    Базовый класс для ошибок, связанных с парсингом json описания объекта.
    """
    pass


class JsonTagAbsentError(DatabaseError):
    """
    Ошибка, возникающая при отсутствии тега в json описании объекта.
    """
    pass


class JsonValueError(DatabaseError):
    """
    Ошибка, возникающая при некорректном значении тега в json описании объекта.
    """
    pass


class DuplicateNameError(JsonValueError):
    """
    Ошибка, возникающая при наличии дубликатов имен объектов.
    """
    pass


class DBObjectJsonTag(Enum):
    """
    Теги, используемые для описания объектов базы данных в json.
    """
    name = "name"


T = TypeVar("T")


@dataclass
class DBObjectParam:
    """
    Описание параметра объекта базы данных.

    :param kwarg_name: имя параметра в методе __init__.
    :param json_tag: имя тега в json описании объекта.
    :param type: тип параметра.
    :param required: является ли параметр обязательным.
    """
    kwarg_name: str
    json_tag: str
    type: Type
    required: bool


class BaseDBObject:
    """
    Базовый класс для всех объектов базы данных.

    :param name: Название объекта.
    """
    def __init__(self, name: str, *args, **kwargs):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @classmethod
    def parameters(cls) -> list[DBObjectParam]:
        """
        Переопределите данный метод, чтобы указать параметры, которые должны
        быть получены из json описания объекта.

        Пример:
        [
            DBObjectParam("name", "name", str, True),
            DBObjectParam("age", "age", int, False)
        ]

        Ожидаемый json описания объекта:
        {
            "name": "John",
            "age": 25
        }

        :return: список описаний параметров.
        """
        return []

    @classmethod
    def _parse_kwargs(cls, json_data: dict) -> dict[str, Any]:
        """
        Парсинг параметров, перечисленных в методе parameters, из json
        описания объекта.

        :param json_data: описание объекта в json.
        :return: список пар "имя_параметра": "значение_параметра".

        :raises JsonTagAbsentError: если в json_data отсутствует тег,
            описанный в методе parameters.

        :raises JsonValueError: если в json_data некорректное значение
            какого-либо тега.
        """
        kwargs = {}
        try:
            for param in cls.parameters():
                if param.json_tag not in json_data and param.required:
                    raise JsonTagAbsentError(
                        f"There is no tag \"{param.json_tag}\" in json data: "
                        f"{dumps(json_data)}"
                    )
                value = json_data.get(param.json_tag)
                kwargs[param.kwarg_name] = param.type(value)
        except ValueError:
            raise JsonValueError(
                f"Tag \"{param.json_tag}\" must be a {param.type.__name__}: "
                f"{dumps(json_data)}"
            )
        return kwargs

    @classmethod
    def from_json(cls: Type[T], json_data: dict) -> T:
        """
        Создание экземпляра класса из json описания объекта.

        :param json_data: описание объекта в json.
        :return: новый экземпляр класса.

        :raises DBObjectParseJsonError: если не удалось создать объект из
            json описания.
        """
        if not isinstance(json_data, dict):
            raise JsonValueError(
                f"Database object metadata must be a dict, not "
                f"{json_data.__class__.__name__}: {dumps(json_data)}"
            )
        try:
            name = json_data[DBObjectJsonTag.name.value]
            kwargs: dict[str, Any] = cls._parse_kwargs(json_data)
        except KeyError as err:
            raise JsonTagAbsentError(
                f"There is tag \"{err}\" in json data: {dumps(json_data)}"
            )
        return cls(name, **kwargs)


class IncludedObject(DBObjectParam):
    """
    Описание объекта, который может быть включен в другой объект.

    Например, описание колонки таблицы.
    """
    type: Type[BaseDBObject]


class DBObject(BaseDBObject):
    """
    Базовый класс для объектов базы данных, которые могут включать в себя
    другие объекты.

    Например, описание таблицы базы данных.

    """
    @classmethod
    def included_objs(cls) -> list[IncludedObject]:
        """
        Переопределите данный метод, чтобы указать список сущностей, включенных
        в данный объект.

        Пример:
        [
            IncludedObject("columns", "columns", Column, True)
        ]

        где Column - класс, описывающий колонку таблицы и имеющий json
        описание типа:
        {
            "name": "id",
            "type": "int"
        }.

        Ожидаемый json описания объекта:

        {
            "columns": [
                [
                        {
                            "name": "id",
                            "type": "int"
                        },
                        {
                            "name": "name",
                            "type": "str"
                        }
                ]
            ]
        }

        :return: список описаний объектов.
        """
        return []

    @staticmethod
    def _check_duplicates(
            objs: list[BaseDBObject],
            obj: IncludedObject,
            json_data: list
    ) -> None:
        """
        Проверка на дубликаты имен объектов.

        :param objs: список объектов.
        :param obj: описание объекта.
        :param json_data: json описание объектов.
        :return: None.
        """
        name_counts = Counter(obj.name for obj in objs)
        duplicates = [name for name, count in name_counts.items() if count > 1]
        if duplicates:
            raise DuplicateNameError(
                f"Tag \"{obj.json_tag}\" must not contain duplicates: "
                f"{dumps(json_data)}"
            )


    @classmethod
    def _list_included_objs(
            cls,
            json_data: list[dict],
            obj: IncludedObject
    ) -> list[BaseDBObject]:
        """
        Парсинг списка сущностей для конкретного объекта из cls.included_objs.

        :param json_data: json описание сущностей.
        :param obj: описание сущности.
        :return: список сущностей.

        :raises JsonValueError: если в json_data некорректное значение
            какого-либо тега.

        :raises DuplicateNameError: если в json_data есть сущности с одинаковым
            именем.
        """
        if not isinstance(json_data, list):
            raise JsonValueError(
                f"Tag \"{obj.json_tag}\" must be a list, not "
                f"{json_data.__class__.__name__}: {dumps(json_data)}"
            )
        if len(json_data) == 0 and obj.required:
            raise JsonValueError(
                f"Tag \"{obj.json_tag}\" must not be empty: {dumps(json_data)}"
            )
        objs = [obj.type.from_json(item) for item in json_data]
        cls._check_duplicates(objs, obj, json_data)
        return objs

    @classmethod
    def _parse_included_objs(cls, json_data: dict) -> dict[str, Any]:
        """
        Парсинг сущностей, перечисленных в методе included_objs, из json
        описания объекта.

        :param json_data: json описание объекта.
        :return: список пар "имя_сущности": "значение_сущности".

        :raises DBObjectParseJsonError: если не удалось создать объект из
            json описания.
        """
        objects = {}
        for obj in cls.included_objs():
            if obj.json_tag not in json_data and obj.required:
                raise JsonTagAbsentError(
                    f"There is no tag \"{obj.json_tag}\" in json data: "
                    f"{dumps(json_data)}"
                )
            tag_value = json_data.get(obj.json_tag)
            if tag_value is not None:
                objects[obj.kwarg_name] = \
                    cls._list_included_objs(tag_value, obj)
        return objects

    @classmethod
    def _parse_kwargs(cls, json_data: dict) -> dict[str, Any]:
        """
        Парсинг параметров, перечисленных в методе parameters, из json
        описания объекта и параметров, перечисленных в методе included_objs.

        :param json_data: json описание объекта.
        :return: список пар "имя_параметра": "значение_параметра".
        """
        kwargs = super()._parse_kwargs(json_data)
        kwargs.update(cls._parse_included_objs(json_data))
        return kwargs

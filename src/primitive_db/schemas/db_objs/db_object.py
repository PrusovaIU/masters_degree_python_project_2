from enum import Enum
from json import dumps
from typing import TypeVar, Type, Any
from dataclasses import dataclass


class DatabaseError(Exception):
    pass


class DBObjectParseJsonError(DatabaseError):
    pass


class DBObjectJsonTag(Enum):
    name = "name"


T = TypeVar("T")


@dataclass
class DBObjectParam:
    kwarg_name: str
    json_tag: str
    type: Type
    required: bool


class BaseDBObject:
    def __init__(self, name: str, *args, **kwargs):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    @classmethod
    def parameters(cls) -> list[DBObjectParam]:
        return []

    @classmethod
    def _parse_kwargs(cls, json_data: dict) -> dict[str, Any]:
        kwargs = {}
        try:
            for param in cls.parameters():
                if param.json_tag not in json_data and param.required:
                    raise DBObjectParseJsonError(
                        f"There is no tag \"{param.json_tag}\" in json data: "
                        f"{dumps(json_data)}"
                    )
                value = json_data.get(param.json_tag)
                kwargs[param.kwarg_name] = param.type(value)
        except ValueError:
            raise DBObjectParseJsonError(
                f"Tag \"{param.json_tag}\" must be a {param.type.__name__}: "
                f"{dumps(json_data)}"
            )
        return kwargs

    @classmethod
    def from_json(cls: Type[T], json_data: dict) -> T:
        if not isinstance(json_data, dict):
            raise DBObjectParseJsonError(
                f"Database object metadata must be a dict, not "
                f"{json_data.__class__.__name__}: {dumps(json_data)}"
            )
        try:
            name = json_data[DBObjectJsonTag.name.value]
            kwargs: dict[str, Any] = cls._parse_kwargs(json_data)
        except KeyError as err:
            raise DBObjectParseJsonError(
                f"There is tag \"{err}\" in json data: {dumps(json_data)}"
            )
        return cls(name, **kwargs)


class IncludedObject(DBObjectParam):
    type: Type[BaseDBObject]


class DBObject(BaseDBObject):
    @classmethod
    def included_objs(cls) -> list[IncludedObject]:
        return []

    @classmethod
    def _list_included_objs(
            cls,
            json_data: list[dict],
            obj: IncludedObject
    ) -> list[BaseDBObject]:
        if not isinstance(json_data, list):
            raise DBObjectParseJsonError(
                f"Tag \"{obj.json_tag}\" must be a list, not "
                f"{json_data.__class__.__name__}: {dumps(json_data)}"
            )
        if len(json_data) == 0 and obj.required:
            raise DBObjectParseJsonError(
                f"Tag \"{obj.json_tag}\" must not be empty: {dumps(json_data)}"
            )
        return [obj.type.from_json(item) for item in json_data]

    @classmethod
    def _parse_included_objs(cls, json_data: dict) -> dict[str, Any]:
        objects = {}
        for obj in cls.included_objs():
            if obj.json_tag not in json_data and obj.required:
                raise DBObjectParseJsonError(
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
        kwargs = super()._parse_kwargs(json_data)
        kwargs.update(cls._parse_included_objs(json_data))
        return kwargs

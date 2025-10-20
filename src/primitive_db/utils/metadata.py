from pathlib import Path
from src.primitive_db.schemas.db_meta import Database
from json import load, JSONDecodeError
from loguru import logger


class GetMetadataError(Exception):
    pass


class MetadataFileError(GetMetadataError):
    pass


class MetadataTypeError(GetMetadataError):
    pass


def _open_file(filepath: Path) -> dict:
    """
    Чтение метаданных из файла.

    :param filepath: путь к файлу.
    :return: словарь с метаданными.

    :raises GetMetadataError: если не удалось получить метаданные.
    """
    try:
        with filepath.open() as file:
            data = load(file)
    except (OSError, JSONDecodeError) as err:
        raise MetadataFileError(
            f"Cannot get metadata from {filepath}: "
            f"{err} ({err.__class__.__name__})"
        )
    return data


def _parse_metadata(data: dict) -> Database:
    if not isinstance(data, dict):
        raise MetadataTypeError(
            f"Metadata in file must be an object, "
            f"but {data.__class__.__name__} was given"
        )



def load_metadata(filepath: Path) -> Database:


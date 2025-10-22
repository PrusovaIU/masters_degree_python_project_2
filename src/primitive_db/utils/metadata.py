from pathlib import Path
from src.primitive_db.schemas.db_meta import Database
from json import load, JSONDecodeError, dump


class GetMetadataError(Exception):
    pass


class MetadataFileError(GetMetadataError):
    pass


def load_metadata(filepath: Path) -> Database:
    """
    Загрузка метаданных о базе данных.

    :param filepath: путь до файла с метаданными.
    :return: словарь с метаданными.

    :raises GetMetadataError: если не удалось загрузить метаданные.
    """
    if not filepath.exists():
        return {}
    try:
        with filepath.open() as file:
            data = load(file)
    except (OSError, JSONDecodeError) as err:
        raise MetadataFileError(
            f"Cannot get metadata from {filepath}: "
            f"{err} ({err.__class__.__name__})"
        )
    return data


def save_metadata(filepath: Path, data: dict) -> None:
    """
    Сохранение метаданных о базе данных.

    :param filepath: путь до файла с метаданными.
    :param data: метаданные.
    :return: None.
    :raises MetadataFileError: если не удалось сохранить метаданные.
    """
    try:
        with filepath.open("w") as file:
            dump(data, file, indent=4, ensure_ascii=False)
    except OSError as err:
        raise MetadataFileError(
            f"Cannot save metadata to {filepath}: "
            f"{err} ({err.__class__.__name__})"
        )


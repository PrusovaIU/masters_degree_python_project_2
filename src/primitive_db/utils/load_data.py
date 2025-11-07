from json import JSONDecodeError, dump, load
from pathlib import Path


class LoadDataError(Exception):
    pass


class SaveDataError(Exception):
    pass


def load_data(filepath: Path) -> dict | list:
    """
    Загрузка данных из файла.

    :param filepath: путь до файла с данными.
    :return: словарь с данными.

    :raises LoadDataError: если не удалось загрузить данные.
    """
    try:
        with filepath.open() as file:
            data = load(file)
    except (OSError, JSONDecodeError) as err:
        raise LoadDataError(
            f"Не удалось загрузить метаданные из файла {filepath}: "
            f"{err} ({err.__class__.__name__})"
        )
    return data


def save_data(filepath: Path, data: dict | list) -> None:
    """
    Сохранение данных в файл.

    :param filepath: путь до файла с данными.
    :param data: словарь с данными.

    :return: None.
    :raises SaveDataError: если не удалось сохранить данные.
    """
    try:
        with filepath.open("w") as file:
            dump(data, file, indent=4, ensure_ascii=False)
    except OSError as err:
        raise SaveDataError(
            f"Не удалось сохранить метаданные в файл {filepath}: "
            f"{err} ({err.__class__.__name__})"
        )

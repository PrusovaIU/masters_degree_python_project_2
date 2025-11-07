from collections.abc import Callable
from src.primitive_db.metadata.db_object import DatabaseError
from .load_data import SaveDataError
from src.primitive_db.exceptions.command_error import CommandError


def handle_db_errors(func: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as err:
            print(f"Введены некорректные данные: {err}")
        except DatabaseError as err:
            print(f"Не удалось выполнить операцию: {err}")
        except SaveDataError as err:
            print(f"Не удалось сохранить данные: {err}")
        except CommandError as err:
            print(f"Некорректная команда: {err}")
    return wrapper

from collections.abc import Callable
from src.primitive_db.metadata.db_object import DatabaseError
from .load_data import SaveDataError
from src.primitive_db.exceptions.command_error import CommandError
import prompt
from re import Match
from .parser import ParserError
from src.primitive_db.exceptions.cancelled_error import CancelledError


def handle_db_errors(func: Callable) -> Callable:
    """Обертка для обработки ошибок базы данных."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (ValueError, ParserError) as err:
            print(f"Введены некорректные данные: {err}")
        except DatabaseError as err:
            print(f"Не удалось выполнить операцию: {err}")
        except SaveDataError as err:
            print(f"Не удалось сохранить данные: {err}")
        except CommandError as err:
            print(f"Некорректная команда: {err}")
    return wrapper


def confirm_action(action_name: str) -> Callable:
    """
    Обертка для подтверждения действия.

    :param action_name: название действия.
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            matching: Match = prompt.regex(
                r"^(y|n)$",
                f"Вы уверены, что хотите выполнить "
                f"\"{action_name}\"? [y/n]: "
            )
            if matching.string == "y":
                return func(*args, **kwargs)
            else:
                raise CancelledError(f"Операция \"{action_name}\" отменена.")
        return wrapper
    return decorator

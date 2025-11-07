from collections.abc import Callable


def create_cacher(size: int = 10) -> Callable:
    """
    Обертка для кэширования результатов вызова функций.

    Не стала применять к select по требованию задания, т.к. select не может
    быть кэшируемым, потому что между вызовами могут произойти изменения в БД.

    :param size: размер кэша.
    """
    cache = {}
    def decorator(func: Callable) -> Callable:
        def cache_result(*args, **kwargs):
            key = (args, tuple(kwargs.items()))
            if key in cache:
                return cache[key]
            else:
                result = func(*args, **kwargs)
                if len(cache) >= size:
                    cache.popitem()
                cache[key] = result
                return result
        return cache_result
    return decorator

from collections import Counter

from src.primitive_db.metadata.db_object import Model


def get_duplicates(lst: list[Model]) -> list[str]:
    """
    Получение списка дубликатов (по имени).

    :param lst: список объектов для проверки.
    :return: список имен дубликатов, если есть. Иначе пустой список.
    """
    name_counts = Counter(obj.name for obj in lst)
    duplicates = [name for name, count in name_counts.items() if count > 1]
    return duplicates

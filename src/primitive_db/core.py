from src.primitive_db.db_objs import Database, Table
from src.primitive_db.db_objs.column import Column
from src.primitive_db.utils.metadata import save_metadata
from src.primitive_db.conf import CONFIG


def _create_columns(columns: list[str]) -> list[Column]:
    column_objs = []
    for column in columns:
        column_name, column_type = column.split(":")
        column_objs.append(
            Column(column_name.strip(), type=column_type.strip())
        )
    return column_objs


def create_table(
        database: Database,
        table_name: str,
        columns: list[str]
) -> None:
    """
    Обработка команды создания таблицы.

    :param database: описание базы данных.
    :param table_name: имя таблицы.
    :param columns: список строк с описанием колонок вида имя:тип.

    :return: None.

    :raises db_objs.db_object.DatabaseError: если не удалось создать таблицу.

    :raises utils.metadata.MetadataError: если не удалось сохранить метаданные.
    """
    column_objs = _create_columns(columns)
    table = Table(table_name, columns=column_objs)
    database.add_table(table)
    save_metadata(CONFIG.db_metadata_path, database.dumps())


def drop_table(database: Database, table_name: str) -> None:
    """
    Обработка команды удаления таблицы.

    :param database: описание базы данных.
    :param table_name: имя таблицы.

    :return: None.

    :raises db_objs.db_object.DatabaseError: если не удалось удалить таблицу.

    :raises utils.metadata.MetadataError: если не удалось сохранить метаданные.
    """
    database.drop_table(table_name)
    save_metadata(CONFIG.db_metadata_path, database.to_json())

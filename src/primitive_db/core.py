from db_objs import Database, Table
from db_objs.column import Column, ColumnTypeError
from utils.metadata import save_metadata
from conf import CONFIG


def _create_columns(columns: list[str]) -> list[Column]:
    column_objs = []
    for column in columns:
        column_name, column_type = column.split(":")
        column_objs.append(
            Column(column_name, column_type)
        )
    return column_objs


def create_table(
        metadata: Database,
        table_name: str,
        columns: list[str]
) -> None:
    """
    Обработка команды создания таблицы.

    :param metadata: описание базы данных.
    :param table_name: имя таблицы.
    :param columns: список строк с описанием колонок вида имя:тип.

    :return: None.

    :raises db_objs.db_object.DatabaseError: если не удалось создать таблицу.
    """
    column_objs = _create_columns(columns)
    table = Table(table_name, column_objs)
    metadata.add_table(table)
    save_metadata(CONFIG.db_metadata_path, metadata.to_json())


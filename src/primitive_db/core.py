from pathlib import Path

from src.primitive_db.metadata import Database, Table
from src.primitive_db.metadata.column import Column
from src.primitive_db.utils.metadata import save_metadata, load_metadata
from src.primitive_db.conf import CONFIG
from src.primitive_db.const.columns_type import ColumnsType


class Core:
    """
    Класс, реализующий функционал ядра базы данных.

    :param metadata_path: путь к файлу с метаданными.
    """
    def __init__(self, metadata_path: Path):
        self._metadata_path = metadata_path
        self._database_meta = self._get_database_meta(metadata_path)

    @staticmethod
    def _get_database_meta(metadata_path: Path) -> Database:
        """
        Получение описания базы данных из файла метаданных.

        :param metadata_path: путь к файлу метаданных.
        :return: описание базы данных.
        """
        if metadata_path.exists():
            metadata: dict = load_metadata(metadata_path)
            database = Database(**metadata)
        else:
            database_name: str = metadata_path.name.split(".")[0]
            database = Database(database_name)
            save_metadata(metadata_path, database.dumps())
        return database

    def create_table(
            self,
            table_name: str,
            columns: list[tuple[str, str]]
    ) -> Table:
        """
        Обработка команды создания таблицы.

        :param database: описание базы данных.
        :param table_name: имя таблицы.
        :param columns: список с описанием колонок вида [имя, тип].

        :return: None.

        :raises metadata.db_object.DatabaseError: если не удалось создать
            таблицу.

        :raises utils.metadata.MetadataError: если не удалось сохранить
            метаданные.
        """
        column_objs = [
            Column(column_name.strip(), type=column_type.strip())
            for column_name, column_type in columns
        ]
        column_objs.insert(
            0,
            Column("ID", type=ColumnsType.int.value)
        )
        table = Table(table_name, columns=column_objs)
        self._database_meta.add_table(table)
        save_metadata(CONFIG.db_metadata_path, self._database_meta.dumps())
        return table

    def list_tables(self) -> list[Table]:
        """
        :return: список таблиц базы данных.
        """
        return self._database_meta.tables

    def drop_table(self, table_name: str) -> None:
        """
        Обработка команды удаления таблицы.

        :param database: описание базы данных.
        :param table_name: имя таблицы.

        :return: None.

        :raises metadata.db_object.DatabaseError: если не удалось удалить
            таблицу.

        :raises utils.metadata.MetadataError: если не удалось сохранить
            метаданные.
        """
        self._database_meta.drop_table(table_name)
        save_metadata(CONFIG.db_metadata_path, self._database_meta.dumps())

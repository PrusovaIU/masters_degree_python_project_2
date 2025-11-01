from pathlib import Path

from src.primitive_db.metadata import Database, Table
from src.primitive_db.metadata.column import Column
from src.primitive_db.utils.load_data import save_data, load_data
from src.primitive_db.const.columns_type import ColumnsType


class Core:
    """
    Класс, реализующий функционал ядра базы данных.

    :param metadata_path: путь к файлу с метаданными.
    """
    def __init__(self, database_path: Path):
        self._database_path = database_path
        self._database_meta_path = database_path / "metadata.json"
        self._database = self._get_database_meta(self._database_meta_path)
        for table in self._database.tables:
            self._get_table_data(table)

    @staticmethod
    def _get_database_meta(metadata_path: Path) -> Database:
        """
        Получение описания базы данных из файла метаданных.

        :param metadata_path: путь к файлу метаданных.
        :return: описание базы данных.
        """
        if metadata_path.exists():
            metadata: dict = load_data(metadata_path)
            database = Database(**metadata)
        else:
            database_name: str = metadata_path.name.split(".")[0]
            database = Database(database_name)
            save_data(metadata_path, database.dumps())
        return database

    def _get_table_data(self, table: Table) -> None:
        """
        Получение данных таблицы из файла.
        Если файл с данными таблицы существует, то данные считываются из него.
        Иначе, создается пустой список для данных таблицы и сохраняется в
        новом файле.

        :param table: описание таблицы.
        :return: None.
        """
        path: Path = self._database_path / f"table_{table.name}.json"
        if path.exists():
            table.rows = load_data(path)
        else:
            table.rows = []
            save_data(path, table.rows)

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
        self._database.add_table(table)
        save_data(self._database_meta_path, self._database.dumps())
        self._get_table_data(table)
        return table

    def list_tables(self) -> list[Table]:
        """
        :return: список таблиц базы данных.
        """
        return self._database.tables

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
        self._database.drop_table(table_name)
        save_data(self._database_meta_path, self._database.dumps())

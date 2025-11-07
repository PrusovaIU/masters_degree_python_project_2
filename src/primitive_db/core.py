from pathlib import Path
from typing import Optional, Any

from src.primitive_db.metadata import Database, Table
from src.primitive_db.metadata.column import Column
from src.primitive_db.utils.load_data import save_data, load_data
from src.primitive_db.const.columns_type import ColumnsType
from src.primitive_db.const.auto_column_names import AutoColumnNames
from src.primitive_db.utils.decorators import confirm_action, log_time


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

        :raises utils.load_data.LoadDataError: если не удалось считать данные
            таблицы.
        """
        path: Path = self._table_file_path(table.name)
        if path.exists():
            table.rows = load_data(path)
        else:
            table.rows = []
            save_data(path, table.rows)

    def _table_file_path(self, table_name: str) -> Path:
        """
        :param table_name: название таблицы.
        :return: путь к файлу с данными таблицы.
        """
        return self._database_path / f"table_{table_name}.json"

    def _table_names(self) -> list[str]:
        """
        :return: список имен таблиц, существующих в базе данных.
        """
        return [table.name for table in self._database.tables]

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

        :raises utils.load_data.SaveDataError: если не удалось сохранить
            метаданные.
        """
        column_objs = [
            Column(column_name.strip(), type=column_type.strip())
            for column_name, column_type in columns
        ]
        column_objs.insert(
            0,
            Column(AutoColumnNames.ID.value, type=ColumnsType.int.value)
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

    @confirm_action("удаление таблицы")
    def drop_table(self, table_name: str) -> None:
        """
        Обработка команды удаления таблицы.

        :param database: описание базы данных.
        :param table_name: имя таблицы.

        :return: None.

        :raises metadata.db_object.DatabaseError: если не удалось удалить
            таблицу.

        :raises utils.load_data.SaveDataError: если не удалось сохранить
            метаданные.
        """
        self._database.drop_table(table_name)
        save_data(self._database_meta_path, self._database.dumps())

    @log_time
    def insert(self, table_name: str, values: list) -> int:
        """
        Обработка команды вставки данных в таблицу.

        :param table_name: название таблицы.
        :param values: значения колонок.
        :return: ID добавленной строки.

        :raises src.primitive_db.metadata.db_object.DatabaseError: если не
            удалось добавить строку.

        :raises ValueError: если переданные значения не соответствуют
            требуемому формату.
        """
        table: Table = self._database.get_table(table_name)
        columns: list[Column] = [
            c for c in table.columns if c.name != AutoColumnNames.ID.value
        ]
        if len(values) != len(columns):
            raise ValueError(
                "Количество значений не совпадает с количеством колонок."
            )
        values = {
            column.name: value for column, value in zip(columns, values)
        }
        row_id: int = table.add_row(values)
        save_data(self._table_file_path(table_name), table.rows)
        return row_id

    @log_time
    def select(
            self,
            table_name: str,
            where: Optional[dict[str, Any]]
    ) -> list[list]:
        """
        Получение данных из таблицы.

        :param table_name: имя таблицы.

        :param where: словарь с условиями фильтрации вида
            {имя колонки: значение}.

        :return: список данных. Первая строка - заголовки колонок.

        :raises src.primitive_db.metadata.db_object.DatabaseError: если не
            удалось получить данные из таблицы.

        :raises ValueError: если переданные значения не соответствуют
            требуемому формату.
        """
        table: Table = self._database.get_table(table_name)
        rows = [[c.name for c in table.columns]]
        for row in table.select(where):
            rows.append(list(row.values()))
        return rows

    def update(
            self,
            table_name: str,
            set_data: dict[str, Any],
            where_data: dict[str, Any]
    ) -> list[int]:
        """
        Обновление данных в таблице.

        :param table_name: название таблицы.

        :param set_data: словарь с данными для обновления вида
            {имя колонки: новое значение}.

        :param where_data: словарь с условиями фильтрации вида
            {имя колонки: значение}.

        :return: список ID обновленных строк.

        :raises src.primitive_db.metadata.db_object.DatabaseError: если не
            удалось обновить строки.

        :raises ValueError: если переданные значения не соответствуют
            требуемому формату.

        :raises utils.load_data.SaveDataError: если не удалось сохранить
            данные.
        """
        table: Table = self._database.get_table(table_name)
        updated_rows_ids: list[int] = table.update_row(set_data, where_data)
        save_data(self._table_file_path(table_name), table.rows)
        return updated_rows_ids

    @confirm_action("удаление данных")
    def delete(
            self,
            table_name: str,
            where: dict[str, Any]
    ) -> list[int]:
        """
        Удаление данных из таблицы.

        :param table_name: название таблицы.

        :param where: словарь с условиями фильтрации вида
            {имя колонки: значение}.

        :return: список ID удаленных строк.

        :raises src.primitive_db.metadata.db_object.DatabaseError: если не
            удалось добавить строку.

        :raises ValueError: если переданные значения не соответствуют
            требуемому формату.

        :raises utils.load_data.SaveDataError: если не удалось сохранить
            данные.
        """
        table: Table = self._database.get_table(table_name)
        deleted_rows_ids: list[int] = table.delete_row(where)
        save_data(self._table_file_path(table_name), table.rows)
        return deleted_rows_ids

    def get_table(self, table_name: str) -> Table:
        return self._database.get_table(table_name)

#!/usr/bin/env python3
from engine import welcome
from src.primitive_db.db_objs import Database, Column
from src.primitive_db.utils.metadata import load_metadata, MetadataFileError, save_metadata
from pathlib import Path
from loguru import logger
from src.primitive_db.core import create_table
from src.primitive_db.conf import CONFIG


def main():
    print("DB project is running!")
    welcome()

if __name__ == "__main__":
    CONFIG.load(Path("/home/hex/git/masters_degree_python_project_2/src/conf.json"))
    DATABASE_NAME = "my_db"
    try:
        metadata = load_metadata(CONFIG.db_metadata_path)
        logger.info("Database are loaded!")
    except MetadataFileError:
        logger.info("New database created!")
        metadata = {"name": DATABASE_NAME}
    database = Database(**metadata)
    print(database)
    create_table(
        database,
        "new_table",
        [
            "id:int",
            "name: str"
        ]
    )


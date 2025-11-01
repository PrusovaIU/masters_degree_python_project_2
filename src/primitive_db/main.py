#!/usr/bin/env python3
from engine import Engine
from src.primitive_db.metadata import Database, Column
from pathlib import Path
from loguru import logger
from src.primitive_db.core import Core
from src.primitive_db.conf import CONFIG


if __name__ == "__main__":
    CONFIG.load(Path("/home/hex/git/masters_degree_python_project_2/src/conf.json"))
    engine = Engine()
    engine.run()


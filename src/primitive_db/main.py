#!/usr/bin/env python3
import argparse
from pathlib import Path

from src.primitive_db.engine import Engine

from src.primitive_db.conf import CONFIG


def main():
    parser = argparse.ArgumentParser(description="Primitive DB")
    parser.add_argument(
        "-c", "--config",
        type=str,
        dest="config",
        help="Путь файла конфигурации .json"
    )
    args = parser.parse_args()

    CONFIG.load(Path(args.config))
    # CONFIG.load(Path("/home/hex/git/masters_degree_python_project_2/src/conf.json"))

    engine = Engine(CONFIG.database_path)
    try:
        engine.run()
    except KeyboardInterrupt:
        print("Завершение работы...")


if __name__ == "__main__":
    main()

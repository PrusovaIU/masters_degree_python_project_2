#!/usr/bin/env python3
import argparse
from pathlib import Path

from engine import Engine

from src.primitive_db.conf import CONFIG

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Primitive DB")
    parser.add_argument(
        "-c", "--config",
        type=str,
        dest="config",
        help="Путь файла конфигурации .json"
    )
    args = parser.parse_args()

    CONFIG.load(Path(args.config))

    engine = Engine(CONFIG.database_path)
    try:
        engine.run()
    except KeyboardInterrupt:
        print("Завершение работы...")

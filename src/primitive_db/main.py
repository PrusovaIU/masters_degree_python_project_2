#!/usr/bin/env python3
from engine import Engine
from pathlib import Path
from src.primitive_db.conf import CONFIG
import argparse


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

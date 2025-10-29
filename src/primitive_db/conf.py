from enum import Enum
from json import load
from pathlib import Path

class LoadConfigError(Exception):
    pass


class ConfigJSONTags(Enum):
    db_metadata_path = "db_metadata_path"


class Config:
    def __init__(self):
        self.__is_loaded = False
        self._db_metadata_path: Path | None = Path("db.json")

    def _check_loaded(self):
        if not self.__is_loaded:
            raise SyntaxError(
                "Config is not loaded. Please, load() first."
            )

    @property
    def db_metadata_path(self) -> Path:
        self._check_loaded()
        return self._db_metadata_path

    def load(self, config_path: Path) -> None:
        try:
            with config_path.open() as f:
                data = load(f)
            self._db_metadata_path = Path(
                data[ConfigJSONTags.db_metadata_path.value]
            )
        except Exception as err:
            raise LoadConfigError(
                f"Cannot load config from {config_path}: "
                f"{err} ({err.__class__.__name__})"
            )
        else:
            self.__is_loaded = True


CONFIG = Config()

from enum import Enum
from json import load
from pathlib import Path

class LoadConfigError(Exception):
    pass


class ConfigJSONTags(Enum):
    database_path = "database_path"


class Config:
    def __init__(self):
        self.__is_loaded = False
        self._database_path: Path | None = Path("database_data")

    def _check_loaded(self):
        if not self.__is_loaded:
            raise SyntaxError(
                "Config is not loaded. Please, load() first."
            )

    @property
    def database_path(self) -> Path:
        return self._database_path

    def load(self, config_path: Path) -> None:
        try:
            with config_path.open() as f:
                data = load(f)
            self._database_path = Path(
                data[ConfigJSONTags.database_path.value]
            )
        except Exception as err:
            raise LoadConfigError(
                f"Cannot load config from {config_path}: "
                f"{err} ({err.__class__.__name__})"
            )
        else:
            self.__is_loaded = True


CONFIG = Config()

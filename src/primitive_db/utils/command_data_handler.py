from typing import Any
from re import match


def check_value(value: str) -> Any:
    value = value.strip()
    if match(r"^[+-]?\d+(\.\d+)?$", value):
        return value

    if value in ("true", "false"):
        return value

    quoted_match = match(r"^\"(.*)\"$", value) or match(r"^'(.*)'$", value)
    if quoted_match:
        return quoted_match.group(1)

    raise ValueError(f"Неверный формат значения ({value})")


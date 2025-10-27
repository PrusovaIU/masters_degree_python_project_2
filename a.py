from typing import get_args, get_origin, get_type_hints

class Table:
    pass


a = list[int] | None
b = a([1, 2, 3])

print(b)


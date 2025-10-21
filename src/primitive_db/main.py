#!/usr/bin/env python3
from engine import welcome
from schemas.db_objs.database import Database


def main():
    print("DB project is running!")
    welcome()

if __name__ == "__main__":
    db = Database.from_json(
        {
            "name": "db",
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {
                            "name": "id",
                            "type": "int"
                        },
                        {
                            "name": "name",
                            "type": "str"
                        }
                    ]
                },
                {
                    "name": "posts",
                    "columns": [
                        {
                            "name": "id",
                            "type": "int"
                        },
                        {
                            "name": "title",
                            "type": "str"
                        }
                    ]
                }
            ]
        }
    )
    print(db)

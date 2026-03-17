from __future__ import annotations

from pathlib import Path


def get_schema_path() -> Path:
    return Path(__file__).resolve().parent / "schema.sql"


def load_schema_sql() -> str:
    return get_schema_path().read_text(encoding="utf-8")


def split_sql_script(script: str) -> list[str]:
    statements: list[str] = []
    current: list[str] = []
    in_single_quote = False

    for char in script:
        if char == "'":
            in_single_quote = not in_single_quote
        if char == ";" and not in_single_quote:
            statement = "".join(current).strip()
            if statement:
                statements.append(statement)
            current = []
            continue
        current.append(char)

    tail = "".join(current).strip()
    if tail:
        statements.append(tail)

    return statements

"""Small TOML configuration reader."""
from __future__ import annotations

from pathlib import Path
import tomllib


def path() -> Path:
    return Path.home() / ".config" / "gfyupm" / "config.toml"


def read_default() -> str | None:
    try:
        with path().open("rb") as file:
            value = tomllib.load(file).get("default_manager")
    except FileNotFoundError:
        return None
    if value is not None and not isinstance(value, str):
        raise ValueError("config default_manager must be string")
    return value


def write_default(name: str) -> None:
    target = path()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(f'default_manager = "{name}"\n', encoding="utf-8")

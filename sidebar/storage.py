"""Save and load the shelf as JSON. Plain Python, no Qt."""

import json
import os
import sys
from typing import List

APP_DIR_NAME = "QuickShelf"
FILE_NAME = "shelf.json"


def default_path() -> str:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.expanduser("~")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support")
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, APP_DIR_NAME, FILE_NAME)


def load(path: str) -> List[str]:
    """Return saved item paths. A missing or unreadable file gives an empty shelf.

    A corrupt file is renamed to <path>.bad so the user's data is not lost.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = data["items"]
        return [p for p in items if isinstance(p, str)]
    except FileNotFoundError:
        return []
    except (OSError, ValueError, KeyError, TypeError):
        try:
            os.replace(path, path + ".bad")
        except OSError:
            pass
        return []


def save(path: str, items: List[str]) -> None:
    """Write atomically: temp file first, then replace, so a crash cannot corrupt it."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"version": 1, "items": items}, f, indent=2)
    os.replace(tmp, path)

"""Shelf item model: plain Python, no Qt, so it is easy to test."""

import os
from dataclasses import dataclass
from typing import Iterable, List


@dataclass(frozen=True)
class ShelfItem:
    path: str

    @property
    def name(self) -> str:
        return os.path.basename(self.path.rstrip("\\/")) or self.path

    @property
    def is_dir(self) -> bool:
        return os.path.isdir(self.path)


def make_items(
    paths: Iterable[str],
    existing: Iterable[ShelfItem] = (),
    must_exist: bool = True,
) -> List[ShelfItem]:
    """Turn dropped paths into new items.

    Skips duplicates within the drop and paths already on the shelf
    (compared case-insensitively, normalised). Paths that do not exist are
    skipped unless must_exist is False, which is used when reloading a saved
    shelf so moved files stay visible instead of silently vanishing.
    """
    seen = {os.path.normcase(os.path.normpath(item.path)) for item in existing}
    new: List[ShelfItem] = []
    for raw in paths:
        if not raw:
            continue
        path = os.path.normpath(raw)
        key = os.path.normcase(path)
        if key in seen or (must_exist and not os.path.exists(path)):
            continue
        seen.add(key)
        new.append(ShelfItem(path))
    return new


def matches(item: ShelfItem, query: str) -> bool:
    """True if every word in query appears in the item's name or path (case-insensitive)."""
    haystack = f"{item.name} {item.path}".lower()
    return all(word in haystack for word in query.lower().split())


def moved(items: List[ShelfItem], index: int, delta: int) -> List[ShelfItem]:
    """Return a copy of items with the entry at index moved by delta, clamped to the ends."""
    if not 0 <= index < len(items):
        return list(items)
    target = max(0, min(len(items) - 1, index + delta))
    result = list(items)
    result.insert(target, result.pop(index))
    return result

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


def make_items(paths: Iterable[str], existing: Iterable[ShelfItem] = ()) -> List[ShelfItem]:
    """Turn dropped paths into new items.

    Skips paths that do not exist, duplicates within the drop, and paths
    already on the shelf (compared case-insensitively, normalised).
    """
    seen = {os.path.normcase(os.path.normpath(item.path)) for item in existing}
    new: List[ShelfItem] = []
    for raw in paths:
        if not raw:
            continue
        path = os.path.normpath(raw)
        key = os.path.normcase(path)
        if key in seen or not os.path.exists(path):
            continue
        seen.add(key)
        new.append(ShelfItem(path))
    return new

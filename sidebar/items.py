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

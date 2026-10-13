"""Open a file or folder with the system default handler."""

import os
import subprocess
import sys
from typing import Callable, Optional


def _default_launcher(path: str) -> None:
    if sys.platform == "win32":
        os.startfile(path)  # opens files with their app and folders in Explorer
    elif sys.platform == "darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])


def open_path(path: str, launcher: Optional[Callable[[str], None]] = None) -> bool:
    """Open path. Returns False if it no longer exists or could not be opened."""
    if not os.path.exists(path):
        return False
    try:
        (launcher or _default_launcher)(path)
    except OSError:
        return False
    return True

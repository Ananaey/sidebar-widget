"""Start the widget when the user logs in to Windows (HKCU Run key, no admin needed)."""

import os
import sys
from typing import Optional, Protocol

RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
VALUE_NAME = "QuickShelf"


class Backend(Protocol):
    def get(self, name: str) -> Optional[str]: ...
    def set(self, name: str, command: str) -> None: ...
    def delete(self, name: str) -> None: ...


class WindowsRegistryBackend:
    def get(self, name: str) -> Optional[str]:
        import winreg

        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY) as key:
                value, _ = winreg.QueryValueEx(key, name)
            return value
        except OSError:
            return None

    def set(self, name: str, command: str) -> None:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_SZ, command)

    def delete(self, name: str) -> None:
        import winreg

        try:
            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE
            ) as key:
                winreg.DeleteValue(key, name)
        except OSError:
            pass  # already absent


def launch_command() -> str:
    """The command Windows should run at login.

    Packaged build: the .exe itself. From source: pythonw (no console window)
    running the package.
    """
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'
    exe = sys.executable
    pythonw = os.path.join(os.path.dirname(exe), "pythonw.exe")
    if os.path.exists(pythonw):
        exe = pythonw
    return f'"{exe}" -m sidebar'


def is_supported() -> bool:
    return sys.platform == "win32"


def is_enabled(backend: Optional[Backend] = None) -> bool:
    backend = backend or WindowsRegistryBackend()
    return backend.get(VALUE_NAME) is not None


def set_enabled(enabled: bool, backend: Optional[Backend] = None) -> None:
    backend = backend or WindowsRegistryBackend()
    if enabled:
        backend.set(VALUE_NAME, launch_command())
    else:
        backend.delete(VALUE_NAME)

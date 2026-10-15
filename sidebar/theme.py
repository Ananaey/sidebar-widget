"""Light and dark palettes, plus system theme detection. No Qt needed."""

import sys
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass(frozen=True)
class Theme:
    name: str
    panel_bg: str
    text: str
    muted: str
    hover: str
    selected: str
    handle: str
    handle_hover: str


DARK = Theme(
    name="dark",
    panel_bg="rgba(30,30,34,235)",
    text="#f2f2f7",
    muted="#9a9aa2",
    hover="rgba(255,255,255,25)",
    selected="rgba(10,132,255,140)",
    handle="rgba(40,40,45,200)",
    handle_hover="rgba(80,80,90,230)",
)

LIGHT = Theme(
    name="light",
    panel_bg="rgba(246,246,248,238)",
    text="#1c1c1e",
    muted="#6e6e73",
    hover="rgba(0,0,0,18)",
    selected="rgba(10,132,255,110)",
    handle="rgba(200,200,205,215)",
    handle_hover="rgba(170,170,178,235)",
)

THEMES = {"light": LIGHT, "dark": DARK}


def _read_windows_light_flag() -> Optional[int]:
    """1 if Windows apps use the light theme, 0 if dark, None if unknown."""
    if sys.platform != "win32":
        return None
    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        )
        with key:
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return int(value)
    except OSError:
        return None


def system_is_dark(reader: Callable[[], Optional[int]] = _read_windows_light_flag) -> bool:
    """True if the system prefers dark. Defaults to dark when it cannot tell."""
    return reader() != 1


def get_theme(name: str = "auto", reader: Callable[[], Optional[int]] = _read_windows_light_flag) -> Theme:
    """Return the theme for 'light', 'dark' or 'auto' (follow the system)."""
    if name in THEMES:
        return THEMES[name]
    return DARK if system_is_dark(reader) else LIGHT


def toggled(theme: Theme) -> Theme:
    return LIGHT if theme is DARK else DARK

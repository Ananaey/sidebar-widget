"""The slide-out panel and the edge handle that toggles it."""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget

from sidebar.shelf import Shelf
from sidebar.theme import DARK, Theme, get_theme, toggled


PANEL_WIDTH = 320
PANEL_HEIGHT = 520
PANEL_TOP = 60
HANDLE_WIDTH = 14
HANDLE_HEIGHT = 80
ANIMATION_MS = 220

_FLAGS = (
    Qt.WindowType.FramelessWindowHint
    | Qt.WindowType.WindowStaysOnTopHint
    | Qt.WindowType.Tool
)


class Handle(QPushButton):
    """Thin tab on the right edge of the screen. Click to toggle the panel."""

    def __init__(self, on_click):
        super().__init__("")
        self.setWindowFlags(_FLAGS)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(HANDLE_WIDTH, HANDLE_HEIGHT)
        self.apply_theme(DARK)
        self.clicked.connect(on_click)

    def apply_theme(self, theme: Theme) -> None:
        self.setStyleSheet(
            f"QPushButton {{ background: {theme.handle}; border: none;"
            " border-top-left-radius: 7px; border-bottom-left-radius: 7px; }"
            f"QPushButton:hover {{ background: {theme.handle_hover}; }}"
        )

    def place(self, screen_rect: QRect) -> None:
        self.move(screen_rect.right() - HANDLE_WIDTH + 1, screen_rect.top() + PANEL_TOP)


class Panel(QWidget):
    """Frameless always-on-top panel that slides in from the right edge."""

    def __init__(self):
        super().__init__()
        self.setWindowFlags(_FLAGS)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(PANEL_WIDTH, PANEL_HEIGHT)
        self._open = False

        self._body = QWidget(self)
        self._body.setObjectName("body")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._body)

        inner = QVBoxLayout(self._body)
        inner.setContentsMargins(20, 20, 20, 20)
        header = QHBoxLayout()
        self._title = QLabel("Quick Shelf")
        self._title.setStyleSheet("font-size: 18px; font-weight: 600;")
        self._theme_button = QPushButton("◐")
        self._theme_button.setFixedSize(28, 28)
        self._theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._theme_button.setToolTip("Switch light / dark")
        self._theme_button.clicked.connect(lambda: self.apply_theme(toggled(self._theme)))
        header.addWidget(self._title)
        header.addStretch()
        header.addWidget(self._theme_button)
        self._hint = QLabel("Drag files or folders here")
        self.shelf = Shelf()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Search")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self.shelf.set_filter)
        inner.addLayout(header)
        inner.addWidget(self._search)
        inner.addWidget(self._hint)
        inner.addWidget(self.shelf, 1)

        self._anim = QPropertyAnimation(self, b"geometry", self)
        self._anim.setDuration(ANIMATION_MS)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.finished.connect(self._on_anim_finished)

        self.handle = Handle(self.toggle)
        self._theme = DARK
        self.apply_theme(get_theme("auto"))

    def apply_theme(self, theme: Theme) -> None:
        self._theme = theme
        self._body.setStyleSheet(
            f"#body {{ background: {theme.panel_bg}; border-top-left-radius: 16px;"
            " border-bottom-left-radius: 16px; }"
            f"QLabel {{ color: {theme.text}; }}"
        )
        self._hint.setStyleSheet(f"color: {theme.muted};")
        self._search.setStyleSheet(
            f"QLineEdit {{ background: {theme.hover}; color: {theme.text}; border: none;"
            " border-radius: 8px; padding: 6px 10px; font-size: 14px; }"
        )
        self._theme_button.setStyleSheet(
            f"QPushButton {{ background: transparent; border: none; color: {theme.muted};"
            " font-size: 16px; border-radius: 14px; }"
            f"QPushButton:hover {{ background: {theme.hover}; color: {theme.text}; }}"
        )
        self.shelf.apply_theme(theme)
        self.handle.apply_theme(theme)

    def _screen_rect(self) -> QRect:
        return QGuiApplication.primaryScreen().availableGeometry()

    def _rect_at(self, x: int) -> QRect:
        return QRect(x, self._screen_rect().top() + PANEL_TOP, PANEL_WIDTH, PANEL_HEIGHT)

    def start(self) -> None:
        """Show the (collapsed) handle."""
        screen = self._screen_rect()
        self.setGeometry(self._rect_at(screen.right() + 1))
        self.handle.place(screen)
        self.handle.show()

    def toggle(self) -> None:
        screen = self._screen_rect()
        self._open = not self._open
        shown_x = screen.right() - PANEL_WIDTH + 1
        hidden_x = screen.right() + 1
        if self._open:
            self.setGeometry(self._rect_at(hidden_x))
            self.show()
            self.raise_()
        self._anim.stop()
        self._anim.setStartValue(self.geometry())
        self._anim.setEndValue(self._rect_at(shown_x if self._open else hidden_x))
        self._anim.start()
        # Keep the handle on the panel's left edge while open.
        if self._open:
            self.handle.move(shown_x - HANDLE_WIDTH, self.handle.y())
        else:
            self.handle.place(screen)

    def _on_anim_finished(self) -> None:
        if not self._open:
            self.hide()

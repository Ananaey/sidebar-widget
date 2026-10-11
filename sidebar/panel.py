"""The slide-out panel and the edge handle that toggles it."""

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

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
        self.setStyleSheet(
            "QPushButton { background: rgba(40,40,45,200); border: none;"
            " border-top-left-radius: 7px; border-bottom-left-radius: 7px; }"
            "QPushButton:hover { background: rgba(80,80,90,230); }"
        )
        self.clicked.connect(on_click)

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
        self._body.setStyleSheet(
            "#body { background: rgba(30,30,34,235); border-top-left-radius: 16px;"
            " border-bottom-left-radius: 16px; }"
            "QLabel { color: #f2f2f7; }"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._body)

        inner = QVBoxLayout(self._body)
        inner.setContentsMargins(20, 20, 20, 20)
        title = QLabel("Quick Shelf")
        title.setStyleSheet("font-size: 18px; font-weight: 600;")
        hint = QLabel("Your files and folders will live here.")
        hint.setStyleSheet("color: #9a9aa2;")
        inner.addWidget(title)
        inner.addWidget(hint)
        inner.addStretch()

        self._anim = QPropertyAnimation(self, b"geometry", self)
        self._anim.setDuration(ANIMATION_MS)
        self._anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._anim.finished.connect(self._on_anim_finished)

        self.handle = Handle(self.toggle)

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

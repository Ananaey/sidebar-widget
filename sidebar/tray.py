"""System tray icon with a small menu."""

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from sidebar import autostart


def make_icon() -> QIcon:
    """Draw a simple icon in code so the app needs no image assets."""
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor("#0a84ff"))
    painter.drawRoundedRect(QRectF(6, 6, 52, 52), 14, 14)
    painter.setBrush(QColor("#ffffff"))
    painter.drawRoundedRect(QRectF(36, 14, 14, 36), 5, 5)
    painter.end()
    return QIcon(pixmap)


class Tray:
    def __init__(self, app: QApplication, panel):
        self._panel = panel
        self.icon = QSystemTrayIcon(make_icon(), app)
        self.icon.setToolTip("Quick Shelf")

        menu = QMenu()
        toggle_action = QAction("Show / hide shelf", menu)
        toggle_action.triggered.connect(panel.toggle)
        menu.addAction(toggle_action)

        if autostart.is_supported():
            self._autostart_action = QAction("Start with Windows", menu)
            self._autostart_action.setCheckable(True)
            self._autostart_action.setChecked(autostart.is_enabled())
            self._autostart_action.toggled.connect(self._on_autostart_toggled)
            menu.addAction(self._autostart_action)

        menu.addSeparator()
        quit_action = QAction("Quit", menu)
        quit_action.triggered.connect(app.quit)
        menu.addAction(quit_action)

        self._menu = menu  # keep a reference so it is not garbage collected
        self.icon.setContextMenu(menu)
        self.icon.activated.connect(self._on_activated)
        self.icon.show()

    def _on_activated(self, reason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # left click
            self._panel.toggle()

    def _on_autostart_toggled(self, enabled: bool) -> None:
        try:
            autostart.set_enabled(enabled)
        except OSError:
            # Could not write the setting: show the real state again.
            self._autostart_action.blockSignals(True)
            self._autostart_action.setChecked(autostart.is_enabled())
            self._autostart_action.blockSignals(False)

"""The list that holds shelf items and accepts files dropped from Explorer."""

from typing import List

from PySide6.QtCore import QFileInfo, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QAbstractItemView,
    QFileIconProvider,
    QListWidget,
    QListWidgetItem,
    QMenu,
)

from sidebar.items import ShelfItem, make_items
from sidebar.opener import open_path

_STYLE = (
    "QListWidget { background: transparent; border: none; color: #f2f2f7; font-size: 14px; }"
    "QListWidget::item { padding: 8px; border-radius: 8px; }"
    "QListWidget::item:hover { background: rgba(255,255,255,25); }"
    "QListWidget::item:selected { background: rgba(10,132,255,140); }"
)


class Shelf(QListWidget):
    def __init__(self):
        super().__init__()
        self._items: List[ShelfItem] = []
        self._icons = QFileIconProvider()
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.setFrameShape(QListWidget.Shape.NoFrame)
        self.setStyleSheet(_STYLE)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.itemDoubleClicked.connect(self._open_item)

    def _open_item(self, row: QListWidgetItem) -> None:
        path = row.data(Qt.ItemDataRole.UserRole)
        if not open_path(path):
            # The file moved or was deleted: dim the row so it is obvious.
            row.setForeground(QColor("#6e6e73"))
            row.setToolTip(f"{path}\n(not found)")

    def remove_row(self, index: int) -> None:
        if 0 <= index < len(self._items):
            del self._items[index]
            self.takeItem(index)

    def contextMenuEvent(self, event):
        row = self.itemAt(event.pos())
        if row is None:
            return
        index = self.row(row)
        menu = QMenu(self)
        open_action = menu.addAction("Open")
        remove_action = menu.addAction("Remove from shelf")
        chosen = menu.exec(event.globalPos())
        if chosen == open_action:
            self._open_item(row)
        elif chosen == remove_action:
            self.remove_row(index)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace) and self.currentRow() >= 0:
            self.remove_row(self.currentRow())
        else:
            super().keyPressEvent(event)

    def add_paths(self, paths) -> int:
        """Add paths to the shelf and return how many were new."""
        new_items = make_items(paths, self._items)
        for item in new_items:
            self._items.append(item)
            row = QListWidgetItem(self._icons.icon(QFileInfo(item.path)), item.name)
            row.setToolTip(item.path)
            row.setData(Qt.ItemDataRole.UserRole, item.path)
            self.addItem(row)
        return len(new_items)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        self.add_paths(url.toLocalFile() for url in urls if url.isLocalFile())
        event.acceptProposedAction()

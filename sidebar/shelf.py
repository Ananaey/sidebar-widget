"""The list that holds shelf items and accepts files dropped from Explorer."""

import os
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

from sidebar import storage
from sidebar.items import ShelfItem, make_items, matches, moved
from sidebar.opener import open_path
from sidebar.theme import DARK, Theme

def _style_for(theme: Theme) -> str:
    return (
        f"QListWidget {{ background: transparent; border: none; color: {theme.text}; font-size: 14px; }}"
        "QListWidget::item { padding: 8px; border-radius: 8px; }"
        f"QListWidget::item:hover {{ background: {theme.hover}; }}"
        f"QListWidget::item:selected {{ background: {theme.selected}; color: {theme.text}; }}"
    )


class Shelf(QListWidget):
    def __init__(self, storage_path: str = ""):
        super().__init__()
        self._storage_path = storage_path or storage.default_path()
        self._items: List[ShelfItem] = []
        self._query = ""
        self._icons = QFileIconProvider()
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DropOnly)
        self.setFrameShape(QListWidget.Shape.NoFrame)
        self.apply_theme(DARK)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.itemDoubleClicked.connect(self._open_item)
        self._add_items(make_items(storage.load(self._storage_path), must_exist=False))

    def apply_theme(self, theme: Theme) -> None:
        self.setStyleSheet(_style_for(theme))

    def set_filter(self, query: str) -> None:
        """Show only items matching query; an empty query shows everything."""
        self._query = query
        for index, item in enumerate(self._items):
            self.item(index).setHidden(not matches(item, query))

    def move_row(self, index: int, delta: int) -> None:
        """Move an item up (-1) or down (+1) and keep it selected."""
        reordered = moved(self._items, index, delta)
        if reordered == self._items:
            return
        self._items = []
        self.clear()
        self._add_items(reordered)
        self._save()
        self.setCurrentRow(max(0, min(len(reordered) - 1, index + delta)))

    def _save(self) -> None:
        try:
            storage.save(self._storage_path, [item.path for item in self._items])
        except OSError:
            pass  # a failed save must never crash the widget

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
            self._save()

    def contextMenuEvent(self, event):
        row = self.itemAt(event.pos())
        if row is None:
            return
        index = self.row(row)
        menu = QMenu(self)
        open_action = menu.addAction("Open")
        up_action = menu.addAction("Move up")
        down_action = menu.addAction("Move down")
        # Reordering while a search hides rows would be confusing.
        up_action.setEnabled(not self._query and index > 0)
        down_action.setEnabled(not self._query and index < len(self._items) - 1)
        remove_action = menu.addAction("Remove from shelf")
        chosen = menu.exec(event.globalPos())
        if chosen == open_action:
            self._open_item(row)
        elif chosen == up_action:
            self.move_row(index, -1)
        elif chosen == down_action:
            self.move_row(index, 1)
        elif chosen == remove_action:
            self.remove_row(index)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace) and self.currentRow() >= 0:
            self.remove_row(self.currentRow())
        else:
            super().keyPressEvent(event)

    def _add_items(self, new_items: List[ShelfItem]) -> None:
        for item in new_items:
            self._items.append(item)
            row = QListWidgetItem(self._icons.icon(QFileInfo(item.path)), item.name)
            row.setToolTip(item.path)
            row.setData(Qt.ItemDataRole.UserRole, item.path)
            if not os.path.exists(item.path):
                row.setForeground(QColor("#6e6e73"))
                row.setToolTip(f"{item.path}\n(not found)")
            row.setHidden(not matches(item, self._query))
            self.addItem(row)

    def add_paths(self, paths) -> int:
        """Add paths to the shelf, save, and return how many were new."""
        new_items = make_items(paths, self._items)
        self._add_items(new_items)
        if new_items:
            self._save()
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

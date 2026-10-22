"""Runs the real Qt widgets headlessly. Skipped when PySide6 is not installed."""

import os
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

try:
    from PySide6.QtWidgets import QApplication

    from sidebar.panel import Panel
    from sidebar.shelf import Shelf
    from sidebar.theme import DARK, LIGHT

    HAVE_QT = True
except ImportError:
    HAVE_QT = False


@unittest.skipUnless(HAVE_QT, "PySide6 is not installed")
class QtSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])

    @classmethod
    def tearDownClass(cls):
        # Let Qt finish deleting widgets before the interpreter shuts down.
        cls.app.processEvents()

    def make_shelf(self):
        shelf = Shelf(self.store)
        self.addCleanup(shelf.deleteLater)
        return shelf

    def make_panel(self):
        panel = Panel(self.store)
        self.addCleanup(panel.deleteLater)
        self.addCleanup(panel.handle.deleteLater)
        self.addCleanup(panel.hide)
        self.addCleanup(panel.handle.hide)
        return panel

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.store = os.path.join(self.tmp.name, "store", "shelf.json")
        self.files = []
        for name in ("alpha.txt", "beta.txt", "gamma.txt"):
            path = os.path.join(self.tmp.name, name)
            open(path, "w").close()
            self.files.append(path)

    def names(self, shelf):
        return [shelf.item(i).text() for i in range(shelf.count())]

    def visible(self, shelf):
        return [shelf.item(i).text() for i in range(shelf.count()) if not shelf.item(i).isHidden()]

    def test_add_filter_move_remove(self):
        shelf = self.make_shelf()
        self.assertEqual(shelf.add_paths(self.files), 3)
        self.assertEqual(shelf.add_paths(self.files), 0)  # duplicates ignored
        self.assertEqual(self.names(shelf), ["alpha.txt", "beta.txt", "gamma.txt"])

        shelf.set_filter("beta")
        self.assertEqual(self.visible(shelf), ["beta.txt"])
        shelf.set_filter("")
        self.assertEqual(len(self.visible(shelf)), 3)

        shelf.move_row(0, 1)
        self.assertEqual(self.names(shelf), ["beta.txt", "alpha.txt", "gamma.txt"])

        shelf.remove_row(1)
        self.assertEqual(self.names(shelf), ["beta.txt", "gamma.txt"])

    def test_shelf_persists_between_instances(self):
        first = self.make_shelf()
        first.add_paths(self.files[:2])
        first.move_row(1, -1)

        second = self.make_shelf()
        self.assertEqual(self.names(second), ["beta.txt", "alpha.txt"])

    def test_missing_saved_file_is_still_listed(self):
        first = self.make_shelf()
        first.add_paths(self.files[:1])
        os.remove(self.files[0])
        second = self.make_shelf()
        self.assertEqual(self.names(second), ["alpha.txt"])
        self.assertIn("not found", second.item(0).toolTip())

    def test_panel_toggle_and_theme(self):
        panel = self.make_panel()
        panel.start()
        self.assertFalse(panel._open)
        panel.toggle()
        self.assertTrue(panel._open)
        panel.toggle()
        self.assertFalse(panel._open)

        panel.apply_theme(LIGHT)
        self.assertIs(panel._theme, LIGHT)
        panel.apply_theme(DARK)
        self.assertIs(panel._theme, DARK)

    def test_search_box_filters_the_shelf(self):
        panel = self.make_panel()
        panel.shelf.add_paths(self.files)
        panel._search.setText("gamma")
        self.assertEqual(self.visible(panel.shelf), ["gamma.txt"])
        panel._search.clear()
        self.assertEqual(len(self.visible(panel.shelf)), 3)


if __name__ == "__main__":
    unittest.main()

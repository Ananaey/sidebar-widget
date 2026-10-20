import os
import tempfile
import unittest

from sidebar.items import ShelfItem, make_items


class MakeItemsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = os.path.join(self.tmp.name, "notes.txt")
        open(self.file, "w").close()
        self.folder = os.path.join(self.tmp.name, "docs")
        os.mkdir(self.folder)

    def test_adds_files_and_folders(self):
        items = make_items([self.file, self.folder])
        self.assertEqual([i.name for i in items], ["notes.txt", "docs"])
        self.assertFalse(items[0].is_dir)
        self.assertTrue(items[1].is_dir)

    def test_skips_missing_paths(self):
        missing = os.path.join(self.tmp.name, "nope.txt")
        self.assertEqual(make_items([missing, ""]), [])

    def test_keeps_missing_paths_when_not_required(self):
        missing = os.path.join(self.tmp.name, "gone.txt")
        items = make_items([missing], must_exist=False)
        self.assertEqual([i.name for i in items], ["gone.txt"])

    def test_skips_duplicates_in_one_drop(self):
        self.assertEqual(len(make_items([self.file, self.file])), 1)

    def test_skips_items_already_on_shelf(self):
        existing = [ShelfItem(self.file)]
        self.assertEqual(make_items([self.file], existing), [])

    def test_name_of_folder_with_trailing_slash(self):
        self.assertEqual(ShelfItem(self.folder + os.sep).name, "docs")


class SearchAndMoveTests(unittest.TestCase):
    def setUp(self):
        from sidebar.items import ShelfItem as S

        self.a = S(r"C:\Work\Report Final.docx")
        self.b = S(r"C:\Work\budget.xlsx")
        self.c = S(r"C:\Photos\trip")

    def test_empty_query_matches_everything(self):
        from sidebar.items import matches

        self.assertTrue(all(matches(i, "") for i in (self.a, self.b, self.c)))

    def test_matches_name_case_insensitive(self):
        from sidebar.items import matches

        self.assertTrue(matches(self.a, "report"))
        self.assertFalse(matches(self.b, "report"))

    def test_matches_path_and_multiple_words(self):
        from sidebar.items import matches

        self.assertTrue(matches(self.a, "work final"))
        self.assertFalse(matches(self.c, "work trip"))

    def test_move_down_and_up(self):
        from sidebar.items import moved

        items = [self.a, self.b, self.c]
        self.assertEqual(moved(items, 0, 1), [self.b, self.a, self.c])
        self.assertEqual(moved(items, 2, -1), [self.a, self.c, self.b])

    def test_move_clamps_at_ends_and_ignores_bad_index(self):
        from sidebar.items import moved

        items = [self.a, self.b, self.c]
        self.assertEqual(moved(items, 0, -1), items)
        self.assertEqual(moved(items, 2, 1), items)
        self.assertEqual(moved(items, 9, 1), items)
        self.assertEqual(items, [self.a, self.b, self.c])


if __name__ == "__main__":
    unittest.main()

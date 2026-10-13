import os
import tempfile
import unittest

from sidebar.opener import open_path


class OpenPathTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.file = os.path.join(self.tmp.name, "a.txt")
        open(self.file, "w").close()

    def test_opens_existing_path_with_launcher(self):
        opened = []
        self.assertTrue(open_path(self.file, opened.append))
        self.assertEqual(opened, [self.file])

    def test_opens_folder(self):
        opened = []
        self.assertTrue(open_path(self.tmp.name, opened.append))
        self.assertEqual(opened, [self.tmp.name])

    def test_missing_path_returns_false_and_does_not_launch(self):
        opened = []
        missing = os.path.join(self.tmp.name, "gone.txt")
        self.assertFalse(open_path(missing, opened.append))
        self.assertEqual(opened, [])

    def test_launcher_error_returns_false(self):
        def boom(_path):
            raise OSError("no handler")

        self.assertFalse(open_path(self.file, boom))


if __name__ == "__main__":
    unittest.main()

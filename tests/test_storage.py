import os
import tempfile
import unittest

from sidebar import storage


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = os.path.join(self.tmp.name, "sub", "shelf.json")

    def test_round_trip_creates_folder(self):
        storage.save(self.path, ["C:\\a.txt", "C:\\docs"])
        self.assertEqual(storage.load(self.path), ["C:\\a.txt", "C:\\docs"])

    def test_missing_file_is_empty(self):
        self.assertEqual(storage.load(self.path), [])

    def test_corrupt_file_is_empty_and_kept_as_bad(self):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w") as f:
            f.write("{not json")
        self.assertEqual(storage.load(self.path), [])
        self.assertTrue(os.path.exists(self.path + ".bad"))

    def test_wrong_shape_is_empty(self):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w") as f:
            f.write('["just", "a", "list"]')
        self.assertEqual(storage.load(self.path), [])

    def test_non_string_entries_dropped(self):
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w") as f:
            f.write('{"items": ["ok", 5, null]}')
        self.assertEqual(storage.load(self.path), ["ok"])

    def test_save_overwrites_and_leaves_no_temp_file(self):
        storage.save(self.path, ["one"])
        storage.save(self.path, ["two"])
        self.assertEqual(storage.load(self.path), ["two"])
        self.assertFalse(os.path.exists(self.path + ".tmp"))


if __name__ == "__main__":
    unittest.main()

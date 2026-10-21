import unittest
from typing import Dict, Optional

from sidebar import autostart


class FakeBackend:
    def __init__(self):
        self.values: Dict[str, str] = {}

    def get(self, name: str) -> Optional[str]:
        return self.values.get(name)

    def set(self, name: str, command: str) -> None:
        self.values[name] = command

    def delete(self, name: str) -> None:
        self.values.pop(name, None)


class AutostartTests(unittest.TestCase):
    def setUp(self):
        self.backend = FakeBackend()

    def test_disabled_by_default(self):
        self.assertFalse(autostart.is_enabled(self.backend))

    def test_enable_writes_launch_command(self):
        autostart.set_enabled(True, self.backend)
        self.assertTrue(autostart.is_enabled(self.backend))
        self.assertEqual(self.backend.values[autostart.VALUE_NAME], autostart.launch_command())

    def test_disable_removes_value(self):
        autostart.set_enabled(True, self.backend)
        autostart.set_enabled(False, self.backend)
        self.assertFalse(autostart.is_enabled(self.backend))

    def test_disable_when_already_disabled_is_fine(self):
        autostart.set_enabled(False, self.backend)
        self.assertFalse(autostart.is_enabled(self.backend))

    def test_launch_command_is_quoted(self):
        command = autostart.launch_command()
        self.assertTrue(command.startswith('"'))
        self.assertIn("sidebar", command)


if __name__ == "__main__":
    unittest.main()

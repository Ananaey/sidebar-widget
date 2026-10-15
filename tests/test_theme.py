import unittest

from sidebar.theme import DARK, LIGHT, get_theme, system_is_dark, toggled


class ThemeTests(unittest.TestCase):
    def test_explicit_names(self):
        self.assertIs(get_theme("light"), LIGHT)
        self.assertIs(get_theme("dark"), DARK)

    def test_auto_follows_system(self):
        self.assertIs(get_theme("auto", reader=lambda: 1), LIGHT)
        self.assertIs(get_theme("auto", reader=lambda: 0), DARK)

    def test_auto_defaults_to_dark_when_unknown(self):
        self.assertTrue(system_is_dark(reader=lambda: None))
        self.assertIs(get_theme("auto", reader=lambda: None), DARK)

    def test_unknown_name_falls_back_to_auto(self):
        self.assertIs(get_theme("neon", reader=lambda: 1), LIGHT)

    def test_toggle_flips_between_themes(self):
        self.assertIs(toggled(DARK), LIGHT)
        self.assertIs(toggled(LIGHT), DARK)

    def test_palettes_have_distinct_text_and_background(self):
        for theme in (LIGHT, DARK):
            self.assertNotEqual(theme.text, theme.panel_bg)


if __name__ == "__main__":
    unittest.main()

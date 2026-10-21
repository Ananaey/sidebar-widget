"""Entry point: python -m sidebar"""

import sys

from PySide6.QtWidgets import QApplication

from sidebar.panel import Panel
from sidebar.tray import Tray


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # keep running in the tray
    panel = Panel()
    panel.start()
    tray = Tray(app, panel)  # noqa: F841  (kept alive for the app's lifetime)
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

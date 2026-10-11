"""Entry point: python -m sidebar"""

import sys

from PySide6.QtWidgets import QApplication

from sidebar.panel import Panel


def main() -> int:
    app = QApplication(sys.argv)
    panel = Panel()
    panel.start()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())

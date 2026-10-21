"""Entry script for PyInstaller (it needs a plain script, not `-m sidebar`)."""

import sys

from sidebar.__main__ import main

if __name__ == "__main__":
    sys.exit(main())

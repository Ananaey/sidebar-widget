@echo off
rem Build a single-file Windows exe: dist\QuickShelf.exe
python -m pip install --upgrade pyinstaller PySide6 || exit /b 1
python -m PyInstaller --noconfirm --onefile --windowed --name QuickShelf run.py || exit /b 1
echo.
echo Built dist\QuickShelf.exe

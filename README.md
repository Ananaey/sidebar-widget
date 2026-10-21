# Quick Shelf
n[![tests](https://github.com/Ananaey/sidebar-widget/actions/workflows/tests.yml/badge.svg)](https://github.com/Ananaey/sidebar-widget/actions/workflows/tests.yml)

A slide-out sidebar for your desktop. Keep files and folders in one place, and open them with a double-click.

## Run

```
pip install -r requirements.txt
python -m sidebar
```

Click the thin tab on the right edge of the screen to slide the panel open or closed.

## Build the exe (Windows)

```
build.bat
```

This produces `dist\QuickShelf.exe`. Once the widget has been checked on a real machine, attach that file to a GitHub Release so people can download it.

## Roadmap

- [x] Day 1: frameless always-on-top panel, edge handle, slide animation
- [x] Day 2: drag files and folders onto the panel to add them
- [x] Day 3: double-click to open, right-click to remove (Delete key works too)
- [x] Day 4: save items between runs (stored in `%APPDATA%\QuickShelf\shelf.json`)
- [x] Day 5: light and dark themes (follows the system, toggle button in the header)
- [ ] Later: real blur / acrylic background and remembering the chosen theme
- [x] Day 6: search box and reordering (Move up / Move down in the right-click menu)
- [ ] Later: groups / pinned sections
- [x] Day 7: tray icon (left-click toggles, right-click menu), "Start with Windows", `build.bat` for the exe
- [ ] Build and publish the first `QuickShelf.exe` as a GitHub Release (needs a machine where the widget runs)

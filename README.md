# Quick Shelf

A slide-out sidebar for your desktop. Keep files and folders in one place, and open them with a double-click.

## Run

```
pip install -r requirements.txt
python -m sidebar
```

Click the thin tab on the right edge of the screen to slide the panel open or closed.

## Roadmap

- [x] Day 1: frameless always-on-top panel, edge handle, slide animation
- [x] Day 2: drag files and folders onto the panel to add them
- [x] Day 3: double-click to open, right-click to remove (Delete key works too)
- [x] Day 4: save items between runs (stored in `%APPDATA%\QuickShelf\shelf.json`)
- [x] Day 5: light and dark themes (follows the system, toggle button in the header)
- [ ] Later: real blur / acrylic background and remembering the chosen theme
- [ ] Day 6: search, groups, reordering
- [ ] Day 7: tray icon, start on boot, `.exe` release

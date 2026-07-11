# Release Notes — Symlink Manager v1.1.1

**Release date:** July 12, 2026

---

## Overview

Symlink Manager v1.1.1 brings a completely redesigned user interface with a custom frameless window, cross-platform autostart support, and the new Pastel Pink theme. The system tray has been overhauled for reliability and simplicity.

---

## Features

### Symlink Creation
- Create symlinks for files and directories
- Cross-platform support (Windows, macOS, Linux)
- Drag-and-drop path input
- Path validation before creation
- Relative symlink support for portable structures
- Force mode to overwrite existing targets
- Windows Admin mode for system-protected directories
- Optional confirmation dialog

### Symlink Management
- Automatic tracking of all created symlinks
- View, edit notes, verify status, and delete symlinks
- Status indicators: Active, Broken, Missing, Inactive
- Right-click context menu to copy paths

### History & Statistics
- Timestamped creation history (last 200 records)
- Most-used source and target path tracking
- Persistent storage across sessions

### User Interface
- **Custom frameless window** — native OS title bar replaced with a modern, theme-aware custom title bar with minimize, maximize/restore, and close buttons
- **Drag to move** — click and drag the title bar to move the window; drag out of maximized state to restore and reposition
- **Edge resize** — 6px invisible resize border on all edges and corners
- **Pastel Pink theme** — new light theme with soft pink tones
- Dark, Light, Monokai, and Pastel Pink themes
- Window size and position memory
- Drag-and-drop support for both source and target fields

### System Tray
- Cross-platform tray icon with simplified "Open" and "Close" menu
- Double-click tray icon to restore the main window
- Fixes crash on right-click menu

### Autostart
- **Start on system login** option in Settings
- Cross-platform implementation:
  - Windows: `.lnk` shortcut in Startup folder
  - macOS: `.plist` LaunchAgent loaded via `launchctl`
  - Linux: `.desktop` file in `~/.config/autostart/`
- When launched via autostart, the app starts **minimized to tray** with a notification

---

## Known Limitations

1. **Relative symlinks on Windows** — May not work reliably across different drives.
2. **Admin privileges** — Some Windows directories (e.g. `System32`, `Program Files`) require elevation.
3. **Bundle size** — Standalone executable is ~150–200 MB due to bundled Python and Qt.

---

## Changelog

### v1.1.1 (July 12, 2026)
- **Custom frameless window** — replaced native OS title bar with a custom, theme-aware title bar
  - Draggable with mouse (click-and-drag, drag-out-of-maximize)
  - Minimize, maximize/restore, and close buttons
  - Double-click title bar to toggle maximize
  - Edge resize (6px border on all sides)
- **New Pastel Pink theme** — soft pink color scheme
- **Start on system login** — cross-platform autostart registration
  - New `startup_manager.py` module for Windows/macOS/Linux
  - Starts minimized to tray when launched via autostart
- **System tray overhaul** — fixed right-click crash, simplified to "Open" and "Close" menu options
  - Double-click tray icon restores the window
- **New `title_bar.py`** module for custom frameless window
- Updated `app.py` for minimized-to-tray startup
- Updated `settings_manager.py` with `start_on_login` and `minimize_to_tray` defaults
- Updated `ui_styles.py` with title bar styling for all themes
- Updated `main_window.py` with frameless mode, edge resize, and title bar wiring

### v1.1.0 (July 12, 2026)
- Added cross-platform system tray icon with platform-specific behaviors
- Minimize to system tray on close (configurable in Settings)
- Tray icon context menu: Open and Close
- Notification balloon when minimized to tray
- New `tray_icon.py` module for tray icon management
- Updated `app.py` with `setQuitOnLastWindowClosed(False)` for tray support
- Settings tab now includes System Tray configuration section

### v1.0.1 (July 11, 2026)
- Fixed an issue that caused the pyinstaller to fail on Windows. Build script now creates .ico file on the go.
- Fixed an issue in which users could append paths related to files as if they were directories, which would end with the SM failing to create the symlink.
- Discovered and provided work arounds for an issue related to uv managed .venvs, in which certain python dlls were missing and this caused the build to fail.

### v1.0.0 (July 4, 2026)
- Initial release
- Cross-platform symlink creation (Windows, macOS, Linux)
- Modern PyQt6 GUI with dark/light themes
- Drag-and-drop file/folder input
- Symlink tracking, notes, verification, and deletion
- Creation history and most-used statistics
- Standalone executable builds via PyInstaller

---

## File Structure

```
symlink-manager/
├── app.py                  # Entry point
├── main_window.py          # UI components and event handlers
├── symlink_manager.py      # Core symlink creation/removal logic
├── settings_manager.py     # Settings, history, and symlink tracking
├── drag_drop_widgets.py    # Drag-and-drop QLineEdit widget
├── tray_icon.py            # System tray icon implementation
├── title_bar.py            # Custom frameless title bar widget
├── startup_manager.py      # Cross-platform autostart registration
├── ui_styles.py            # Theme stylesheets
├── build_executable.py     # PyInstaller build automation
├── symlink_app.spec        # PyInstaller specification
├── build.sh / build.bat    # Convenience build scripts
├── requirements.txt        # Python dependencies
├── README.md               # User guide
├── BUILD_GUIDE.md          # Build instructions
├── RELEASE_NOTES.md        # This file
└── SYMLINK_MANAGEMENT.md   # Symlink tracking reference
```

---

## Configuration

Settings and data are stored as JSON in:

| Platform | Directory |
|---|---|
| **Windows** | `%APPDATA%\SymlinkApp\` |
| **macOS / Linux** | `~/.config/symlink_app/` |

| File | Purpose |
|---|---|
| `settings.json` | Window geometry, theme, last-used directories, minimize-to-tray, autostart |
| `history.json` | Creation records and recently used paths |
| `managed_symlinks.json` | Tracked symlinks with notes |

---

## Security

- All paths are validated before any operation.
- The app only creates symlinks — it never deletes or modifies source files.
- No network access required.
- Settings are stored in the user's home directory only.

---

## Future Roadmap

Potential features for future releases:
- [ ] Batch symlink creation
- [ ] Command-line interface (CLI)
- [ ] Automatic dark mode detection
- [ ] Custom icon selection for symlinks
- [ ] Undo / redo support
- [ ] Network / remote symlink support

---

## Support

- **Build issues:** See [BUILD_GUIDE.md](BUILD_GUIDE.md)
- **Usage questions:** See [README.md](README.md)
- **Logs:** Check the config directory for application logs

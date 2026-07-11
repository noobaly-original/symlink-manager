# Release Notes — Symlink Manager v1.0.0

**Release date:** July 4, 2026

---

## Overview

Symlink Manager v1.0.0 is the initial release of a cross-platform GUI application for creating and managing symbolic links. Built with PyQt6, it provides a modern interface for symlink operations on Windows, macOS, and Linux.

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
- Dark and light themes
- Window size and position memory
- Drag-and-drop support for both source and target fields

---

## Known Limitations

1. **Relative symlinks on Windows** — May not work reliably across different drives.
2. **Admin privileges** — Some Windows directories (e.g. `System32`, `Program Files`) require elevation.
3. **Bundle size** — Standalone executable is ~150–200 MB due to bundled Python and Qt.

---

## Changelog

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
├── drag_drop_widgets.py   # Drag-and-drop QLineEdit widget
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
| `settings.json` | Window geometry, theme, last-used directories |
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

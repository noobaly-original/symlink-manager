# Release Notes — Symlink Manager v2.0.0

**Release date:** July 13, 2026

---

## Overview

Symlink Manager v2.0.0 is a major feature release introducing batch symlink creation, three new pastel themes, PyInstaller bundle compatibility for elevation features, UIPI drag-and-drop support for admin mode, and numerous UI refinements.

---

## New in v2.0.0

### Batch Operations
- **Batch symlink creation** — new **Batch** tab with ability to create multiple symlinks from:
  - A CSV file (columns: source, target, optional relative/force flags)
  - A manually populated list within the UI
  - Progress tracking with success/ failure indicators per operation
  - Admin checkbox for batch operations when elevation is needed

### New Themes
- **Pastel Blue** — light theme with soft blue tones and navy accents
- **Pastel Green** — light theme with soft green tones and forest accents
- **Pastel Orange** — light theme with warm peach tones and brown accents
- Combined with existing Dark, Light, Monokai, and Pastel Pink for a total of **7 themes**

### PyInstaller Bundle Compatibility
- **`relaunch_as_admin()`** — now detects PyInstaller bundles and passes the correct arguments (`None` for .exe, script path for dev mode)
- **`StartupManager._get_launch_command()`** — new helper returning `(executable, args_list)` appropriate for bundled vs. script mode, used on all platforms (Windows, macOS, Linux)
- **`mklink` subprocess calls** — changed to `shell=True` because `mklink` is a `cmd.exe` internal command
- **`symlink_app.spec`** — all custom modules added to `hiddenimports`

### UIPI Drag-and-Drop Support (Admin Mode)
- When running elevated on Windows, **UIPI (User Interface Privilege Isolation)** previously blocked drag-and-drop from non-elevated Explorer
- **Process-wide fix** via `_patch_uipi_for_drag_drop()` in `app.py` — calls `ChangeWindowMessageFilter()` before any windows are created
- **Per-window fix** via `_patch_uipi_for_window()` in `main_window.py` — calls `ChangeWindowMessageFilterEx()` on the window's HWND

### UI Improvements
- **Full path display** — Manage, History, and Statistics tables now show full paths without truncation; Qt handles ellipsis clipping via column resize modes
- **Interactive column resizing** — all table columns are draggable (`Interactive` resize mode) with sensible initial widths
- **Window geometry memory** — now saves and restores window position (x, y) and maximized state alongside size
- **Theme combo hover** — combo box dropdown items now correctly use the active theme's accent color instead of the system default (pink)

### General
- Updated version to 2.0.0
- Updated `build_executable.py`, `symlink_app.spec`, and build scripts for compatibility

---

## Changelog

### v2.0.0 (July 13, 2026)
- **Major feature:** Batch symlink creation — new `batch_operations_widget.py` module with CSV and list-based batch creation
- **New themes:** Pastel Blue, Pastel Green, Pastel Orange — three new light themes (7 total)
- **PyInstaller compatibility:** `relaunch_as_admin()` and `StartupManager` now detect frozen bundles; `mklink` calls use `shell=True`; all modules added to `hiddenimports`
- **UIPI fix:** Drag-and-drop now works when running as admin on Windows — process-wide and per-window message filter patching
- **UI fix:** Combo box dropdown hover highlight now matches the active theme's accent color
- **UI fix:** Manage, History, and Statistics tables show full paths without slicing truncation
- **UI fix:** All table columns now have interactive resize mode with sensible initial widths
- **UI improvement:** Window geometry now saves/restores position (x, y) and maximized state
- **Updated version:** v1.1.2 → v2.0.0

### v1.1.2 (July 12, 2026)
- **Bug fix:** Fixed `TypeError: unable to convert a C++ 'QSystemTrayIcon::ActivationReason' instance to a Python object` on shutdown
- **Bug fix:** Application now fully exits when "Minimize to system tray" is disabled (was remaining as a background process)
- Added `cleanup()` method to `TrayIcon` for safe signal disconnection before quit
- Added safety guard in `_on_tray_activated` to silently ignore signal errors during shutdown
- Updated version to 1.1.2

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

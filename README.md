# Symlink Manager

A modern, cross-platform GUI application for creating and managing symbolic links on Windows, macOS, and Linux. Built with PyQt6.

---

## Features

### Core
- 🔗 **Create Symlinks** — File and directory symlinks on any supported OS
- 🎨 **Modern GUI** — 7 themes (Dark, Light, Monokai, Pastel Pink, Pastel Blue, Pastel Green, Pastel Orange) with drag-and-drop path input
- 🖼️ **Custom Frameless Window** — Beautiful custom title bar with minimize, maximize, and close buttons; draggable and theme-aware
- 🛡️ **Path Validation** — Validates paths before creating symlinks
- 🔒 **Admin Mode** (Windows) — Create symlinks in system-protected directories; UIPI patched for drag-and-drop support when running elevated
- 📋 **Symlink Tracking** — Automatically track, annotate, verify, and delete symlinks
- 📊 **History & Statistics** — View creation history and most-used paths
- 🖥️ **System Tray** — Minimize to tray, right-click menu with Open/Close, double-click to restore
- 🚀 **Autostart** — Option to launch on system login (starts minimized to tray)
- ♻️ **Symlink Persistence** — Automatically recreate missing symlinks every 60 seconds (optional, configurable in Settings)
- � **Merge Management** — Before recreating a missing symlink, copy source directory contents into the symlink folder (newer files override)
- �📦 **Batch Operations** — Create multiple symlinks at once from a CSV or manual list
- 🏗️ **PyInstaller Bundle** — Compatible with standalone .exe builds; elevation, autostart, and drag-drop all work in bundled mode

### Options
| Option | Description |
|---|---|
| **Relative** | Creates a relative symlink (useful for portable structures) |
| **Force** | Overwrites any existing file/folder at the target location |
| **Admin** (Windows) | Elevates to administrator privileges for protected directories |
| **Confirm** | Shows a confirmation dialog before creating the symlink |

---

## Quick Start

### Prerequisites
- Python 3.8+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Run from Source
```bash
# Clone and enter the project directory
cd symlink-manager

# Create a virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt

# Launch the application
.venv/bin/python app.py      # macOS / Linux
.venv\Scripts\python app.py  # Windows
```

### Build a Standalone Executable
```bash
./build.sh          # macOS / Linux
build.bat           # Windows
```
See [BUILD_GUIDE.md](BUILD_GUIDE.md) for detailed instructions.

---

## Usage

### Creating a Symlink

1. Go to the **Create** tab.
2. **Source** — The file or folder you want to link **to** (drag & drop or browse).
3. **Target** — Where the symlink should be created. When you drag a folder, the app auto-generates a name like `symlink-a1b2c3d4`. If you drag a **file**, the app uses its parent directory instead.
4. Toggle any options (Relative, Force, Admin, Confirm).
5. Click **Create Symlink**.

### Managing Symlinks

The **Manage** tab shows all symlinks created through the app:

| Action | How |
|---|---|
| **View** | Table shows target, source, status, notes, and creation date |
| **Edit Notes** | Select a symlink → **Edit Notes** → add a description → **Save** |
| **Delete** | Select a symlink → **Delete** → confirm → removed from disk and tracking |
| **Verify All** | Checks every tracked symlink and reports active, broken, and missing links |
| **Right-click** | Copy target or source path to clipboard |

**Status indicators:**
- ✓ **Active** — Symlink exists and its target is reachable
- ✗ **Broken** — Symlink exists but the original target was moved or deleted
- ? **Missing** — Symlink was deleted outside the app
- ○ **Inactive** — Marked as inactive in tracking

### History & Statistics

The **History** tab shows:
- Recent symlink creations with timestamps and success/failure status
- Most frequently used target directories
- Right-click any row to copy paths

### Settings

The **Settings** tab lets you:
- Switch between **Dark**, **Light**, **Monokai**, **Pastel Pink**, **Pastel Blue**, **Pastel Green**, and **Pastel Orange** themes
- Toggle **Minimize to system tray on close** — closing the window minimizes to tray instead of quitting
- Toggle **Start on system login (minimized to tray)** — register the app to launch automatically when you log in
- Toggle **Persist symlinks** — automatically recreate missing symlinks every 60 seconds (cross-platform)
- Toggle **Merge management** — merge source directory contents into the symlink's folder before recreating (newer files override)
- View platform and Python version info

### System Tray

When enabled, the application minimizes to the system tray instead of quitting:
- **Windows/Linux:** Left-click or double-click toggles window visibility, right-click opens the context menu
- **macOS:** Context menu opens on click, double-click toggles window visibility
- The tray icon menu provides **Open** and **Close** options
- A notification balloon appears when the application is minimized to tray

### Autostart

The **Start on system login** option registers the application to launch automatically when you log in:

| Platform | Mechanism |
|---|---|
| **Windows** | `.lnk` shortcut in `%APPDATA%\...\Startup` |
| **macOS** | `.plist` LaunchAgent in `~/Library/LaunchAgents/` |
| **Linux** | `.desktop` file in `~/.config/autostart/` |

When launched via autostart, the window starts **minimized to the system tray** so it doesn't interrupt your workflow.

### Symlink Persistence

When enabled in **Settings**, the application automatically checks all tracked symlinks every 60 seconds and recreates any that are missing:

| Feature | Detail |
|---|---|
| **Check interval** | Every 60 seconds |
| **Scope** | All symlinks in the tracked list (created via the app) |
| **Recreation** | Uses the original source path automatically |
| **Admin fallback** (Windows) | If a symlink requires admin privileges, the app retries with elevated mode |
| **Status bar** | Shows a notification when symlinks are recreated |
| **Logging** | All persistence operations are logged via `logging` (debug, info, warning, error levels) |
| **Cross-platform** | Works identically on Windows, macOS, and Linux |

> 💡 Enable persistence if you want your symlinks to survive accidental deletion, cleanup tools, or other processes that remove them. The app will silently restore them in the background.

### Merge Management

When enabled alongside persistence, the **Merge management** option copies the contents of the source directory into the folder that contains the symlink **before** recreating it:

| Detail | Description |
|---|---|
| **Behavior** | Recursively copies all files and subdirectories from the source into the symlink's parent directory |
| **Newer files win** | For existing files, the source file only overwrites the destination if its modification time is newer |
| **Existing files** | Files present in the destination but not in the source are preserved (not deleted) |
| **Symlink recreation** | After the merge, the old symlink is removed and a fresh symlink is created pointing back to the source |
| **Safety** | Skips files that are symlinks pointing back to the source to avoid circular copies |
| **Logging** | Every merge operation is logged (files copied, skipped, errors) |
| **Batch-aware** | All symlink creations during a persistence cycle are batched into a single `run_batch()` call — including sub-symlinks produced by merge operations |

> 💡 Merge management is useful when you want to keep a local copy of the symlinked files in the same folder as the symlink itself. This ensures the data is available even if the symlink's source becomes temporarily unavailable.

---

## Configuration Files

All data is stored as JSON in a platform-specific directory:

| Platform | Settings & History |
|---|---|
| **Windows** | `%APPDATA%\SymlinkApp\` |
| **macOS / Linux** | `~/.config/symlink_app/` |

| File | Contents |
|---|---|
| `settings.json` | Window geometry, theme preference, last-used directories, minimize-to-tray, autostart, symlink persistence, merge management |
| `history.json` | Creation records (last 200), recently used source/target paths |
| `managed_symlinks.json` | Tracked symlinks with notes and status |

> ⚠️ Do not edit these files while the app is running — changes will be overwritten.

---

## Platform Notes

### Windows
- Symlinks in system directories (e.g. `C:\Program Files`) require **Admin** mode.
- Uses the `mklink` command internally; `/D` flag for directory junctions.
- Windows 10+ recommended for best symlink support.
- The build process auto-converts PNG icons to ICO format.
- Autostart uses a VBScript-generated `.lnk` shortcut (no extra dependencies).

### macOS
- Full symlink support without special privileges.
- Relative symlinks work across mounted drives.
- Symlinks appear as aliases in Finder.
- Autostart uses a `launchctl`-loaded `.plist` agent.

### Linux
- Full symlink support (ext4, Btrfs, XFS, etc.).
- No special privileges required for standard directories.
- Autostart uses a freedesktop `.desktop` file in `~/.config/autostart/`.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| **"Source path does not exist"** | Verify the path is correct and the file/folder hasn't been moved. Use the **Browse** button. |
| **"Target path already exists"** | Enable **Force** to overwrite, or choose a different target location. |
| **"No write permission"** (Linux/macOS) | Check write permissions on the target directory (`chmod` if needed). |
| **App won't start** | Run from a terminal to see error messages. Ensure Python 3.8+ and all dependencies are installed. |
| **Drag & drop not working** | Your file manager must support standard MIME types. Works on Windows 7+, macOS 10.13+, and modern Linux desktops. If running as admin, the app automatically patches UIPI to allow drag-drop from non-elevated Explorer. |
| **Autostart not working** | Try running the app as administrator (Windows) or check the autostart directory permissions (macOS/Linux). |

NOTE: I have not done enough testing on other platforms between updates ! I would appreciate the feedback C:
---

## Project Structure

```
symlink-manager/
├── app.py                  # Entry point
├── main_window.py          # UI components and event handlers
├── symlink_manager.py      # Core symlink creation/removal logic
├── settings_manager.py     # Settings, history, and symlink tracking persistence
├── drag_drop_widgets.py    # Drag-and-drop enabled QLineEdit
├── batch_operations_widget.py  # Batch symlink creation from CSV/lists
├── tray_icon.py            # System tray icon implementation
├── title_bar.py            # Custom frameless title bar widget
├── startup_manager.py      # Cross-platform autostart registration
├── ui_styles.py            # Dark, light, and custom theme stylesheets
├── build_executable.py     # Cross-platform PyInstaller build script
├── symlink_app.spec        # PyInstaller specification
├── build.sh / build.bat    # Convenience build scripts
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── CHANGELOG.md            # Version history and release notes
├── BUILD_GUIDE.md          # Build and distribution instructions
├── RELEASE_NOTES.md        # Version history and changelog
└── SYMLINK_MANAGEMENT.md   # Symlink tracking reference
```

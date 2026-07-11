# Symlink Manager

A modern, cross-platform GUI application for creating and managing symbolic links on Windows, macOS, and Linux. Built with PyQt6.

---

## Features

### Core
- 🔗 **Create Symlinks** — File and directory symlinks on any supported OS
- 🎨 **Modern GUI** — Dark/light themes with drag-and-drop path input
- 🛡️ **Path Validation** — Validates paths before creating symlinks
- 🔒 **Admin Mode** (Windows) — Create symlinks in system-protected directories
- 📋 **Symlink Tracking** — Automatically track, annotate, verify, and delete symlinks
- 📊 **History & Statistics** — View creation history and most-used paths

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
- Switch between **Dark** and **Light** themes
- View platform and Python version info

---

## Configuration Files

All data is stored as JSON in a platform-specific directory:

| Platform | Settings & History |
|---|---|
| **Windows** | `%APPDATA%\SymlinkApp\` |
| **macOS / Linux** | `~/.config/symlink_app/` |

| File | Contents |
|---|---|
| `settings.json` | Window geometry, theme preference, last-used directories |
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

### macOS
- Full symlink support without special privileges.
- Relative symlinks work across mounted drives.
- Symlinks appear as aliases in Finder.

### Linux
- Full symlink support (ext4, Btrfs, XFS, etc.).
- No special privileges required for standard directories.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| **"Source path does not exist"** | Verify the path is correct and the file/folder hasn't been moved. Use the **Browse** button. |
| **"Target path already exists"** | Enable **Force** to overwrite, or choose a different target location. |
| **"No write permission"** (Linux/macOS) | Check write permissions on the target directory (`chmod` if needed). |
| **App won't start** | Run from a terminal to see error messages. Ensure Python 3.8+ and all dependencies are installed. |
| **Drag & drop not working** | Your file manager must support standard MIME types. Works on Windows 7+, macOS 10.13+, and modern Linux desktops. |

---

## Project Structure

```
symlink-manager/
├── app.py                  # Entry point
├── main_window.py          # UI components and event handlers
├── symlink_manager.py      # Core symlink creation/removal logic
├── settings_manager.py     # Settings, history, and symlink tracking persistence
├── drag_drop_widgets.py   # Drag-and-drop enabled QLineEdit
├── ui_styles.py            # Dark and light theme stylesheets
├── build_executable.py     # Cross-platform PyInstaller build script
├── symlink_app.spec        # PyInstaller specification
├── build.sh / build.bat    # Convenience build scripts
├── requirements.txt        # Python dependencies
├── README.md               # This file
├── BUILD_GUIDE.md          # Build and distribution instructions
├── RELEASE_NOTES.md        # Version history and changelog
└── SYMLINK_MANAGEMENT.md   # Symlink tracking reference
```

# Build Guide — Symlink Manager

This guide explains how to build a standalone executable of **Symlink Manager** from source on Windows, macOS, and Linux using [PyInstaller](https://pyinstaller.org/).

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start (Run from Source)](#quick-start-run-from-source)
- [Build for Windows](#build-for-windows)
- [Build for macOS](#build-for-macos)
- [Build for Linux](#build-for-linux)
- [Build Script Reference](#build-script-reference)
- [Manual PyInstaller Build](#manual-pyinstaller-build)
- [Troubleshooting](#troubleshooting)
- [Output Structure](#output-structure)

---

## Prerequisites

| Requirement | Version |
|---|---|
| **Python** | 3.8 or later |
| **pip / uv** | Latest recommended |
| **PyInstaller** | 6.21.0 (managed by `requirements.txt`) |
| **Pillow** | 10.4.0 (for icon conversion on Windows) |

### Install uv (recommended package manager)

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

> Alternatively, you can use plain `pip` — all commands below work with both `uv` and `pip`.

---

## Quick Start (Run from Source)

```bash
# Clone the repository
git clone https://github.com/noobaly-original/symlink-manager.git
cd symlink-manager

# Create a virtual environment and install dependencies
uv venv
uv pip install -r requirements.txt

# Launch the application
# Windows:
.venv\Scripts\python app.py
# macOS / Linux:
.venv/bin/python app.py
```

---

## Build for Windows

### One-command build

```bat
build.bat
```

Or manually:

```powershell
.venv\Scripts\python build_executable.py
```

### What the build does

1. **Icon conversion** — Converts `symlink_manager_icon.png` → `symlink_manager_icon.ico` with high-quality BMP DIB encoding at multiple sizes (16×16 up to 256×256).
2. **Cleaning** — Removes previous `build/` and `dist/` directories.
3. **PyInstaller** — Bundles the application using `symlink_app.spec`.

### Output

```
dist\SymlinkManager.exe
```

A single `.exe` file that runs without a console window. Launch it directly or move it anywhere.

---

## Build for macOS

### One-command build

```bash
./build.sh
```

Or manually:

```bash
.venv/bin/python build_executable.py
```

### What the build does

1. **Cleaning** — Removes previous `build/` and `dist/` directories.
2. **PyInstaller** — Bundles the application using `symlink_app.spec`, which also creates a `.app` bundle.

### Output

```
dist/SymlinkManager.app
```

Launch with:

```bash
open dist/SymlinkManager.app
```

Or copy `SymlinkManager.app` to your `/Applications` folder.

> **Note:** On macOS, the app uses `symlink_manager_icon.png` directly as the bundle icon. The spec file sets `NSHighResolutionCapable = True` for Retina display support.

---

## Build for Linux

### One-command build

```bash
./build.sh
```

Or manually:

```bash
.venv/bin/python build_executable.py
```

### What the build does

On Linux, the script uses a `--onefile` PyInstaller approach instead of the `.spec` file, producing a single self-contained binary.

### Output

```
dist/SymlinkManager
```

Run it:

```bash
chmod +x dist/SymlinkManager
./dist/SymlinkManager
```

---

## Build Script Reference

### `build.bat` (Windows)

A thin wrapper that:
- Checks for the `.venv` virtual environment.
- Runs `build_executable.py`.

### `build.sh` (macOS / Linux)

A thin wrapper that:
- Checks for the `.venv` virtual environment.
- Runs `build_executable.py`.

### `build_executable.py`

The cross-platform build script that:

| Step | Description |
|---|---|
| **Platform detection** | Identifies Windows, macOS, or Linux |
| **Icon conversion** (Windows) | Converts PNG → ICO using Pillow with manually constructed BMP DIB entries (avoids blurry icons) |
| **Clean** | Removes `build/`, `dist/`, and `__pycache__` directories |
| **PyInstaller** | Runs PyInstaller with the appropriate platform configuration |

### `symlink_app.spec`

The PyInstaller spec file used for Windows and macOS builds:

- **Entry point:** `app.py`
- **Hidden imports:** All custom modules (required for PyInstaller to find them)
- **Icon:** `symlink_manager_icon.ico` (Windows) / `symlink_manager_icon.png` (macOS)
- **Console:** `False` (no terminal window shown)
- **UPX compression:** Enabled
- **macOS bundle:** Creates `SymlinkManager.app` with `NSHighResolutionCapable`

---

## Manual PyInstaller Build

If you prefer to run PyInstaller directly instead of using the build script:

### Windows

```powershell
.venv\Scripts\pyinstaller symlink_app.spec --distpath=dist --workpath=build
```

### macOS

```bash
.venv/bin/pyinstaller symlink_app.spec --distpath=dist --workpath=build
```

### Linux

```bash
.venv/bin/pyinstaller --onefile --windowed --name=SymlinkManager --distpath=dist --workpath=build app.py
```

---

## Troubleshooting

### "Virtual environment not found"

Create one and install dependencies:

```bash
uv venv
uv pip install -r requirements.txt
```

Or with pip:

```bash
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt   # Windows
.venv/bin/pip install -r requirements.txt        # macOS / Linux
```

### "Pillow not installed" (Windows build)

The icon conversion step requires Pillow. Install it:

```bash
uv pip install Pillow
```

The build will still succeed if Pillow is missing — it simply skips the ICO conversion and uses whatever icon is already present.

### Icon looks blurry on Windows

If the `.ico` file already exists but looks pixelated, delete it and rebuild:

```powershell
Remove-Item symlink_manager_icon.ico
.venv\Scripts\python build_executable.py
```

The build script uses a custom BMP DIB encoding (not Pillow's default PNG-in-ICO) for crisp rendering at all sizes.

### "UPX is not available" warning

UPX compression is optional. PyInstaller will warn but continue normally. To remove the warning, install [UPX](https://upx.github.io/) and add it to your `PATH`.

### macOS: "app is damaged" or "cannot be opened"

Remove the quarantine attribute:

```bash
xattr -cr dist/SymlinkManager.app
```

### Linux: "Permission denied"

Make the binary executable:

```bash
chmod +x dist/SymlinkManager
```

---

## Output Structure

After a successful build, the project will contain:

```
symlink-manager/
├── build/                  # PyInstaller working files (intermediate)
├── dist/                   # ✅ Final executable lives here
│   ├── SymlinkManager.exe  #   Windows
│   ├── SymlinkManager.app  #   macOS
│   └── SymlinkManager      #   Linux
├── symlink_manager_icon.ico # Generated icon (Windows)
├── symlink_app.spec         # PyInstaller spec file
├── build_executable.py      # Cross-platform build script
├── build.bat                # Windows build wrapper
├── build.sh                 # macOS/Linux build wrapper
└── ...                      # Source files
```

The `build/` directory can be safely deleted. Only `dist/` contains the final executable.

---

## Version

Current app version: **2.0.2** (defined in `app.py`).
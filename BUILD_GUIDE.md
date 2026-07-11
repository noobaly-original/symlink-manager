# Symlink Manager — Build Guide

Instructions for building standalone executables on Windows, macOS, and Linux using PyInstaller.

---

## Prerequisites

- Python 3.8+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Virtual environment with all dependencies installed:
  ```bash
  uv venv
  uv pip install -r requirements.txt
  ```

---

## Quick Build

### macOS / Linux
```bash
chmod +x build.sh
./build.sh
```

### Windows
```cmd
build.bat
```

Both scripts activate the virtual environment and run `build_executable.py`, which handles platform detection, icon conversion, and PyInstaller invocation.

---

## Output

| Platform | Executable |
|---|---|
| **macOS** | `dist/SymlinkManager.app` |
| **Windows** | `dist\SymlinkManager.exe` |
| **Linux** | `dist/SymlinkManager` |

Run the executable directly or create a shortcut on your Desktop.

---

## Customizing the Build

Edit `symlink_app.spec` or `build_executable.py` to change:

| Customization | How |
|---|---|
| **App name** | Change `--name` in build scripts or `name=` in `.spec` |
| **App icon** | Replace `symlink_manager_icon.png` (PNG) — Windows builds auto-convert to `.ico` |
| **Console output** (debugging) | In `symlink_app.spec`, set `console=True` |
| **Single-file bundle** | Add `--onefile` to the PyInstaller command (larger startup time, single output) |

---

## Manual Build with PyInstaller

If you prefer to run PyInstaller directly:

```bash
# macOS / Linux
.venv/bin/pyinstaller symlink_app.spec

# Windows
.venv\Scripts\pyinstaller.exe symlink_app.spec
```

---

## Troubleshooting

### "module not found"
```bash
uv pip install -r requirements.txt
```

### macOS: "App is damaged"
```bash
xcodelect --install
codesign --remove-signature dist/SymlinkManager.app
codesign -s - dist/SymlinkManager.app
```

### Windows: "Python not found"
```cmd
.venv\Scripts\python.exe build_executable.py
```

### Windows: "icon must be .ico format"
The build script auto-converts `symlink_manager_icon.png` to `.ico` using Pillow. If it fails, install Pillow:
```bash
uv pip install Pillow
```

### Windows: "The specified procedure could not be found"
This is caused by a PyQt6 DLL mismatch. The project pins compatible versions in `requirements.txt`:
- `PyQt6==6.11.0`
- `PyQt6-Qt6==6.11.1`

If the error persists:
1. Use Python 3.10.
2. Verify the pinned versions are installed.
3. Manually copy `python3.dll` or `vcruntime*.dll` from a working Python installation into your venv's `Scripts` folder.

---

## Distribution

### macOS — Create a .dmg
```bash
hdiutil create -volname "SymlinkManager" -srcfolder dist/SymlinkManager.app -ov -format UDZO SymlinkManager.dmg
```

### Windows — Create an Installer
Use [NSIS](https://nsis.sourceforge.io/) or [Inno Setup](https://jrsoftware.org/isinfo.php) to wrap `dist\SymlinkManager.exe`.

### Linux — Create an AppImage
Use [AppImageKit](https://appimage.org/) or package as a `.snap` via Snapcraft.

---

## Build Output Structure

```
dist/
├── SymlinkManager.app/        # macOS bundle
│   └── Contents/MacOS/SymlinkManager
├── SymlinkManager.exe         # Windows executable
└── SymlinkManager             # Linux executable
```

## Performance Notes

- **Bundle size:** ~150–200 MB (Python + Qt libraries bundled).
- **For smaller size:** Use `--onefile` (slower startup, single output file).

# Symlink Manager - Build Guide

This guide explains how to build standalone executable applications for Windows, macOS, and Linux.

## Prerequisites

1. **Python 3.8+** installed on your system
2. **uv** (recommended) or pip for managing packages
3. The virtual environment should be set up (see Installation section)

## Quick Build

### macOS & Linux

```bash
cd /Users/noobaly/Documents/pythontools/Symlink
chmod +x build.sh
./build.sh
```

### Windows

Double-click `build.bat` or run in Command Prompt:

```cmd
cd C:\path\to\Symlink
build.bat
```

## Detailed Build Instructions

### For macOS

1. **Navigate to project directory:**
   ```bash
   cd /Users/noobaly/Documents/pythontools/Symlink
   ```

2. **Ensure virtual environment is activated** (optional but recommended):
   ```bash
   source .venv/bin/activate
   ```

3. **Run the build script:**
   ```bash
   ./build.sh
   ```

4. **Find the executable:**
   - Location: `dist/SymlinkManager.app`
   - Run with: `open dist/SymlinkManager.app`
   - Or double-click `SymlinkManager.app` in Finder

5. **Create a Desktop shortcut (optional):**
   ```bash
   # Create an alias on Desktop
   ln -s "$(pwd)/dist/SymlinkManager.app" ~/Desktop/SymlinkManager.app
   ```

### For Windows

1. **Open Command Prompt or PowerShell**

2. **Navigate to project directory:**
   ```cmd
   cd C:\path\to\Symlink
   ```

3. **Double-click `build.bat`** or run:
   ```cmd
   build.bat
   ```

4. **Find the executable:**
   - Location: `dist\SymlinkManager.exe`
   - Double-click to run or create a shortcut on Desktop

### For Linux

1. **Navigate to project directory:**
   ```bash
   cd /path/to/Symlink
   ```

2. **Run the build script:**
   ```bash
   chmod +x build.sh
   ./build.sh
   ```

3. **Find the executable:**
   - Location: `dist/SymlinkManager`
   - Run with: `./dist/SymlinkManager`
   - Or make it executable: `chmod +x dist/SymlinkManager`

## Build Options

To customize the build, you can edit `build_executable.py` or `symlink_app.spec`:

### Common Customizations

**Change app name:**
- Edit the `--name` parameter in build scripts
- Edit `bundle_identifier` in `symlink_app.spec`

**Add an icon:**
- Create an icon file (`.ico` for Windows, `.icns` for macOS)
- Add to `symlink_app.spec`: `icon='path/to/icon'`

**Enable console output (for debugging):**
- In `symlink_app.spec`, change `console=False` to `console=True`

## Troubleshooting

### Build fails with "module not found"

**Solution:** Ensure all dependencies are installed:
```bash
uv pip install -r requirements.txt
```

### macOS: "App is damaged" message

**Solution:** Code sign the app:
```bash
xcode-select --install
codesign --remove-signature dist/SymlinkManager.app
codesign -s - dist/SymlinkManager.app
```

### Windows: "Python not found" error

**Solution:** Ensure Python is in your PATH or use full path to activate venv:
```cmd
.venv\Scripts\python.exe build_executable.py
```

### Build is too large

**Solution:** The executable includes all Python libraries. To reduce size:
- Remove unused modules from hidden imports
- Use `--strip` option in PyInstaller
- Consider using `--onefile` for single executable file

## Distribution

### macOS

1. Create a `.dmg` file:
   ```bash
   hdiutil create -volname "SymlinkManager" -srcfolder dist/SymlinkManager.app -ov -format UDZO SymlinkManager.dmg
   ```

2. Distribute the `.dmg` file

### Windows

1. The `.exe` file is ready to distribute
2. Optionally create an installer using NSIS or InnoSetup
3. Distribute the `.exe` or installer

### Linux

1. The binary is ready to distribute
2. Optionally create a `.AppImage` using AppImageKit
3. Or package as `.snap` for Snapcraft

## Performance Notes

- Initial startup may take a few seconds as Python initializes
- All libraries are bundled, resulting in a larger file size (~150-200 MB)
- For smallest size, consider using PyInstaller's `--onefile` option

## Build Output Structure

```
dist/
├── SymlinkManager.app/        # macOS app bundle
│   └── Contents/
│       └── MacOS/SymlinkManager
├── SymlinkManager.exe         # Windows executable
├── SymlinkManager             # Linux executable
└── [Other dependencies]
```

## Advanced: Manual Build with PyInstaller

If you prefer manual control, use PyInstaller directly:

```bash
# macOS/Linux
.venv/bin/pyinstaller symlink_app.spec

# Windows
.venv\Scripts\pyinstaller.exe symlink_app.spec
```

## Version Management

Update version in multiple places:
1. `app.py` - `setApplicationVersion("1.0.0")`
2. This guide - Update version numbers mentioned
3. `README.md` - Update version information

## Support

For PyInstaller documentation: https://pyinstaller.org/

For issues specific to this project, ensure:
- All dependencies in `requirements.txt` are installed
- Virtual environment is properly set up
- You're using compatible Python version (3.8+)

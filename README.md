# Symlink Manager

A modern, cross-platform GUI application for creating and managing symlinks on Windows, macOS, and Linux.

THIS PROJECT IS VIBE CODED FROM START TO FINISH !

## Features

### Core Features
- 🔗 **Create Symlinks** - Full support for file and directory symlinks
- 🌍 **Cross-Platform** - Works on Windows, macOS, and Linux
- 🎨 **Modern GUI** - Beautiful dark and light themes with transparency elements
- 🛡️ **Safe Operation** - Validates paths before creating symlinks
- 🔒 **Admin Support** - Windows administrator mode for system-protected directories

### Advanced Options
- **Relative Symlinks** - Create relative symlinks (when on the same drive)
- **Force Creation** - Overwrite existing targets
- **Confirmation Dialog** - Optional confirmation before creation
- **Path Validation** - Check paths before creating symlinks

### Symlink Management
- 📋 **Track Symlinks** - Automatically track all created symlinks
- ✏️ **Edit Notes** - Add notes to remember each symlink's purpose
- 🗑️ **Delete Symlinks** - Safely delete symlinks from disk and tracking
- 🔍 **Verify Status** - Check which symlinks are active, broken, or missing

### History & Statistics
- 📊 **Creation History** - Track all symlink creations with timestamps
- 📈 **Most Used Destinations** - View your most frequently used source and target paths
- 🕐 **Recent Paths** - Quick access to recently used paths
- 💾 **Persistent Settings** - Application settings are saved automatically

## Installation

### Prerequisites
- Python 3.8 or higher
- uv (recommended) or pip

### Option 1: Run from Source (Recommended for Development)

1. **Clone or download the repository:**
   ```bash
   cd /path/to/Symlink
   ```

2. **Create virtual environment with uv:**
   ```bash
   uv venv
   ```

3. **Install dependencies:**
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   .venv/bin/python app.py
   ```

### Option 2: Build Standalone Executable (For Distribution)

**macOS/Linux:**
```bash
./build.sh
open dist/SymlinkManager.app              # macOS
./dist/SymlinkManager                     # Linux
```

**Windows:**
```cmd
build.bat
dist\SymlinkManager.exe
```

See [BUILD_GUIDE.md](BUILD_GUIDE.md) for detailed build instructions.

## Usage

### Creating a Symlink

1. **Launch the application:**
   ```bash
   python app.py
   ```

2. **On the "Create Symlink" tab:**
   - **Source**: Enter or browse to the file/folder you want to link to
   - **Target**: Enter or browse to where the symlink should be created
   - **Options**: Choose any desired options
   - **Create Symlink**: Click the button to create

3. **Confirmation**: If enabled, confirm the operation in the dialog

### Options Explained

- **Relative Symlink**: Creates a symlink with a relative path instead of absolute. Useful for portable directory structures.
- **Force Creation**: Overwrites existing target if it already exists.
- **Administrator Privileges** (Windows only): Required for some system directories.
- **Show Confirmation**: Displays a confirmation dialog before creating the symlink.

### Managing Symlinks

1. **Click the "Manage" tab** to:
   - View all symlinks you've created
   - See their status (active, broken, missing)
   - Add or edit notes for each symlink
   - Delete symlinks from disk and tracking
   - Verify the health of all symlinks

2. **Edit Notes**:
   - Select a symlink
   - Click "Edit Notes"
   - Add information about the symlink's purpose
   - Click "Save"

3. **Delete Symlinks**:
   - Select a symlink
   - Click "Delete"
   - Confirm deletion
   - Symlink is removed from disk and tracking

4. **Verify Symlinks**:
   - Click "Verify All"
   - See a report of all symlinks and their status
   - Identify broken or missing links

### Viewing History

1. **Click the "History" tab** to see:
   - Recent symlink creations with timestamps and status
   - Recently used source paths
   - Recently used target paths

2. **Click "Refresh"** to update the history
3. **Click "Clear History"** to remove all creation records

### Viewing Statistics

1. **Click the "Most Used" tab** to see:
   - Most frequently used source paths
   - Most frequently used target destinations
   - Count of how many times each path was used

2. **Click "Refresh Statistics"** to update

### Managing Settings

1. **Click the "Settings" tab** to:
   - Change the application theme (Dark/Light)
   - Toggle auto-expand paths
   - View system information and config directory

## Platform-Specific Notes

### Windows
- Symlinks may require administrator privileges for system directories
- The `/D` flag is used for directory junctions
- Use the "Administrator Privileges" option if standard creation fails
- Windows 10+ recommended for best symlink support

### macOS
- Full symlink support without special privileges
- Relative symlinks work across mounted drives
- Symlinks appear as aliases in Finder

### Linux
- Full symlink support without special privileges
- Works with all filesystems that support symlinks
- Relative symlinks useful for portable installations

## Configuration

Settings are stored in:
- **Windows**: `%APPDATA%\SymlinkApp\settings.json`
- **macOS/Linux**: `~/.config/symlink_app/settings.json`

History is stored in:
- **Windows**: `%APPDATA%\SymlinkApp\history.json`
- **macOS/Linux**: `~/.config/symlink_app/history.json`

You can manually edit these JSON files, but changes made while the app is running will be overwritten.

## Troubleshooting

### "Source path does not exist"
- Verify the source path is correct
- Ensure the file/folder hasn't been moved or deleted
- Use the Browse button to select the path

### "Target path already exists"
- Check if the target location already has a file or symlink
- Use the "Force Creation" option to overwrite
- Or choose a different target location

### "No write permission for target directory" (Linux/macOS)
- Ensure you have write permissions in the target directory
- Use `chmod` to change permissions if needed
- May need to use `sudo` or administrator privileges

### "Access Denied" (Windows)
- Try enabling "Administrator Privileges" option
- Run the application as Administrator
- Some system directories require elevation

## Command Line Usage

To create symlinks from the command line using the underlying module:

```python
from symlink_manager import SymlinkManager

success, message = SymlinkManager.create_symlink(
    source='/path/to/original',
    target='/path/to/symlink',
    relative=False,
    force=False
)

print(message)
```

## Advanced Features

### Settings API
```python
from settings_manager import SettingsManager

settings = SettingsManager()

# Get a setting
theme = settings.get_setting('theme', 'dark')

# Set a setting
settings.set_setting('theme', 'light')

# Get history
recent_sources = settings.get_history('sources', limit=10)

# Get statistics
most_used = settings.get_most_used_destinations(limit=10)
```

## License

This project is provided as-is for personal and commercial use.

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review the application's status bar for error messages
3. Check the configuration directory for log files

## Contributing

Feel free to submit pull requests or suggestions for improvements!

## Version History

### v1.0.0 (Initial Release)
- Cross-platform symlink creation
- Modern GUI with dark/light themes
- History and statistics tracking
- Settings persistence
- Full path validation
- Platform-specific optimizations

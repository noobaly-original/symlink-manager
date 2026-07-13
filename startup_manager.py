"""
Cross-platform autostart manager for the Symlink application.
Supports Windows, macOS, and Linux startup registration.
"""

import os
import sys
import platform
import logging
from pathlib import Path


class StartupManager:
    """
    Manages application autostart on system login.
    
    Platform implementations:
    - Windows:  Shortcut in %APPDATA%\\Microsoft\\Windows\\Start Menu\\Programs\\Startup
    - macOS:    .plist launch agent in ~/Library/LaunchAgents/
    - Linux:    .desktop file in ~/.config/autostart/
    """

    APP_NAME = "SymlinkManager"

    @staticmethod
    def _get_launch_command() -> tuple:
        """Return (executable, args_list) appropriate for the current runtime.
        
        When running as a PyInstaller bundle, sys.executable is the .exe itself
        and needs no script argument. In script mode, the Python interpreter
        needs the script path as an argument.
        """
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # PyInstaller bundle — the .exe is self-contained
            return sys.executable, []
        else:
            # Running as Python script
            return sys.executable, [str(Path(sys.argv[0]).absolute())]

    @staticmethod
    def is_startup_enabled() -> bool:
        """Check if the app is registered to start on login."""
        system = platform.system()
        if system == "Windows":
            return StartupManager._is_startup_enabled_windows()
        elif system == "Darwin":
            return StartupManager._is_startup_enabled_macos()
        else:  # Linux
            return StartupManager._is_startup_enabled_linux()

    @staticmethod
    def set_startup_enabled(enabled: bool) -> bool:
        """Enable or disable autostart. Returns True on success."""
        system = platform.system()
        try:
            if system == "Windows":
                if enabled:
                    return StartupManager._enable_startup_windows()
                else:
                    return StartupManager._disable_startup_windows()
            elif system == "Darwin":
                if enabled:
                    return StartupManager._enable_startup_macos()
                else:
                    return StartupManager._disable_startup_macos()
            else:  # Linux
                if enabled:
                    return StartupManager._enable_startup_linux()
                else:
                    return StartupManager._disable_startup_linux()
        except Exception as e:
            logging.warning(f"Error {'enabling' if enabled else 'disabling'} autostart: {e}")
            return False

    # ------------------------------------------------------------------ #
    #  Windows
    # ------------------------------------------------------------------ #

    @staticmethod
    def _startup_folder_windows() -> Path:
        """Get the Windows shell:startup folder path."""
        return Path(os.environ.get(
            "APPDATA",
            Path.home() / "AppData" / "Roaming"
        )) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"

    @staticmethod
    def _shortcut_path_windows() -> Path:
        return StartupManager._startup_folder_windows() / f"{StartupManager.APP_NAME}.lnk"

    @staticmethod
    def _is_startup_enabled_windows() -> bool:
        return StartupManager._shortcut_path_windows().exists()

    @staticmethod
    def _enable_startup_windows() -> bool:
        """Create a shortcut in the Windows Startup folder using a VBScript helper."""
        shortcut_path = StartupManager._shortcut_path_windows()
        executable, args = StartupManager._get_launch_command()
        target = executable

        if args:
            args_str = f'"{args[0]}"'
        else:
            args_str = ""

        # Use a VBScript to create the shortcut (most reliable method without pywin32)
        vbs_code = f'''
Set ws = CreateObject("WScript.Shell")
Set sc = ws.CreateShortcut("{shortcut_path}")
sc.TargetPath = "{target}"
sc.Arguments = "{args_str}"
sc.WorkingDirectory = "{Path(sys.argv[0]).parent}"
sc.Description = "Symlink Manager"
sc.Save
'''
        vbs_path = Path(os.environ["TEMP"]) / f"{StartupManager.APP_NAME}_create_shortcut.vbs"
        try:
            vbs_path.write_text(vbs_code.strip())
            import subprocess
            subprocess.run(["cscript", "//nologo", str(vbs_path)], check=True,
                           capture_output=True, timeout=10)
            vbs_path.unlink(missing_ok=True)
            return shortcut_path.exists()
        except Exception:
            return False

    @staticmethod
    def _disable_startup_windows() -> bool:
        shortcut = StartupManager._shortcut_path_windows()
        if shortcut.exists():
            shortcut.unlink()
            return True
        return True  # Already removed

    # ------------------------------------------------------------------ #
    #  macOS
    # ------------------------------------------------------------------ #

    @staticmethod
    def _launch_agents_dir() -> Path:
        return Path.home() / "Library" / "LaunchAgents"

    @staticmethod
    def _plist_path() -> Path:
        return StartupManager._launch_agents_dir() / f"{StartupManager.APP_NAME}.plist"

    @staticmethod
    def _is_startup_enabled_macos() -> bool:
        return StartupManager._plist_path().exists()

    @staticmethod
    def _enable_startup_macos() -> bool:
        """Create a LaunchAgent plist that runs the app on login."""
        plist_dir = StartupManager._launch_agents_dir()
        plist_dir.mkdir(parents=True, exist_ok=True)

        executable, args = StartupManager._get_launch_command()

        # Build ProgramArguments array
        prog_args = f"        <string>{executable}</string>\n"
        for arg in args:
            prog_args += f"        <string>{arg}</string>\n"

        plist_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{StartupManager.APP_NAME}</string>
    <key>ProgramArguments</key>
    <array>
{prog_args}    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
'''
        plist_path = StartupManager._plist_path()
        plist_path.write_text(plist_content)

        # Load the agent so it takes effect immediately
        import subprocess
        subprocess.run(["launchctl", "load", str(plist_path)],
                       check=False, capture_output=True)
        return plist_path.exists()

    @staticmethod
    def _disable_startup_macos() -> bool:
        plist = StartupManager._plist_path()
        if plist.exists():
            # Unload first
            import subprocess
            subprocess.run(["launchctl", "unload", str(plist)],
                           check=False, capture_output=True)
            plist.unlink()
        return True

    # ------------------------------------------------------------------ #
    #  Linux
    # ------------------------------------------------------------------ #

    @staticmethod
    def _autostart_dir() -> Path:
        return Path.home() / ".config" / "autostart"

    @staticmethod
    def _desktop_file_path() -> Path:
        return StartupManager._autostart_dir() / f"{StartupManager.APP_NAME}.desktop"

    @staticmethod
    def _is_startup_enabled_linux() -> bool:
        return StartupManager._desktop_file_path().exists()

    @staticmethod
    def _enable_startup_linux() -> bool:
        """Create a .desktop file in ~/.config/autostart/."""
        autostart_dir = StartupManager._autostart_dir()
        autostart_dir.mkdir(parents=True, exist_ok=True)

        executable, args = StartupManager._get_launch_command()
        if args:
            exec_line = f"{executable} {' '.join(args)}"
        else:
            exec_line = executable

        desktop_content = f"""[Desktop Entry]
Type=Application
Name=Symlink Manager
Exec={exec_line}
Comment=Manage symbolic links
X-GNOME-Autostart-enabled=true
"""
        desktop_path = StartupManager._desktop_file_path()
        desktop_path.write_text(desktop_content)
        desktop_path.chmod(0o755)
        return desktop_path.exists()

    @staticmethod
    def _disable_startup_linux() -> bool:
        desktop = StartupManager._desktop_file_path()
        if desktop.exists():
            desktop.unlink()
        return True
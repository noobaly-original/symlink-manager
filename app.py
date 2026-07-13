#!/usr/bin/env python3
"""
Symlink Manager - Cross-platform GUI application for creating symlinks.
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from main_window import SymlinkMainWindow
from settings_manager import SettingsManager
from startup_manager import StartupManager


def setup_logging():
    """Set up application logging to symlmg.log in the app root directory.
    The log file is truncated (cleared) on every app start."""
    log_path = Path(__file__).parent / "symlmg.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename=str(log_path),
        filemode="w",  # Truncate on every start
        encoding="utf-8",
    )
    # Also log to console for development
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
    logging.getLogger().addHandler(console)
    return log_path


def main():
    """Main entry point for the application."""
    log_path = setup_logging()
    logging.info(f"Symlink Manager v2.0.1 starting — log: {log_path}")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Symlink Manager")
    app.setApplicationVersion("2.0.1")
    
    # Don't quit when the last window is closed (for system tray support)
    app.setQuitOnLastWindowClosed(False)
    
    # Check if we should start minimized (e.g. launched on system login)
    temp_settings = SettingsManager()
    start_minimized = temp_settings.get_setting('start_on_login', False)
    
    window = SymlinkMainWindow()
    
    if start_minimized and window.tray_icon.is_available:
        # Start minimized to tray — hide the main window
        window.hide()
        window.tray_icon.update_window_visibility(False)
        # Show a tray notification
        window.tray_icon.show_message(
            "Symlink Manager",
            "Application is running in the system tray.",
            duration=3000
        )
    else:
        window.show()
    
    # Log window size for debugging
    logging.info(f"Window size: {window.width()}x{window.height()}")
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

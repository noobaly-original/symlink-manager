#!/usr/bin/env python3
"""
Symlink Manager - Cross-platform GUI application for creating symlinks.
"""

import sys
from PyQt6.QtWidgets import QApplication
from main_window import SymlinkMainWindow
from settings_manager import SettingsManager
from startup_manager import StartupManager


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Symlink Manager")
    app.setApplicationVersion("1.1.1")
    
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
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

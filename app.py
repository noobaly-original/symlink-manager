#!/usr/bin/env python3
"""
Symlink Manager - Cross-platform GUI application for creating symlinks.
"""

import sys
from PyQt6.QtWidgets import QApplication
from main_window import SymlinkMainWindow
from settings_manager import SettingsManager
from startup_manager import StartupManager


def _patch_uipi_for_drag_drop():
    """
    When running elevated on Windows, UIPI (User Interface Privilege Isolation)
    blocks drag-and-drop from non-elevated processes (e.g. Explorer).

    Calls ChangeWindowMessageFilter to allow OLE drag-drop messages through
    at the process level. Must be called before any windows are created.
    """
    if sys.platform != 'win32':
        return
    try:
        import ctypes
        from ctypes import wintypes

        if ctypes.windll.shell32.IsUserAnAdmin() == 0:
            return  # Not elevated — no UIPI issue

        MSGFLT_ALLOW = 1
        WM_DROPFILES = 0x0233
        WM_COPYDATA = 0x004A
        WM_COPYGLOBALDATA = 0x0049

        user32 = ctypes.windll.user32

        try:
            change_filter = user32.ChangeWindowMessageFilter
            change_filter.argtypes = [wintypes.UINT, wintypes.DWORD]
            change_filter.restype = wintypes.BOOL
            for msg in (WM_DROPFILES, WM_COPYDATA, WM_COPYGLOBALDATA):
                change_filter(msg, MSGFLT_ALLOW)
        except AttributeError:
            pass
    except Exception:
        pass  # Best-effort; drag-drop may silently fail


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Symlink Manager")
    app.setApplicationVersion("2.0.0")
    
    # Don't quit when the last window is closed (for system tray support)
    app.setQuitOnLastWindowClosed(False)
    
    # When running elevated on Windows, UIPI blocks drag-drop from Explorer.
    # Patch the message filter to allow OLE drag-drop messages.
    _patch_uipi_for_drag_drop()
    
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
    
    # Print window size for debugging
    print(f"Window size: {window.width()}x{window.height()}")
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

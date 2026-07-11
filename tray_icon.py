"""
Cross-platform system tray icon for the Symlink Manager.
Supports Windows, macOS, and Linux with platform-specific behaviors.
"""

import sys
import platform
from pathlib import Path
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QApplication
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import QObject, pyqtSignal


class TrayIcon(QObject):
    """
    System tray icon with cross-platform support.

    Provides a tray icon with context menu for quick access to:
    - Open the main window
    - Close the application

    Platform-specific behaviors:
    - Windows: Left-click toggles window, right-click opens menu
    - macOS: Both clicks open menu, app menu bar integration
    - Linux: Left-click toggles window, right-click opens menu
    - Double-click on any platform opens the main window
    """

    # Signals
    show_window_requested = pyqtSignal()
    hide_window_requested = pyqtSignal()
    quit_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize the tray icon."""
        super().__init__(parent)
        self.tray_icon = None
        self.tray_menu = None
        self._is_visible = False
        self._window_visible = True

        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            print("Warning: System tray is not available on this system.")
            return

        self._setup_tray_icon()

    def _setup_tray_icon(self):
        """Set up the system tray icon and menu."""
        # Create the tray icon
        self.tray_icon = QSystemTrayIcon()

        # Set icon
        icon_path = Path(__file__).parent / 'symlink_manager_icon.png'
        if icon_path.exists():
            self.tray_icon.setIcon(QIcon(str(icon_path)))
        else:
            # Use a default application icon as fallback
            self.tray_icon.setIcon(QApplication.style().standardIcon(
                self._get_standard_icon()
            ))

        self.tray_icon.setToolTip("Symlink Manager")

        # Create the context menu (must be parented to the tray icon)
        self._create_menu()

        # Connect signals
        self.tray_icon.activated.connect(self._on_tray_activated)

        # Show the tray icon
        self.tray_icon.show()
        self._is_visible = True

    def _get_standard_icon(self):
        """Get the appropriate standard icon for the platform."""
        from PyQt6.QtGui import QStyle
        return QStyle.StandardPixmap.SP_ComputerIcon

    def _create_menu(self):
        """Create the tray icon context menu."""
        # Parent the menu to the tray icon to prevent garbage collection
        self.tray_menu = QMenu()

        # Open action
        self.open_action = QAction("Open", self.tray_menu)
        self.open_action.triggered.connect(self._on_open)
        self.tray_menu.addAction(self.open_action)

        self.tray_menu.addSeparator()

        # Close action
        self.close_action = QAction("Close", self.tray_menu)
        self.close_action.triggered.connect(self._on_quit)
        self.tray_menu.addAction(self.close_action)

        # Assign the menu to the tray icon
        self.tray_icon.setContextMenu(self.tray_menu)

    def _on_tray_activated(self, reason):
        """
        Handle tray icon activation.

        Platform-specific behavior:
        - Double-click always opens the main window
        - Single-click on Windows/Linux toggles the window
        - Right-click shows the context menu automatically
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            # Double-click always opens the app
            self._ensure_window_visible()
        elif reason == QSystemTrayIcon.ActivationReason.Trigger:
            # Single click behavior varies by platform
            if platform.system() == "Darwin":
                # On macOS, single click typically opens the menu
                pass
            else:
                # On Windows/Linux, single click toggles window
                self._toggle_window()
        elif reason == QSystemTrayIcon.ActivationReason.Context:
            # Context menu is shown automatically by the OS
            pass

    def _ensure_window_visible(self):
        """Ensure the main window is visible."""
        if not self._window_visible:
            self.show_window_requested.emit()
            self._window_visible = True

    def _toggle_window(self):
        """Toggle the main window visibility."""
        if self._window_visible:
            self.hide_window_requested.emit()
            self._window_visible = False
        else:
            self.show_window_requested.emit()
            self._window_visible = True

    def _on_open(self):
        """Handle Open action from menu."""
        self._ensure_window_visible()

    def _on_quit(self):
        """Handle quit/close action from menu."""
        self.quit_requested.emit()

    def show_message(self, title: str, message: str, icon=None, duration: int = 5000):
        """
        Show a balloon/tooltip message from the tray icon.

        Args:
            title: Message title
            message: Message body
            icon: Message icon type (QSystemTrayIcon.MessageIcon)
            duration: Display duration in milliseconds
        """
        if self.tray_icon and self._is_visible:
            if icon is None:
                icon = QSystemTrayIcon.MessageIcon.Information
            self.tray_icon.showMessage(title, message, icon, duration)

    def set_tooltip(self, tooltip: str):
        """Set the tray icon tooltip text."""
        if self.tray_icon:
            self.tray_icon.setToolTip(tooltip)

    def update_window_visibility(self, visible: bool):
        """Update the internal window visibility state."""
        self._window_visible = visible

    def hide(self):
        """Hide the tray icon."""
        if self.tray_icon and self._is_visible:
            self.tray_icon.hide()
            self._is_visible = False

    def show(self):
        """Show the tray icon."""
        if self.tray_icon and not self._is_visible:
            self.tray_icon.show()
            self._is_visible = True

    @property
    def is_visible(self) -> bool:
        """Check if the tray icon is visible."""
        return self._is_visible

    @property
    def is_available(self) -> bool:
        """Check if system tray is available on this system."""
        return QSystemTrayIcon.isSystemTrayAvailable()
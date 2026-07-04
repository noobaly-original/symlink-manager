#!/usr/bin/env python3
"""
Symlink Manager - Cross-platform GUI application for creating symlinks.
"""

import sys
from PyQt6.QtWidgets import QApplication
from main_window import SymlinkMainWindow


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Symlink Manager")
    app.setApplicationVersion("1.0.0")
    
    window = SymlinkMainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()

"""
Custom widgets with drag-and-drop support for file paths.
"""

from pathlib import Path
from PyQt6.QtWidgets import QLineEdit, QWidget, QLabel
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent


class DragDropLineEdit(QLineEdit):
    """QLineEdit widget that accepts file/folder drag and drop."""
    
    # Signal emitted when files are dropped
    filesDropped = pyqtSignal(str)
    
    def __init__(self, parent=None, accept_files=True, accept_dirs=True):
        """
        Initialize the drag-drop line edit.
        
        Args:
            parent: Parent widget
            accept_files: Whether to accept file drops
            accept_dirs: Whether to accept directory drops
        """
        super().__init__(parent)
        self.accept_files = accept_files
        self.accept_dirs = accept_dirs
        
        # Enable drag and drop
        self.setAcceptDrops(True)
        
        # Set placeholder text for visual feedback
        self.setPlaceholderText("Drag and drop a file or folder here...")
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            # Visual feedback
            self.setStyleSheet(self.styleSheet() + "\nQLineEdit { border: 2px solid #89b4fa; }")
        else:
            event.ignore()
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event."""
        # Reset style
        self.setStyleSheet(self.styleSheet().replace("\nQLineEdit { border: 2px solid #89b4fa; }", ""))
        event.accept()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        # Reset style
        self.setStyleSheet(self.styleSheet().replace("\nQLineEdit { border: 2px solid #89b4fa; }", ""))
        
        mime_data = event.mimeData()
        
        if mime_data.hasUrls():
            urls = mime_data.urls()
            
            if urls:
                # Get the first dropped item
                file_path = urls[0].toLocalFile()
                path_obj = Path(file_path)
                
                # Validate the dropped path
                is_valid = False
                
                if path_obj.is_file() and self.accept_files:
                    is_valid = True
                elif path_obj.is_dir() and self.accept_dirs:
                    is_valid = True
                
                if is_valid:
                    self.setText(file_path)
                    self.filesDropped.emit(file_path)
                    event.acceptProposedAction()
                else:
                    event.ignore()
            else:
                event.ignore()
        else:
            event.ignore()


class DragDropLabel(QLabel):
    """QLabel widget that shows drag-drop area visual feedback."""
    
    def __init__(self, parent=None):
        """Initialize the drag-drop label."""
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setText("Drop files here")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event."""
        mime_data = event.mimeData()
        
        if mime_data.hasUrls():
            urls = mime_data.urls()
            
            if urls:
                file_path = urls[0].toLocalFile()
                self.setText(f"Dropped: {Path(file_path).name}")
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

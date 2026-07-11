"""
Custom frameless title bar widget with minimize, maximize/restore, and close buttons.
Theme-aware and draggable for moving the window.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QIcon, QMouseEvent


class TitleBarButton(QPushButton):
    """A compact title bar button with hover effect."""

    def __init__(self, text: str, parent=None):
        super().__init__(text, parent)
        self.setFixedSize(46, 32)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.setCursor(Qt.CursorShape.ArrowCursor)


class TitleBar(QWidget):
    """Custom title bar for frameless windows."""

    minimize_requested = pyqtSignal()
    maximize_requested = pyqtSignal()
    close_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._dragging = False
        self._drag_position = QPoint()
        self._maximized = False

        self.setFixedHeight(36)
        self.setObjectName("titleBar")

        layout = QHBoxLayout()
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(4)

        # App icon
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(20, 20)
        layout.addWidget(self.icon_label)

        # Title
        self.title_label = QLabel("Symlink Manager")
        self.title_label.setObjectName("titleLabel")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(self.title_label)

        layout.addStretch()

        # Minimize button
        self.min_btn = TitleBarButton("─")
        self.min_btn.setObjectName("minimizeButton")
        self.min_btn.clicked.connect(self.minimize_requested.emit)
        layout.addWidget(self.min_btn)

        # Maximize / Restore button
        self.max_btn = TitleBarButton("□")
        self.max_btn.setObjectName("maximizeButton")
        self.max_btn.clicked.connect(self._on_maximize_clicked)
        layout.addWidget(self.max_btn)

        # Close button
        self.close_btn = TitleBarButton("✕")
        self.close_btn.setObjectName("closeButton")
        self.close_btn.clicked.connect(self.close_requested.emit)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)

    def set_window_icon(self, icon: QIcon):
        """Set the app icon displayed in the title bar."""
        self.icon_label.setPixmap(icon.pixmap(20, 20))

    def set_title(self, title: str):
        """Set the title text."""
        self.title_label.setText(title)

    def update_maximize_state(self, maximized: bool):
        """Update the maximize button icon based on window state."""
        self._maximized = maximized
        self.max_btn.setText("❐" if maximized else "□")

    def _on_maximize_clicked(self):
        """Toggle maximize/restore state."""
        self._maximized = not self._maximized
        self.max_btn.setText("❐" if self._maximized else "□")
        self.maximize_requested.emit()

    def mousePressEvent(self, event: QMouseEvent):
        """Start window drag."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragging = True
            self._drag_position = event.globalPosition().toPoint()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        """Drag the window."""
        if self._dragging:
            window = self.window()
            delta = event.globalPosition().toPoint() - self._drag_position
            new_pos = window.pos() + delta

            if self._maximized:
                # If maximized and dragged, restore then position
                self._on_maximize_clicked()
                ratio = event.position().x() / max(self.width(), 1)
                new_x = int(event.globalPosition().toPoint().x() -
                            self.width() * ratio)
                new_pos = QPoint(new_x,
                                 event.globalPosition().toPoint().y() - 10)

            window.move(new_pos)
            self._drag_position = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent):
        """End window drag."""
        self._dragging = False
        event.accept()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Double-click to toggle maximize."""
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_maximize_clicked()
            event.accept()
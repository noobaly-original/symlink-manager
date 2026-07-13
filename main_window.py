"""
Main application window for the Symlink Manager.
"""

import sys
import uuid
import logging
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QCheckBox, QFileDialog, QMessageBox,
    QTabWidget, QComboBox, QTableWidget,
    QTableWidgetItem, QDialog, QStatusBar, QMenu,
    QApplication, QHeaderView, QSpinBox
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtGui import QClipboard

from symlink_manager import SymlinkManager
from settings_manager import SettingsManager
from ui_styles import get_theme_stylesheet
from drag_drop_widgets import DragDropLineEdit
from batch_operations_widget import BatchOperationsWidget
from tray_icon import TrayIcon
from startup_manager import StartupManager
from title_bar import TitleBar


class MergeSettingsDialog(QDialog):
    """Dialog for configuring merge source → target directory pairs."""

    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.setWindowTitle("Merge Settings")
        self.setMinimumSize(550, 350)
        self.setModal(True)
        self._build_ui()
        self._load_pairs()

    def _build_ui(self):
        layout = QVBoxLayout()

        help_label = QLabel(
            "Configure source and target directory pairs for merge operations.\n"
            "When persistence runs, the target directory is scanned for files not\n"
            "in the source. These files are moved to the source and symlinked back."
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("font-size: 9pt; color: #888; margin-bottom: 6px;")
        layout.addWidget(help_label)

        # Table
        self.pairs_table = QTableWidget()
        self.pairs_table.setColumnCount(3)
        self.pairs_table.setHorizontalHeaderLabels(['Source Directory', 'Target Directory', ''])
        hdr = self.pairs_table.horizontalHeader()
        hdr.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        hdr.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.pairs_table.setColumnWidth(2, 60)
        layout.addWidget(self.pairs_table)

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("+ Add Pair")
        add_btn.clicked.connect(self._add_pair)
        btn_layout.addWidget(add_btn)
        btn_layout.addStretch()
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(close_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_pairs(self):
        pairs = self.settings_manager.get_merge_pairs()
        self.pairs_table.setRowCount(len(pairs))
        for row, pair in enumerate(pairs):
            self._populate_row(row, pair['source'], pair['target'])

    def _populate_row(self, row, source, target):
        source_edit = QLineEdit(source)
        source_edit.setPlaceholderText("C:\\Source\\Dir")
        target_edit = QLineEdit(target)
        target_edit.setPlaceholderText("C:\\Symlink\\Dir")
        remove_btn = QPushButton("✕")
        remove_btn.setMaximumWidth(30)
        remove_btn.clicked.connect(lambda: self._remove_pair_row(row))
        self.pairs_table.setCellWidget(row, 0, source_edit)
        self.pairs_table.setCellWidget(row, 1, target_edit)
        self.pairs_table.setCellWidget(row, 2, remove_btn)

    def _add_pair(self):
        row = self.pairs_table.rowCount()
        self.pairs_table.insertRow(row)
        self._populate_row(row, "", "")

    def _remove_pair_row(self, row):
        self.pairs_table.removeRow(row)

    def accept(self):
        """Save all pairs and close."""
        pairs = []
        for row in range(self.pairs_table.rowCount()):
            src = self.pairs_table.cellWidget(row, 0)
            tgt = self.pairs_table.cellWidget(row, 1)
            if src and tgt:
                s = src.text().strip()
                t = tgt.text().strip()
                if s and t:
                    pairs.append({'source': s, 'target': t})
        # Clear and re-save
        self.settings_manager.symlinks['merge_pairs'] = pairs
        self.settings_manager.save_symlinks()
        super().accept()


class CreationWorker:
    """Worker for background symlink creation."""
    
    def __init__(self, source: str, target: str, relative: bool = False,
                 force: bool = False, admin: bool = False):
        self.source = source
        self.target = target
        self.relative = relative
        self.force = force
        self.admin = admin
    
    def run(self):
        """Run the symlink creation."""
        return SymlinkManager.create_symlink(
            self.source, self.target, self.relative, self.force, self.admin
        )


class SymlinkMainWindow(QMainWindow):
    """Main application window."""

    # Edge resize margin in pixels
    RESIZE_MARGIN = 6

    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.settings_manager = SettingsManager()
        self.symlink_manager = SymlinkManager()
        self._is_resizing = False
        self._resize_edge = 0
        self._drag_start_pos = None
        self._drag_start_geo = None
        self._pending_maximize = False
        self._missing_symlinks_prompted = False
        self._admin_retry_pending = False
        
        self.initUI()
        self.load_settings()

        # Persistence timer — periodically checks and recreates missing symlinks
        self._persist_timer = QTimer(self)
        interval = self.settings_manager.get_setting('persistence_interval', 60) * 1000
        self._persist_timer.setInterval(interval)
        self._persist_timer.timeout.connect(self._run_persistence_check)
        if self.settings_manager.get_setting('persist_symlinks', False):
            self._persist_timer.start()
            logging.info(f"Persistence timer started (interval={interval//1000}s)")
        
    def showEvent(self, event):
        """Restore maximized state after the window is first shown."""
        super().showEvent(event)
        if self._pending_maximize:
            self._pending_maximize = False
            self.showMaximized()

    def initUI(self):
        """Initialize the user interface."""
        self.setWindowTitle('Symlink Manager')
        self.setMinimumSize(660, 660)
        self.resize(650, 420)
        
        # Remove the native window frame (cross-platform)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        # Enable mouse tracking for resize cursor changes
        self.setMouseTracking(True)
        
        # Set application icon
        icon_path = Path(__file__).parent / 'symlink_manager_icon.png'
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # --- Build the frameless layout ---
        # Outer container with zero margins — title bar sits at top
        self._outer_widget = QWidget()
        self._outer_widget.setObjectName("framelessWindow")
        self.setCentralWidget(self._outer_widget)
        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(2)
        self._outer_widget.setLayout(outer_layout)
        
        # Custom title bar
        self.title_bar = TitleBar(self._outer_widget)
        self.title_bar.set_title("Symlink Manager")
        if icon_path.exists():
            self.title_bar.set_window_icon(QIcon(str(icon_path)))
        outer_layout.addWidget(self.title_bar)
        
        # Content widget — everything below the title bar
        content_widget = QWidget()
        content_widget.setObjectName("windowContent")
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(12, 10, 12, 12)
        self._content_layout.setSpacing(10)
        content_widget.setLayout(self._content_layout)
        outer_layout.addWidget(content_widget, 1)  # stretch factor 1
        
        # Create tab widget for different sections
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { padding: 6px 12px; }")
        self._content_layout.addWidget(self.tabs, stretch=1)
        
        # Tab 1: Create Symlink
        create_tab = self.create_symlink_tab()
        self.tabs.addTab(create_tab, "Create")
        
        # Tab 2: Manage Symlinks
        manage_tab = self.create_manage_symlinks_tab()
        self.tabs.addTab(manage_tab, "Manage")
        
        # Tab 3: Batch Operations
        self.batch_widget = BatchOperationsWidget()
        self.batch_widget.operation_completed.connect(self._on_batch_operation_completed)
        self.tabs.addTab(self.batch_widget, "Batch")

        # Tab 4: History & Statistics
        history_tab = self.create_history_tab()
        self.tabs.addTab(history_tab, "History")
        
        # Tab 5: Settings
        settings_tab = self.create_settings_tab()
        self.tabs.addTab(settings_tab, "Settings")
        
        # Connect tab change signal to refresh manage tab
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Connect title bar signals
        self.title_bar.minimize_requested.connect(self._on_title_minimize)
        self.title_bar.maximize_requested.connect(self._on_title_maximize)
        self.title_bar.close_requested.connect(self._on_title_close)
        
        # Status bar (still works in frameless mode)
        self.statusBar().showMessage("Ready")
        
        # Apply theme
        theme = self.settings_manager.get_setting('theme', 'dark')
        self.setStyleSheet(get_theme_stylesheet(theme))
        
        # Initialize system tray icon
        self._setup_tray_icon()
    
    def _setup_tray_icon(self):
        """Set up the system tray icon."""
        self.tray_icon = TrayIcon(self)
        
        if self.tray_icon.is_available:
            # Connect tray icon signals
            self.tray_icon.show_window_requested.connect(self.show_window)
            self.tray_icon.hide_window_requested.connect(self.hide_window)
            self.tray_icon.quit_requested.connect(self.quit_application)
            
            # Load minimize-to-tray preference
            self.minimize_to_tray = self.settings_manager.get_setting('minimize_to_tray', True)
    
    # ---- Title bar handlers ----
    
    def _on_title_minimize(self):
        """Minimize the window."""
        self.showMinimized()
    
    def _on_title_maximize(self):
        """Toggle maximize/restore."""
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
        self.title_bar.update_maximize_state(self.isMaximized())
    
    def _on_title_close(self):
        """Close the window (respects minimize-to-tray)."""
        self.close()
    
    def changeEvent(self, event):
        """Sync title bar maximize button when window state changes."""
        if event.type() == event.Type.WindowStateChange:
            self.title_bar.update_maximize_state(self.isMaximized())
        super().changeEvent(event)
    
    # ---- Resize from edges (frameless window) ----
    
    def _get_resize_edge(self, pos):
        """Determine which edge (bitmask) the cursor is on."""
        margin = self.RESIZE_MARGIN
        x, y = pos.x(), pos.y()
        w, h = self.width(), self.height()
        
        edge = 0
        if x <= margin:
            edge |= 1  # left
        if x >= w - margin:
            edge |= 2  # right
        if y <= margin:
            edge |= 4  # top
        if y >= h - margin:
            edge |= 8  # bottom
        return edge
    
    def _resize_cursor_from_edge(self, edge):
        """Get cursor shape for a given edge bitmask."""
        if edge in (5, 5+2, 5+8):  # top-left or corners with top+left
            return Qt.CursorShape.SizeFDiagCursor
        if edge in (6, 6+1, 6+8):  # top-right
            return Qt.CursorShape.SizeBDiagCursor
        if edge in (9, 9+2, 9+4):  # bottom-left
            return Qt.CursorShape.SizeBDiagCursor
        if edge in (10, 10+1, 10+4):  # bottom-right
            return Qt.CursorShape.SizeFDiagCursor
        if edge & 1 or edge & 2:  # left or right
            return Qt.CursorShape.SizeHorCursor
        if edge & 4 or edge & 8:  # top or bottom
            return Qt.CursorShape.SizeVerCursor
        return Qt.CursorShape.ArrowCursor
    
    def mouseMoveEvent(self, event):
        """Update cursor for resize edges, or perform resize."""
        if self._is_resizing:
            # Perform the actual resize
            self._do_resize(event.globalPosition().toPoint())
        elif not self.isMaximized():
            edge = self._get_resize_edge(event.pos())
            self.setCursor(self._resize_cursor_from_edge(edge))
        super().mouseMoveEvent(event)
    
    def mousePressEvent(self, event):
        """Start window resize from edges."""
        if event.button() == Qt.MouseButton.LeftButton and not self.isMaximized():
            edge = self._get_resize_edge(event.pos())
            if edge:
                self._is_resizing = True
                self._resize_edge = edge
                self._drag_start_pos = event.globalPosition().toPoint()
                self._drag_start_geo = self.geometry()
                event.accept()
                return
        super().mousePressEvent(event)
    
    def mouseReleaseEvent(self, event):
        """End window resize."""
        self._is_resizing = False
        self._resize_edge = 0
        super().mouseReleaseEvent(event)
    
    def _do_resize(self, global_pos):
        """Resize the window based on the active edge(s)."""
        delta = global_pos - self._drag_start_pos
        geo = self._drag_start_geo
        min_w = self.minimumWidth()
        min_h = self.minimumHeight()
        
        new_left = geo.x()
        new_top = geo.y()
        new_w = geo.width()
        new_h = geo.height()
        
        edge = self._resize_edge
        
        if edge & 1:  # left
            new_left = geo.x() + delta.x()
            new_w = geo.width() - delta.x()
            if new_w < min_w:
                new_w = min_w
                new_left = geo.x() + geo.width() - min_w
        
        if edge & 2:  # right
            new_w = geo.width() + delta.x()
            if new_w < min_w:
                new_w = min_w
        
        if edge & 4:  # top
            new_top = geo.y() + delta.y()
            new_h = geo.height() - delta.y()
            if new_h < min_h:
                new_h = min_h
                new_top = geo.y() + geo.height() - min_h
        
        if edge & 8:  # bottom
            new_h = geo.height() + delta.y()
            if new_h < min_h:
                new_h = min_h
        
        self.setGeometry(new_left, new_top, new_w, new_h)
    
    def show_window(self):
        """Show the main window."""
        self.show()
        self.raise_()
        self.activateWindow()
        self.tray_icon.update_window_visibility(True)
    
    def hide_window(self):
        """Hide the main window to system tray."""
        self.hide()
        self.tray_icon.update_window_visibility(False)
    
    def quit_application(self):
        """Quit the application from tray."""
        self.save_window_geometry()
        self.tray_icon.cleanup()
        QApplication.quit()
    
    def focus_create_tab(self):
        """Switch to the create symlink tab."""
        self.tabs.setCurrentIndex(0)
    
    def save_window_geometry(self):
        """Save the current window geometry (size, position, maximized state)."""
        geometry = {
            'width': self.width(),
            'height': self.height(),
            'x': self.x(),
            'y': self.y(),
            'maximized': self.isMaximized(),
        }
        self.settings_manager.set_setting('window_geometry', geometry)
    
    def create_symlink_tab(self) -> QWidget:
        """Create the symlink creation tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Source selection
        source_label = QLabel("Source:")
        source_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(source_label)
        
        source_layout = QHBoxLayout()
        self.source_input = DragDropLineEdit(accept_files=True, accept_dirs=True)
        self.source_input.setPlaceholderText("Drag & drop or browse...")
        self.source_input.filesDropped.connect(lambda path: self.settings_manager.set_setting('last_source_dir', str(Path(path).parent)))
        source_layout.addWidget(self.source_input)
        
        source_browse_btn = QPushButton("Browse")
        source_browse_btn.setMaximumWidth(100)
        source_browse_btn.clicked.connect(self.browse_source)
        source_layout.addWidget(source_browse_btn)
        layout.addLayout(source_layout)
        
        # Target selection
        target_label = QLabel("Target:")
        target_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(target_label)
        
        target_layout = QHBoxLayout()
        self.target_input = DragDropLineEdit(accept_files=True, accept_dirs=True)
        self.target_input.setPlaceholderText("Drag & drop or browse...")
        self.target_input.filesDropped.connect(self.on_target_path_selected)
        target_layout.addWidget(self.target_input)
        
        target_browse_btn = QPushButton("Browse")
        target_browse_btn.setMaximumWidth(100)
        target_browse_btn.clicked.connect(self.browse_target)
        target_layout.addWidget(target_browse_btn)
        layout.addLayout(target_layout)
        
        # Options (simplified)
        options_layout = QHBoxLayout()
        
        self.relative_checkbox = QCheckBox("Relative")
        self.relative_checkbox.setChecked(
            self.settings_manager.get_setting('create_relative', False)
        )
        self.relative_checkbox.toggled.connect(
            lambda c: self.settings_manager.set_setting('create_relative', c))
        options_layout.addWidget(self.relative_checkbox)
        
        self.force_checkbox = QCheckBox("Force")
        self.force_checkbox.setChecked(
            self.settings_manager.get_setting('create_force', False)
        )
        self.force_checkbox.toggled.connect(
            lambda c: self.settings_manager.set_setting('create_force', c))
        options_layout.addWidget(self.force_checkbox)
        
        if self.symlink_manager.is_windows():
            self.admin_checkbox = QCheckBox("Admin")
            self.admin_checkbox.setChecked(
                self.settings_manager.get_setting('create_admin', False)
            )
            self.admin_checkbox.toggled.connect(
                lambda c: self.settings_manager.set_setting('create_admin', c))
            options_layout.addWidget(self.admin_checkbox)
        else:
            self.admin_checkbox = None
        
        self.confirm_checkbox = QCheckBox("Confirm")
        default_confirm = self.settings_manager.get_setting('confirm_before_create', True)
        self.confirm_checkbox.setChecked(default_confirm)
        options_layout.addWidget(self.confirm_checkbox)
        
        layout.addLayout(options_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton("Create Symlink")
        create_btn.setObjectName("successButton")
        create_btn.clicked.connect(self.create_symlink)
        button_layout.addWidget(create_btn)
        
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self.clear_inputs)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_manage_symlinks_tab(self) -> QWidget:
        """Create the manage symlinks tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Symlinks table
        table_label = QLabel("Tracked Symlinks:")
        table_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(table_label)
        
        self.symlinks_table = QTableWidget()
        self.symlinks_table.setColumnCount(5)
        self.symlinks_table.setHorizontalHeaderLabels(['Target', 'Source', 'Status', 'Notes', 'Created'])
        # Interactive mode — user can resize all columns manually.
        header = self.symlinks_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)
        self.symlinks_table.setColumnWidth(0, 200)  # Target
        self.symlinks_table.setColumnWidth(1, 180)  # Source
        self.symlinks_table.setColumnWidth(2, 80)   # Status
        self.symlinks_table.setColumnWidth(3, 150)  # Notes
        self.symlinks_table.setColumnWidth(4, 90)   # Created
        self.symlinks_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.symlinks_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.symlinks_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.symlinks_table.customContextMenuRequested.connect(self.show_manage_table_context_menu)
        
        layout.addWidget(self.symlinks_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_symlinks_table)
        button_layout.addWidget(refresh_btn)
        
        edit_btn = QPushButton("Edit Notes")
        edit_btn.clicked.connect(self.edit_symlink_notes)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("warningButton")
        delete_btn.clicked.connect(self.delete_symlink)
        button_layout.addWidget(delete_btn)
        
        verify_btn = QPushButton("Verify All")
        verify_btn.clicked.connect(self.verify_all_symlinks)
        button_layout.addWidget(verify_btn)
        
        layout.addLayout(button_layout)
        
        # Status info
        self.symlinks_status_label = QLabel()
        self.symlinks_status_label.setWordWrap(True)
        self.symlinks_status_label.setStyleSheet("font-size: 9pt; color: #999;")
        layout.addWidget(self.symlinks_status_label)
        
        widget.setLayout(layout)
        self.refresh_symlinks_table()
        return widget
    
    def on_tab_changed(self, index: int):
        """Handle tab change event."""
        if index == 1:  # Manage tab index
            self.refresh_symlinks_table()
    
    def refresh_symlinks_table(self):
        """Refresh the symlinks table and handle missing symlinks (once per session)."""
        # Verify all symlinks to get current status
        status = self.settings_manager.verify_symlinks()
        
        # Find and handle missing symlinks (prompt only once per session)
        missing_links = [link for link in status['symlinks'] if link['status'] == 'missing']
        
        if missing_links and not self._missing_symlinks_prompted:
            self._missing_symlinks_prompted = True
            missing_paths = '\n'.join([link['target'] for link in missing_links])
            
            persist_active = self.settings_manager.get_setting('persist_symlinks', False)
            persist_note = (
                "\n\nPersistence is enabled — missing symlinks will be automatically "
                "recreated in the background." if persist_active else
                "\n\nTip: Enable 'Persist symlinks' in Settings to automatically "
                "recreate missing symlinks in the background."
            )
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Missing Symlinks Detected")
            msg_box.setText(
                f"The following symlinks are missing:\n\n{missing_paths}"
                f"{persist_note}\n\n"
                f"Remove them from the manager?"
            )
            msg_box.setStandardButtons(
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            msg_box.setDefaultButton(QMessageBox.StandardButton.Yes)
            
            reply = msg_box.exec()
            
            if reply == QMessageBox.StandardButton.Yes:
                for link in missing_links:
                    self.settings_manager.remove_symlink(link['target'])
        
        # Now get updated symlinks list
        symlinks = self.settings_manager.get_all_symlinks()
        self.symlinks_table.setRowCount(len(symlinks))
        
        # Re-verify to get current status after removal
        status = self.settings_manager.verify_symlinks()
        status_map = {link['target']: link['status'] for link in status['symlinks']}
        
        for row, link in enumerate(symlinks):
            # Target — store full path, display full path (table shows ellipsis)
            target_item = QTableWidgetItem(link['target'])
            target_item.setData(Qt.ItemDataRole.UserRole, link['target'])
            self.symlinks_table.setItem(row, 0, target_item)
            
            # Source
            source_item = QTableWidgetItem(link['source'])
            self.symlinks_table.setItem(row, 1, source_item)
            
            # Status - get actual status from verification
            current_status = status_map.get(link['target'], 'unknown')
            if current_status == 'active':
                status_text = "✓ Active"
            elif current_status == 'broken':
                status_text = "✗ Broken"
            elif current_status == 'missing':
                status_text = "? Missing"
            else:
                status_text = "○ Inactive"
            
            status_item = QTableWidgetItem(status_text)
            self.symlinks_table.setItem(row, 2, status_item)
            
            # Notes
            notes_item = QTableWidgetItem(link.get('notes', ''))
            self.symlinks_table.setItem(row, 3, notes_item)
            
            # Created
            created = link.get('created_at', '')[:10]
            created_item = QTableWidgetItem(created)
            self.symlinks_table.setItem(row, 4, created_item)
        
        # Update status
        self.update_symlinks_status()
    
    def update_symlinks_status(self):
        """Update the symlinks status label."""
        symlinks = self.settings_manager.get_all_symlinks()
        status_info = self.settings_manager.verify_symlinks()
        
        status_text = f"Total: {status_info['total']} | Active: {status_info['active']} | Broken: {status_info['broken']} | Missing: {status_info['missing']}"
        self.symlinks_status_label.setText(status_text)
    
    def edit_symlink_notes(self):
        """Edit notes for selected symlink."""
        current_row = self.symlinks_table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a symlink to edit.")
            return
        
        target = self.symlinks_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        symlink = self.settings_manager.get_symlink_by_target(target)
        
        if not symlink:
            QMessageBox.warning(self, "Error", "Symlink not found.")
            return
        
        # Create edit dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Symlink Notes")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Target info
        info_label = QLabel(f"Target: {target}")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("font-size: 9pt; color: #888;")
        layout.addWidget(info_label)
        
        # Notes input
        notes_label = QLabel("Notes:")
        layout.addWidget(notes_label)
        
        notes_input = QLineEdit()
        notes_input.setText(symlink.get('notes', ''))
        notes_input.setPlaceholderText("Add notes about this symlink...")
        layout.addWidget(notes_input)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_symlink_notes(dialog, target, notes_input.text()))
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        
        dialog.exec()
    
    def save_symlink_notes(self, dialog: QDialog, target: str, notes: str):
        """Save notes for a symlink."""
        if self.settings_manager.update_symlink(target, notes=notes):
            QMessageBox.information(self, "Success", "Notes saved successfully.")
            dialog.accept()
            self.refresh_symlinks_table()
        else:
            QMessageBox.critical(self, "Error", "Failed to save notes.")
    
    def delete_symlink(self):
        """Delete selected symlink."""
        current_row = self.symlinks_table.currentRow()
        
        if current_row < 0:
            QMessageBox.warning(self, "No Selection", "Please select a symlink to delete.")
            return
        
        target = self.symlinks_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Confirmation dialog
        reply = QMessageBox.question(
            self,
            "Delete Symlink",
            f"Delete symlink at:\n{target}\n\nThis will also remove the symlink from disk.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Remove from disk
        success, message = self.symlink_manager.remove_symlink(target)
        
        if success:
            # Remove from tracking
            self.settings_manager.remove_symlink(target)
            QMessageBox.information(self, "Success", f"Symlink deleted successfully.\n{message}")
            self.statusBar().showMessage("Symlink deleted")
            self.refresh_symlinks_table()
        else:
            QMessageBox.critical(self, "Error", f"Failed to delete symlink:\n{message}")
    
    def verify_all_symlinks(self):
        """Verify all tracked symlinks."""
        status = self.settings_manager.verify_symlinks()
        
        # Build status report
        report = f"Symlink Verification Report\n"
        report += f"{'='*40}\n"
        report += f"Total: {status['total']}\n"
        report += f"Active: {status['active']}\n"
        report += f"Broken Links: {status['broken']}\n"
        report += f"Missing: {status['missing']}\n\n"
        
        report += "Details:\n"
        for link in status['symlinks']:
            status_icon = "✓" if link['status'] == 'active' else "✗" if link['status'] == 'broken' else "?"
            report += f"{status_icon} {link['status'].upper()}: {link['target']}\n"
        
        # Show report
        msg = QMessageBox(self)
        msg.setWindowTitle("Symlink Verification Report")
        msg.setText(report)
        msg.setFont(QFont("Monospace", 9))
        msg.exec()
        
        self.statusBar().showMessage(f"Verification complete: {status['active']} active, {status['broken']} broken")
    
    def show_manage_table_context_menu(self, position):
        """Show context menu for manage tab symlinks table."""
        menu = QMenu()
        
        # Get the item at the clicked position
        item = self.symlinks_table.itemAt(position)
        if item is None:
            return
        
        row = item.row()
        
        # Get target and source from the row
        target_item = self.symlinks_table.item(row, 0)
        source_item = self.symlinks_table.item(row, 1)
        
        target_path = target_item.data(Qt.ItemDataRole.UserRole) if target_item.data(Qt.ItemDataRole.UserRole) else target_item.text()
        source_path = source_item.text() if source_item else ""
        
        # Add copy options
        if target_path:
            copy_target_action = menu.addAction("Copy Target")
            copy_target_action.triggered.connect(lambda: self.copy_to_clipboard(target_path))
        
        if source_path:
            copy_source_action = menu.addAction("Copy Source")
            copy_source_action.triggered.connect(lambda: self.copy_to_clipboard(source_path))
        
        if target_path or source_path:
            menu.exec(self.symlinks_table.mapToGlobal(position))
    
    def show_history_table_context_menu(self, position):
        """Show context menu for history table."""
        menu = QMenu()
        
        # Get the item at the clicked position
        item = self.history_table.itemAt(position)
        if item is None:
            return
        
        row = item.row()
        
        # Get source and target from the row
        source_item = self.history_table.item(row, 1)
        target_item = self.history_table.item(row, 2)
        
        source_path = source_item.text() if source_item else ""
        target_path = target_item.text() if target_item else ""
        
        # Add copy options
        if source_path:
            copy_source_action = menu.addAction("Copy Source")
            copy_source_action.triggered.connect(lambda: self.copy_to_clipboard(source_path))
        
        if target_path:
            copy_target_action = menu.addAction("Copy Target")
            copy_target_action.triggered.connect(lambda: self.copy_to_clipboard(target_path))
        
        if source_path or target_path:
            menu.exec(self.history_table.mapToGlobal(position))
    
    def copy_to_clipboard(self, text: str):
        """Copy text to clipboard."""
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.statusBar().showMessage(f"Copied to clipboard", 2000)

    def create_history_tab(self) -> QWidget:
        """Create the history tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)
        
        # Recent creations
        history_label = QLabel("Creation History:")
        history_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(history_label)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(4)
        self.history_table.setHorizontalHeaderLabels(['Time', 'Source', 'Target', 'Status'])
        hdr = self.history_table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        hdr.setStretchLastSection(True)
        self.history_table.setColumnWidth(0, 150)  # Time
        self.history_table.setColumnWidth(1, 200)  # Source
        self.history_table.setColumnWidth(2, 200)  # Target
        self.history_table.setColumnWidth(3, 60)   # Status
        self.history_table.setMaximumHeight(200)
        self.history_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.history_table.customContextMenuRequested.connect(self.show_history_table_context_menu)
        
        layout.addWidget(self.history_table)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_history)
        button_layout.addWidget(refresh_btn)
        
        clear_history_btn = QPushButton("Clear History")
        clear_history_btn.setObjectName("warningButton")
        clear_history_btn.clicked.connect(self.clear_creation_history)
        button_layout.addWidget(clear_history_btn)
        
        layout.addLayout(button_layout)
        
        # Most used destinations
        dest_label = QLabel("Most Used Destinations:")
        dest_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(dest_label)
        
        self.most_used_targets_table = QTableWidget()
        self.most_used_targets_table.setColumnCount(2)
        self.most_used_targets_table.setHorizontalHeaderLabels(['Path', 'Count'])
        hdr = self.most_used_targets_table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        hdr.setStretchLastSection(True)
        self.most_used_targets_table.setColumnWidth(0, 300)  # Path
        self.most_used_targets_table.setColumnWidth(1, 80)   # Count
        
        layout.addWidget(self.most_used_targets_table)
        
        widget.setLayout(layout)
        self.refresh_history()
        self.refresh_statistics()
        return widget
    
    def create_destinations_tab(self) -> QWidget:
        """Create the most used destinations tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Most used sources
        sources_group = QGroupBox("Most Used Sources")
        sources_layout = QVBoxLayout()
        
        sources_label = QLabel("Most frequently symlinked source paths:")
        sources_layout.addWidget(sources_label)
        
        self.most_used_sources_table = QTableWidget()
        self.most_used_sources_table.setColumnCount(2)
        self.most_used_sources_table.setHorizontalHeaderLabels(['Source Path', 'Count'])
        hdr = self.most_used_sources_table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        hdr.setStretchLastSection(True)
        self.most_used_sources_table.setColumnWidth(0, 300)  # Source Path
        self.most_used_sources_table.setColumnWidth(1, 80)   # Count
        
        sources_layout.addWidget(self.most_used_sources_table)
        sources_group.setLayout(sources_layout)
        layout.addWidget(sources_group)
        
        # Most used targets
        targets_group = QGroupBox("Most Used Destinations")
        targets_layout = QVBoxLayout()
        
        targets_label = QLabel("Most frequent target paths for symlinks:")
        targets_layout.addWidget(targets_label)
        
        self.most_used_targets_table = QTableWidget()
        self.most_used_targets_table.setColumnCount(2)
        self.most_used_targets_table.setHorizontalHeaderLabels(['Target Path', 'Count'])
        hdr = self.most_used_targets_table.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        hdr.setStretchLastSection(True)
        self.most_used_targets_table.setColumnWidth(0, 300)  # Target Path
        self.most_used_targets_table.setColumnWidth(1, 80)   # Count
        
        targets_layout.addWidget(self.most_used_targets_table)
        targets_group.setLayout(targets_layout)
        layout.addWidget(targets_group)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Statistics")
        refresh_btn.clicked.connect(self.refresh_statistics)
        layout.addWidget(refresh_btn)
        
        widget.setLayout(layout)
        self.refresh_statistics()
        return widget
    
    def create_settings_tab(self) -> QWidget:
        """Create the settings tab."""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # ========== Theme ==========
        theme_group = QGroupBox("Appearance")
        theme_inner = QHBoxLayout()
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("font-weight: bold;")
        theme_inner.addWidget(theme_label)

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Dark', 'Light', 'Monokai', 'Pastel Pink', 'Pastel Blue', 'Pastel Green', 'Pastel Orange'])
        current_theme = self.settings_manager.get_setting('theme', 'dark')
        theme_display_map = {
            'dark': 'Dark',
            'light': 'Light',
            'monokai': 'Monokai',
            'pastel_pink': 'Pastel Pink',
            'pastel_blue': 'Pastel Blue',
            'pastel_green': 'Pastel Green',
            'pastel_orange': 'Pastel Orange',
        }
        self.theme_combo.setCurrentText(theme_display_map.get(current_theme, 'Dark'))
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setMinimumWidth(100)
        self.theme_combo.setMaximumWidth(150)
        theme_inner.addWidget(self.theme_combo)
        theme_inner.addStretch()
        theme_group.setLayout(theme_inner)
        layout.addWidget(theme_group)

        # ========== System Tray ==========
        tray_group = QGroupBox("System Tray")
        tray_layout = QVBoxLayout()

        self.minimize_to_tray_checkbox = QCheckBox("Minimize to system tray on close")
        self.minimize_to_tray_checkbox.setChecked(
            self.settings_manager.get_setting('minimize_to_tray', True)
        )
        self.minimize_to_tray_checkbox.toggled.connect(self._on_minimize_to_tray_toggled)
        tray_layout.addWidget(self.minimize_to_tray_checkbox)

        self.start_on_login_checkbox = QCheckBox("Start on system login (minimized to tray)")
        self.start_on_login_checkbox.setChecked(
            self.settings_manager.get_setting('start_on_login', False)
        )
        self.start_on_login_checkbox.toggled.connect(self._on_start_on_login_toggled)
        tray_layout.addWidget(self.start_on_login_checkbox)

        tray_info = QLabel(
            "When enabled, closing the window will minimize it to the system tray "
            "instead of quitting the application. Use the tray icon to show or quit."
        )
        tray_info.setWordWrap(True)
        tray_info.setStyleSheet("font-size: 9pt; color: #888;")
        tray_layout.addWidget(tray_info)

        tray_group.setLayout(tray_layout)
        layout.addWidget(tray_group)

        # ========== Persistence & Merge ==========
        pm_group = QGroupBox("Persistence & Merge")
        pm_layout = QVBoxLayout()

        self.persist_symlinks_checkbox = QCheckBox("Persist symlinks — automatically recreate missing symlinks")
        self.persist_symlinks_checkbox.setChecked(
            self.settings_manager.get_setting('persist_symlinks', False)
        )
        self.persist_symlinks_checkbox.toggled.connect(self._on_persist_symlinks_toggled)
        pm_layout.addWidget(self.persist_symlinks_checkbox)

        # Interval spin row
        interval_layout = QHBoxLayout()
        interval_layout.setContentsMargins(24, 0, 0, 0)
        interval_label = QLabel("Check interval (seconds):")
        interval_label.setStyleSheet("font-size: 9pt;")
        interval_layout.addWidget(interval_label)

        self.persist_interval_spin = QSpinBox()
        self.persist_interval_spin.setRange(10, 3600)
        self.persist_interval_spin.setSuffix(" s")
        self.persist_interval_spin.setValue(
            self.settings_manager.get_setting('persistence_interval', 60)
        )
        self.persist_interval_spin.valueChanged.connect(self._on_persistence_interval_changed)
        self.persist_interval_spin.setMinimumWidth(80)
        self.persist_interval_spin.setMaximumWidth(100)
        interval_layout.addWidget(self.persist_interval_spin)
        interval_layout.addStretch()
        pm_layout.addLayout(interval_layout)

        # Merge Settings button
        merge_btn_layout = QHBoxLayout()
        self.merge_settings_btn = QPushButton("Merge Settings...")
        self.merge_settings_btn.clicked.connect(self._open_merge_settings)
        merge_btn_layout.addWidget(self.merge_settings_btn)
        merge_btn_layout.addStretch()
        pm_layout.addLayout(merge_btn_layout)

        pm_info = QLabel(
            "Persistence checks all tracked symlinks every N seconds and\n"
            "automatically recreates any that are missing.\n\n"
            "Merge Settings lets you define source → target directory pairs.\n"
            "When a merge pair matches a missing symlink, the target folder is\n"
            "scanned for items not in the source. Those are copied to source,\n"
            "removed from target, and replaced with new symlinks."
        )
        pm_info.setWordWrap(True)
        pm_info.setStyleSheet("font-size: 9pt; color: #888;")
        pm_layout.addWidget(pm_info)

        pm_group.setLayout(pm_layout)
        layout.addWidget(pm_group)

        # ========== Information ==========
        info_group = QGroupBox("About")
        info_layout = QVBoxLayout()
        info_text = QLabel()
        info_text.setWordWrap(True)
        info_text.setStyleSheet("font-size: 10pt; line-height: 1.5;")
        info_text.setText(
            f"<b>Symlink Manager v2.1.0</b><br>"
            f"<b>Platform:</b> {self.get_platform_name()}<br>"
            f"<b>Python:</b> {sys.version.split()[0]}"
        )
        info_layout.addWidget(info_text)
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
    def _on_minimize_to_tray_toggled(self, checked: bool):
        """Handle minimize-to-tray checkbox toggle."""
        self.minimize_to_tray = checked
        self.settings_manager.set_setting('minimize_to_tray', checked)
    
    def _on_start_on_login_toggled(self, checked: bool):
        """Handle start-on-login checkbox toggle."""
        success = StartupManager.set_startup_enabled(checked)
        if success:
            self.settings_manager.set_setting('start_on_login', checked)
        else:
            # Revert the checkbox if the operation failed
            self.start_on_login_checkbox.blockSignals(True)
            self.start_on_login_checkbox.setChecked(not checked)
            self.start_on_login_checkbox.blockSignals(False)
            QMessageBox.warning(
                self, "Autostart Error",
                f"Failed to {'enable' if checked else 'disable'} autostart. "
                "Try running as administrator or check permissions."
            )

    def _on_persist_symlinks_toggled(self, checked: bool):
        """Handle persist-symlinks checkbox toggle."""
        self.settings_manager.set_setting('persist_symlinks', checked)
        if checked:
            interval = self.settings_manager.get_setting('persistence_interval', 60) * 1000
            self._persist_timer.setInterval(interval)
            self._persist_timer.start()
            logging.info(f"Persistence enabled — timer started (interval={interval//1000}s)")
            # Run an immediate check so the user sees the effect right away
            self._run_persistence_check()
        else:
            self._persist_timer.stop()
            logging.info("Persistence disabled — timer stopped")

    def _on_persistence_interval_changed(self, seconds: int):
        """Handle persistence interval spinbox change."""
        self.settings_manager.set_setting('persistence_interval', seconds)
        if self._persist_timer.isActive():
            self._persist_timer.setInterval(seconds * 1000)
            logging.info(f"Persistence interval changed to {seconds}s")

    def _on_batch_operation_completed(self, source: str, success: bool, message: str):
        """Called when a batch operation completes — refresh the Manage tab."""
        if self.tabs.currentIndex() == 1:
            self.refresh_symlinks_table()

    def _open_merge_settings(self):
        """Open the Merge Settings dialog."""
        dialog = MergeSettingsDialog(self.settings_manager, self)
        dialog.exec()

    def browse_source(self):
        """Open file dialog to select source."""
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select Source Path")
        
        last_dir = self.settings_manager.get_setting('last_source_dir', str(Path.home()))
        dialog.setDirectory(last_dir)
        
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            path = dialog.selectedFiles()[0]
            self.source_input.setText(path)
            self.settings_manager.set_setting('last_source_dir', str(Path(path).parent))
    
    def on_target_path_selected(self, path: str):
        """Handle target path selection from drag-drop or browse."""
        symlink_id = str(uuid.uuid4())[:8]  # First 8 chars of UUID
        path_obj = Path(path)
        # If a file was dropped, use its parent directory as the target base
        if path_obj.is_file():
            path_obj = path_obj.parent
        target_path = str(path_obj / f"symlink-{symlink_id}")
        self.target_input.setText(target_path)
        self.settings_manager.set_setting('last_target_dir', str(path_obj))
    
    def browse_target(self):
        """Open file dialog to select target directory."""
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select Target Location")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        
        last_dir = self.settings_manager.get_setting('last_target_dir', str(Path.home()))
        dialog.setDirectory(last_dir)
        
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            path = dialog.selectedFiles()[0]
            self.on_target_path_selected(path)
    
    def validate_paths(self):
        """Validate the entered paths."""
        source = self.source_input.text().strip()
        target = self.target_input.text().strip()

        # On Windows, ensure the source path actually exists before proceeding.
        # This prevents attempts to create a symlink when the source is an invalid
        # path such as "hello.png/symlink1234" which may be generated by the app
        # but does not correspond to an existing file or directory.
        if self.symlink_manager.is_windows():
            from pathlib import Path as _Path
            source_path = _Path(source)
            if not source_path.exists():
                QMessageBox.warning(
                    self,
                    "Invalid Source",
                    f"The source path does not exist or is invalid: {source}"
                )
                return
        
        if not source or not target:
            QMessageBox.warning(self, "Validation Error", "Please enter both source and target paths.")
            return
        
        valid, error = self.symlink_manager.validate_paths(source, target)
        
        if valid:
            info_msg = f"✓ Paths are valid\n\n"
            info_msg += f"Source: {source}\n"
            info_msg += f"Target: {target}"
            QMessageBox.information(self, "Validation Success", info_msg)
            self.statusBar().showMessage("Paths validated successfully")
        else:
            QMessageBox.warning(self, "Validation Error", error)
            self.statusBar().showMessage(f"Validation error: {error}")
    
    def create_symlink(self):
        """Create the symlink."""
        source = self.source_input.text().strip()
        target = self.target_input.text().strip()
        
        if not source or not target:
            QMessageBox.warning(self, "Error", "Please enter both source and target paths.")
            return
        
        # Show confirmation if enabled
        if self.confirm_checkbox.isChecked():
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Confirm Symlink Creation")
            msg_box.setText(f"Create symlink?\n\nSource: {source}\nTarget: {target}")
            msg_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            
            if msg_box.exec() != QMessageBox.StandardButton.Ok:
                return
        
        # Create symlink
        relative = self.relative_checkbox.isChecked()
        force = self.force_checkbox.isChecked()
        admin = self.admin_checkbox.isChecked() if self.admin_checkbox else False
        
        success, message = self.symlink_manager.create_symlink(
            source, target, relative, force, admin
        )
        
        # Handle admin-required response — offer to retry with admin mode
        if not success and message == "ADMIN_REQUIRED":
            reply = QMessageBox.question(
                self,
                "Administrator Privileges Required",
                "Creating symlinks on Windows requires administrator privileges.\n\n"
                "Do you want to retry with Admin mode enabled?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                # Set admin checkbox and retry
                if self.admin_checkbox:
                    self.admin_checkbox.setChecked(True)
                self.create_symlink()
            return
        
        # Record in history
        self.settings_manager.record_creation(source, target, success, message)
        
        # Add to history
        if success:
            self.settings_manager.add_to_history(source, 'source')
            self.settings_manager.add_to_history(target, 'target')
            # Add to managed symlinks
            self.settings_manager.add_symlink(source, target, notes="")
            QMessageBox.information(self, "Success", message)
            self.statusBar().showMessage("Symlink created successfully")
            self.clear_inputs()
        else:
            QMessageBox.critical(self, "Error", message)
            self.statusBar().showMessage(f"Error: {message}")
        
        self.refresh_history()
    
    def clear_inputs(self):
        """Clear input fields."""
        self.source_input.clear()
        self.target_input.clear()
        self.relative_checkbox.setChecked(
            self.settings_manager.get_setting('create_relative', False)
        )
        self.force_checkbox.setChecked(
            self.settings_manager.get_setting('create_force', False)
        )
    
    def refresh_history(self):
        """Refresh the history display."""
        # Update creation history table
        creations = self.settings_manager.get_history('creations', 20)
        self.history_table.setRowCount(len(creations))
        
        for row, creation in enumerate(creations):
            time_item = QTableWidgetItem(creation['timestamp'][:19])
            source_item = QTableWidgetItem(creation['source'])
            target_item = QTableWidgetItem(creation['target'])
            status = "✓" if creation['success'] else "✗"
            status_item = QTableWidgetItem(status)
            
            self.history_table.setItem(row, 0, time_item)
            self.history_table.setItem(row, 1, source_item)
            self.history_table.setItem(row, 2, target_item)
            self.history_table.setItem(row, 3, status_item)
    
    def refresh_statistics(self):
        """Refresh the statistics display."""
        # Most used targets
        most_used_targets = self.settings_manager.get_most_used_destinations(10)
        self.most_used_targets_table.setRowCount(len(most_used_targets))
        
        for row, (target, count) in enumerate(most_used_targets):
            target_item = QTableWidgetItem(target)
            count_item = QTableWidgetItem(str(count))
            
            self.most_used_targets_table.setItem(row, 0, target_item)
            self.most_used_targets_table.setItem(row, 1, count_item)
    
    def clear_creation_history(self):
        """Clear the creation history."""
        reply = QMessageBox.question(
            self,
            "Clear History",
            "Are you sure you want to clear all creation history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings_manager.clear_history('creations')
            self.refresh_history()
            self.refresh_statistics()
    
    def change_theme(self, theme_name: str):
        """Change the application theme."""
        # Map display names to internal theme keys
        theme_map = {
            'Dark': 'dark',
            'Light': 'light',
            'Monokai': 'monokai',
            'Pastel Pink': 'pastel_pink',
            'Pastel Blue': 'pastel_blue',
            'Pastel Green': 'pastel_green',
            'Pastel Orange': 'pastel_orange',
        }
        theme = theme_map.get(theme_name, 'dark')
        self.settings_manager.set_setting('theme', theme)
        self.setStyleSheet(get_theme_stylesheet(theme))
    
    def load_settings(self):
        """Load and apply saved settings."""
        geometry = self.settings_manager.get_setting('window_geometry')
        if geometry:
            w = geometry.get('width', 650)
            h = geometry.get('height', 420)
            x = geometry.get('x')
            y = geometry.get('y')
            if x is not None and y is not None:
                self.setGeometry(x, y, w, h)
            else:
                self.resize(w, h)
            # Defer maximize until the window is shown (avoid flash)
            self._pending_maximize = geometry.get('maximized', False)

    def closeEvent(self, event):
        """Handle window close event."""
        self.save_window_geometry()
        
        # Minimize to tray instead of quitting if enabled and tray is available
        if self.minimize_to_tray and self.tray_icon.is_available:
            self.hide_window()
            self.tray_icon.show_message(
                "Symlink Manager",
                "Application minimized to system tray. "
                "Double-click the tray icon to restore."
            )
            event.ignore()
        else:
            # Actually quit the application (setQuitOnLastWindowClosed is False)
            self.quit_application()
            event.accept()
    
    def _run_persistence_check(self):
        """Check all tracked symlinks, run merge on every tick, recreate any that are missing."""
        symlinks = self.settings_manager.get_all_symlinks()
        if not symlinks:
            logging.debug("Persistence check: no tracked symlinks to verify")
            return

        status = self.settings_manager.verify_symlinks()
        missing = [link for link in status['symlinks'] if link['status'] == 'missing']
        merge_pairs = self.settings_manager.get_merge_pairs()

        # ---- Phase 1: Merge — runs EVERY tick regardless of missing symlinks ----
        batch_ops = []       # (source, target, is_dir, force, relative, admin)
        merge_tracked = []   # new sub-symlinks to track after batch
        seen_targets = set() # silently ignore duplicate target paths
        needs_admin = False

        if merge_pairs:
            for link in status['symlinks']:
                target = link['target']
                source = link['source']
                if target in seen_targets:
                    continue
                symlink_parent = str(Path(target).parent.resolve())
                for pair in merge_pairs:
                    if str(Path(pair['target']).resolve()) == symlink_parent:
                        merge_ok, merge_msg, new_symlinks = self.symlink_manager.merge_directories(
                            pair['source'], target
                        )
                        if not merge_ok:
                            logging.warning(f"Persistence recovery: merge failed for '{target}': {merge_msg}")
                        else:
                            logging.info(f"Persistence recovery: merge for '{target}': {merge_msg}")
                            for ns in new_symlinks:
                                merge_tracked.append(ns)
                                ns_target = ns['target']
                                seen_targets.add(ns_target)
                                batch_ops.append((ns['source'], ns_target,
                                                  ns.get('is_dir', Path(ns['source']).is_dir()), False, False, False))
                        break

        # ---- Phase 2: Add missing symlinks to batch ----
        if not missing:
            logging.debug("Persistence check: all symlinks are present")
            self._admin_retry_pending = False
        else:
            logging.info(f"Persistence check: {len(missing)} symlink(s) missing — attempting recovery")
            for entry in missing:
                source = entry['source']
                target = entry['target']
                if target in seen_targets:
                    continue
                seen_targets.add(target)
                try:
                    source_path = Path(source)
                    is_dir = source_path.is_dir() if source_path.exists() else False
                    batch_ops.append((source, target, is_dir, False, False, False))
                except Exception as e:
                    logging.error(f"Persistence recovery: exception for '{target}': {e}")

        if not batch_ops:
            logging.debug("Persistence check: no operations to perform")
            return

        # ---- Phase 2: Run all symlink creations as a single batch ----
        overall_success, batch_msg, results = self.symlink_manager.run_batch(batch_ops)

        # Check if any failures were due to admin privileges
        needs_admin = False
        recreated = sum(1 for _, _, ok, _ in results if ok)
        failed = sum(1 for _, _, ok, _ in results if not ok)
        if failed:
            admin_failures = any("ADMIN_REQUIRED" in msg for s, t, ok, msg in results if not ok)
            if admin_failures and self.symlink_manager.is_windows():
                needs_admin = True
                logging.warning(
                    f"Persistence recovery: {failed} symlink(s) failed — retrying with admin in 15s"
                )
            elif admin_failures:
                logging.warning(f"Persistence recovery: {failed} symlink(s) failed — admin required on another platform")
            else:
                logging.warning(f"Persistence recovery: {failed} symlink(s) failed (non-admin errors)")

        if needs_admin:
            if self._admin_retry_pending:
                logging.debug("Persistence recovery: admin retry already scheduled — skipping")
            else:
                self._admin_retry_pending = True
                # Notify via desktop notification
                if self.tray_icon and self.tray_icon.is_available:
                    self.tray_icon.show_message(
                        "Symlink Manager — Admin Required",
                        f"Persistence recreated {recreated} symlink(s), but {failed} require "
                        f"admin privileges. Retrying with elevated rights in 15 seconds.",
                        duration=8000
                    )
                self.statusBar().showMessage(
                    f"Persistence: {recreated} recreated, {failed} need admin — retrying with admin in 15s",
                    8000
                )
                # Collect only the ops that actually failed
                failed_ops = [op for op, (_, _, ok, _) in zip(batch_ops, results) if not ok]
                QTimer.singleShot(15_000, lambda: self._retry_persistence_with_admin(failed_ops))
        else:
            self._admin_retry_pending = False
            if recreated:
                logging.info(f"Persistence recovery: {recreated} symlink(s) recreated via batch")
            if failed:
                logging.warning(f"Persistence recovery: {failed} symlink(s) failed")

        # Track new sub-symlinks from merge
        for ns in merge_tracked:
            self.settings_manager.add_symlink(ns['source'], ns['target'], notes="")
            logging.info(f"Persistence recovery: tracked new symlink from merge: '{ns['target']}' -> '{ns['source']}'")

        if recreated:
            self.statusBar().showMessage(
                f"Persistence: recreated {recreated} symlink(s)",
                5000
            )
            if self.tabs.currentIndex() == 1:  # Manage tab
                self.refresh_symlinks_table()

    def _retry_persistence_with_admin(self, failed_ops: list):
        """Retry failed symlink creations with admin=True after a delay."""
        if not failed_ops:
            return

        logging.info(f"Persistence retry: attempting {len(failed_ops)} symlink(s) with admin privileges")

        # Rebuild batch ops with admin=True and force=True (since target might exist partially)
        retry_ops = []
        for op in failed_ops:
            s, t, d, _, r, _ = op  # (source, target, is_dir, force, relative, admin)
            retry_ops.append((s, t, d, True, r, True))

        overall_success, batch_msg, results = self.symlink_manager.run_batch(retry_ops)
        recreated = sum(1 for _, _, ok, _ in results if ok)
        failed = sum(1 for _, _, ok, _ in results if not ok)

        # Only reset the retry flag if ALL symlinks were created, or if none
        # required admin (allowing a fresh attempt next time)
        if recreated == 0 or not any("ADMIN_REQUIRED" in msg or "UAC" in msg
                                     for _, _, _, msg in results if not ok):
            self._admin_retry_pending = False

        logging.info(f"Persistence retry: {recreated} symlink(s) recreated with admin, {failed} failed")
        if recreated:
            self.statusBar().showMessage(f"Persistence: {recreated} symlink(s) recreated with admin", 5000)
            if self.tabs.currentIndex() == 1:
                self.refresh_symlinks_table()

    @staticmethod
    def get_platform_name() -> str:
        """Get human-readable platform name."""
        if sys.platform == 'win32':
            return 'Windows'
        elif sys.platform == 'darwin':
            return 'macOS'
        else:
            return 'Linux'

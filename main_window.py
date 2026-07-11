"""
Main application window for the Symlink Manager.
"""

import sys
import os
import uuid
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QCheckBox, QFileDialog, QMessageBox,
    QTabWidget, QListWidget, QListWidgetItem, QComboBox, QTableWidget,
    QTableWidgetItem, QDialog, QScrollArea, QFormLayout, QStatusBar, QMenu, QApplication
)
from PyQt6.QtCore import Qt, QSize, QTimer, pyqtSignal, QMimeData
from PyQt6.QtGui import QIcon, QFont, QColor
from PyQt6.QtGui import QClipboard
from PyQt6.QtCore import QThread

from symlink_manager import SymlinkManager
from settings_manager import SettingsManager
from ui_styles import get_theme_stylesheet
from drag_drop_widgets import DragDropLineEdit


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
    
    def __init__(self):
        """Initialize the main window."""
        super().__init__()
        
        self.settings_manager = SettingsManager()
        self.symlink_manager = SymlinkManager()
        
        self.initUI()
        self.load_settings()
        
    def initUI(self):
        """Initialize the user interface."""
        self.setWindowTitle('Symlink Manager')
        self.setMinimumSize(600, 400)
        self.resize(650, 420)
        
        # Set application icon
        icon_path = Path(__file__).parent / 'symlink_manager_icon.png'
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)
        central_widget.setLayout(main_layout)
        
        # Create tab widget for different sections
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("QTabBar::tab { padding: 6px 12px; }")
        main_layout.addWidget(self.tabs)
        
        # Tab 1: Create Symlink
        create_tab = self.create_symlink_tab()
        self.tabs.addTab(create_tab, "Create")
        
        # Tab 2: Manage Symlinks
        manage_tab = self.create_manage_symlinks_tab()
        self.tabs.addTab(manage_tab, "Manage")
        
        # Tab 3: History & Statistics
        history_tab = self.create_history_tab()
        self.tabs.addTab(history_tab, "History")
        
        # Tab 4: Settings
        settings_tab = self.create_settings_tab()
        self.tabs.addTab(settings_tab, "Settings")
        
        # Connect tab change signal to refresh manage tab
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Apply theme
        theme = self.settings_manager.get_setting('theme', 'dark')
        self.setStyleSheet(get_theme_stylesheet(theme))
    
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
        source_browse_btn.setMaximumWidth(80)
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
        target_browse_btn.setMaximumWidth(80)
        target_browse_btn.clicked.connect(self.browse_target)
        target_layout.addWidget(target_browse_btn)
        layout.addLayout(target_layout)
        
        # Options (simplified)
        options_layout = QHBoxLayout()
        
        self.relative_checkbox = QCheckBox("Relative")
        default_relative = self.settings_manager.get_setting('relative_by_default', False)
        self.relative_checkbox.setChecked(default_relative)
        options_layout.addWidget(self.relative_checkbox)
        
        self.force_checkbox = QCheckBox("Force")
        options_layout.addWidget(self.force_checkbox)
        
        if self.symlink_manager.is_windows():
            self.admin_checkbox = QCheckBox("Admin")
            # Automatically enable admin mode on Windows platforms
            self.admin_checkbox.setChecked(True)
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
        self.symlinks_table.horizontalHeader().setStretchLastSection(True)
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
        """Refresh the symlinks table and handle missing symlinks."""
        # Verify all symlinks to get current status
        status = self.settings_manager.verify_symlinks()
        
        # Find and handle missing symlinks
        missing_links = [link for link in status['symlinks'] if link['status'] == 'missing']
        
        if missing_links:
            # Ask user if they want to remove missing symlinks
            missing_paths = '\n'.join([link['target'] for link in missing_links])
            reply = QMessageBox.question(
                self,
                "Missing Symlinks Detected",
                f"The following symlinks are missing:\n\n{missing_paths}\n\nRemove them from the manager?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
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
            # Target
            target_text = link['target'][-50:] if len(link['target']) > 50 else link['target']
            target_item = QTableWidgetItem(target_text)
            target_item.setData(Qt.ItemDataRole.UserRole, link['target'])
            self.symlinks_table.setItem(row, 0, target_item)
            
            # Source
            source_text = link['source'][-40:] if len(link['source']) > 40 else link['source']
            source_item = QTableWidgetItem(source_text)
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
        self.history_table.horizontalHeader().setStretchLastSection(True)
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
        self.most_used_targets_table.horizontalHeader().setStretchLastSection(True)
        
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
        self.most_used_sources_table.horizontalHeader().setStretchLastSection(True)
        
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
        self.most_used_targets_table.horizontalHeader().setStretchLastSection(True)
        
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
        
        # Theme selection
        theme_layout = QHBoxLayout()
        theme_label = QLabel("Theme:")
        theme_label.setStyleSheet("font-weight: bold;")
        theme_layout.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Dark', 'Light'])
        current_theme = self.settings_manager.get_setting('theme', 'dark')
        self.theme_combo.setCurrentText(current_theme.capitalize())
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        self.theme_combo.setMinimumWidth(100)
        self.theme_combo.setMaximumWidth(150)
        theme_layout.addWidget(self.theme_combo)
        theme_layout.addStretch()
        layout.addLayout(theme_layout)
        
        # Information
        info_text = QLabel()
        info_text.setWordWrap(True)
        info_text.setStyleSheet("font-size: 10pt; line-height: 1.5;")
        info_text.setText(
            f"<b>Symlink Manager v1.0.0</b><br>"
            f"<b>Platform:</b> {self.get_platform_name()}<br>"
            f"<b>Python:</b> {sys.version.split()[0]}"
        )
        layout.addWidget(info_text)
        
        layout.addStretch()
        widget.setLayout(layout)
        return widget
    
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
            self.settings_manager.get_setting('relative_by_default', False)
        )
        self.force_checkbox.setChecked(False)
    
    def refresh_history(self):
        """Refresh the history display."""
        # Update creation history table
        creations = self.settings_manager.get_history('creations', 20)
        self.history_table.setRowCount(len(creations))
        
        for row, creation in enumerate(creations):
            time_item = QTableWidgetItem(creation['timestamp'][:19])
            source_item = QTableWidgetItem(creation['source'][-40:] if len(creation['source']) > 40 else creation['source'])
            target_item = QTableWidgetItem(creation['target'][-40:] if len(creation['target']) > 40 else creation['target'])
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
            path = target[-50:] if len(target) > 50 else target
            target_item = QTableWidgetItem(path)
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
        theme = theme_name.lower()
        self.settings_manager.set_setting('theme', theme)
        self.setStyleSheet(get_theme_stylesheet(theme))
    
    def load_settings(self):
        """Load and apply saved settings."""
        geometry = self.settings_manager.get_setting('window_geometry')
        if geometry:
            self.resize(geometry.get('width', 650), geometry.get('height', 420))
    
    def closeEvent(self, event):
        """Save settings when closing."""
        geometry = {
            'width': self.width(),
            'height': self.height()
        }
        self.settings_manager.set_setting('window_geometry', geometry)
        event.accept()
    
    @staticmethod
    def get_platform_name() -> str:
        """Get human-readable platform name."""
        if sys.platform == 'win32':
            return 'Windows'
        elif sys.platform == 'darwin':
            return 'macOS'
        else:
            return 'Linux'

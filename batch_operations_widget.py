"""
Batch operations widget for creating multiple symlinks at once.
Supports drag-and-drop for source items and target directory.
"""

import os
import uuid
from pathlib import Path
from typing import List, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QFileDialog, QMessageBox,
    QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem,
    QGroupBox, QHeaderView, QAbstractItemView, QProgressBar,
    QSplitter, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QColor

from symlink_manager import SymlinkManager
from settings_manager import SettingsManager
from drag_drop_widgets import DragDropLineEdit


class DropTargetListWidget(QListWidget):
    """QListWidget that accepts file/folder drag and drop for batch sources."""

    filesDropped = pyqtSignal(list)

    def __init__(self, parent=None, accept_files=True, accept_dirs=True):
        super().__init__(parent)
        self.accept_files = accept_files
        self.accept_dirs = accept_dirs
        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.setDefaultDropAction(Qt.DropAction.CopyAction)
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.setAlternatingRowColors(True)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            urls = mime_data.urls()
            dropped_paths = []
            # Collect existing paths for duplicate check
            existing_paths = {self.item(i).text() for i in range(self.count())}
            for url in urls:
                file_path = url.toLocalFile()
                path_obj = Path(file_path)
                is_valid = False
                if path_obj.is_file() and self.accept_files:
                    is_valid = True
                elif path_obj.is_dir() and self.accept_dirs:
                    is_valid = True
                if is_valid and file_path not in existing_paths:
                    dropped_paths.append(file_path)
                    existing_paths.add(file_path)
                    item = QListWidgetItem(file_path)
                    item.setToolTip(file_path)
                    self.addItem(item)
            if dropped_paths:
                self.filesDropped.emit(dropped_paths)
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()


class BatchOperationsWidget(QWidget):
    """Widget for batch symlink creation operations."""

    operation_completed = pyqtSignal(str, bool, str)  # source, success, message

    def __init__(self, parent=None):
        super().__init__(parent)
        self.symlink_manager = SymlinkManager()
        self.settings_manager = SettingsManager()
        self.initUI()

    def initUI(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        # ---- Source input row ----
        source_label = QLabel("Source Items (drag & drop files/folders below, or use Browse):")
        source_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(source_label)

        # ---- Target Directory Section ----
        target_label = QLabel("Target Directory (where symlinks will be created):")
        target_label.setStyleSheet("font-weight: bold; margin-top: 4px;")
        layout.addWidget(target_label)

        target_layout = QHBoxLayout()
        self.target_input = DragDropLineEdit(accept_files=False, accept_dirs=True)
        self.target_input.setPlaceholderText("Drag & drop a folder or browse...")
        target_layout.addWidget(self.target_input)

        self.browse_target_btn = QPushButton("Browse...")
        self.browse_target_btn.setMaximumWidth(100)
        self.browse_target_btn.clicked.connect(self.browse_target_directory)
        target_layout.addWidget(self.browse_target_btn)
        layout.addLayout(target_layout)

        # ---- Naming prefix ----
        prefix_layout = QHBoxLayout()
        prefix_label = QLabel("Symlink name prefix (optional):")
        prefix_layout.addWidget(prefix_label)
        self.prefix_input = QLineEdit()
        self.prefix_input.setPlaceholderText("e.g., link-  (results in link-filename)")
        prefix_layout.addWidget(self.prefix_input, stretch=1)
        prefix_layout.addStretch(1)
        layout.addLayout(prefix_layout)

        # ---- Options ----
        options_group = QGroupBox("Batch Options")
        options_layout = QHBoxLayout()
        options_layout.setSpacing(12)

        self.relative_checkbox = QCheckBox("Relative")
        self.relative_checkbox.setChecked(
            self.settings_manager.get_setting('batch_relative', False)
        )
        self.relative_checkbox.toggled.connect(
            lambda c: self.settings_manager.set_setting('batch_relative', c))
        options_layout.addWidget(self.relative_checkbox)

        self.force_checkbox = QCheckBox("Force")
        self.force_checkbox.setChecked(
            self.settings_manager.get_setting('batch_force', False)
        )
        self.force_checkbox.toggled.connect(
            lambda c: self.settings_manager.set_setting('batch_force', c))
        options_layout.addWidget(self.force_checkbox)

        if self.symlink_manager.is_windows():
            self.admin_checkbox = QCheckBox("Admin")
            self.admin_checkbox.setChecked(
                self.settings_manager.get_setting('batch_admin', False)
            )
            self.admin_checkbox.toggled.connect(
                lambda c: self.settings_manager.set_setting('batch_admin', c))
            options_layout.addWidget(self.admin_checkbox)
        else:
            self.admin_checkbox = None

        self.confirm_checkbox = QCheckBox("Confirm each")
        default_confirm = self.settings_manager.get_setting('confirm_before_create', True)
        self.confirm_checkbox.setChecked(default_confirm)
        options_layout.addWidget(self.confirm_checkbox)

        self.skip_errors_checkbox = QCheckBox("Skip errors (continue on failure)")
        self.skip_errors_checkbox.setChecked(
            self.settings_manager.get_setting('batch_skip_errors', False)
        )
        self.skip_errors_checkbox.toggled.connect(
            lambda c: self.settings_manager.set_setting('batch_skip_errors', c))
        options_layout.addWidget(self.skip_errors_checkbox)

        options_layout.addStretch()
        options_group.setLayout(options_layout)
        options_group.setMinimumHeight(50)
        layout.addWidget(options_group)

        # ---- Action buttons ----
        action_layout = QHBoxLayout()

        self.run_batch_btn = QPushButton("Run Batch")
        self.run_batch_btn.setObjectName("successButton")
        self.run_batch_btn.clicked.connect(self.run_batch)
        self.run_batch_btn.setMinimumHeight(36)
        action_layout.addWidget(self.run_batch_btn)

        self.validate_batch_btn = QPushButton("Validate Paths")
        self.validate_batch_btn.clicked.connect(self.validate_batch)
        action_layout.addWidget(self.validate_batch_btn)

        self.clear_results_btn = QPushButton("Clear Results")
        self.clear_results_btn.clicked.connect(self.clear_results)
        action_layout.addWidget(self.clear_results_btn)

        layout.addLayout(action_layout)

        # ---- Progress bar ----
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        layout.addWidget(self.progress_bar)

        # ---- Splitter: source list (top) + results table (bottom) ----
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        self.splitter.setHandleWidth(4)
        # Give the splitter a minimum height so both panes stay visible
        self.splitter.setMinimumHeight(200)

        # Source wrapper: list + action buttons
        source_wrapper = QWidget()
        source_wrapper_layout = QVBoxLayout()
        source_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        source_wrapper_layout.setSpacing(4)

        source_list_label = QLabel("Source Items:")
        source_list_label.setStyleSheet("font-weight: bold;")
        source_wrapper_layout.addWidget(source_list_label)

        self.source_list = DropTargetListWidget(accept_files=True, accept_dirs=True)
        self.source_list.setMinimumHeight(60)
        source_wrapper_layout.addWidget(self.source_list, stretch=1)

        source_list_actions = QHBoxLayout()
        self.browse_sources_btn = QPushButton("Browse...")
        self.browse_sources_btn.setMaximumWidth(100)
        self.browse_sources_btn.clicked.connect(self.browse_sources)
        source_list_actions.addWidget(self.browse_sources_btn)

        self.remove_selected_btn = QPushButton("Remove Selected")
        self.remove_selected_btn.clicked.connect(self.remove_selected_sources)
        source_list_actions.addWidget(self.remove_selected_btn)

        self.clear_sources_btn = QPushButton("Clear All")
        self.clear_sources_btn.clicked.connect(self.clear_sources)
        source_list_actions.addWidget(self.clear_sources_btn)

        source_list_actions.addStretch()
        source_wrapper_layout.addLayout(source_list_actions)

        source_wrapper.setLayout(source_wrapper_layout)
        source_wrapper.setMinimumHeight(100)
        self.splitter.addWidget(source_wrapper)

        # Results wrapper: label + table + progress bar
        results_wrapper = QWidget()
        results_wrapper_layout = QVBoxLayout()
        results_wrapper_layout.setContentsMargins(0, 0, 0, 0)
        results_wrapper_layout.setSpacing(4)

        results_label = QLabel("Batch Results:")
        results_label.setStyleSheet("font-weight: bold;")
        results_wrapper_layout.addWidget(results_label)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(4)
        self.results_table.setHorizontalHeaderLabels(["Source", "Target", "Status", "Message"])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.results_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.results_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setMinimumHeight(60)
        results_wrapper_layout.addWidget(self.results_table, stretch=1)

        results_wrapper.setLayout(results_wrapper_layout)
        results_wrapper.setMinimumHeight(100)
        self.splitter.addWidget(results_wrapper)

        # Give the splitter a reasonable default split (40% sources, 60% results)
        self.splitter.setSizes([300, 400])
        layout.addWidget(self.splitter, stretch=1)

        self.setLayout(layout)

    # ---- Source management ----

    def browse_sources(self):
        """Open file dialog to add multiple sources."""
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select Source Files/Folders")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        last_dir = self.settings_manager.get_setting('last_source_dir', str(Path.home()))
        dialog.setDirectory(last_dir)
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            paths = dialog.selectedFiles()
            for path in paths:
                # Check duplicates
                is_dup = False
                for i in range(self.source_list.count()):
                    if self.source_list.item(i).text() == path:
                        is_dup = True
                        break
                if not is_dup:
                    item = QListWidgetItem(path)
                    item.setToolTip(path)
                    self.source_list.addItem(item)
            if paths:
                self.settings_manager.set_setting('last_source_dir', str(Path(paths[0]).parent))

    def remove_selected_sources(self):
        """Remove selected items from the source list."""
        for item in self.source_list.selectedItems():
            self.source_list.takeItem(self.source_list.row(item))

    def clear_sources(self):
        """Clear all items from the source list."""
        self.source_list.clear()

    def browse_target_directory(self):
        """Open directory dialog to select target directory."""
        dialog = QFileDialog(self)
        dialog.setWindowTitle("Select Target Directory")
        dialog.setFileMode(QFileDialog.FileMode.Directory)
        last_dir = self.settings_manager.get_setting('last_target_dir', str(Path.home()))
        dialog.setDirectory(last_dir)
        if dialog.exec() == QFileDialog.DialogCode.Accepted:
            path = dialog.selectedFiles()[0]
            self.target_input.setText(path)
            self.settings_manager.set_setting('last_target_dir', path)

    def get_sources(self) -> List[str]:
        """Get the list of source paths."""
        sources = []
        for i in range(self.source_list.count()):
            sources.append(self.source_list.item(i).text())
        return sources

    # ---- Validation ----

    def validate_batch(self):
        """Validate all source paths and target directory."""
        sources = self.get_sources()
        target = self.target_input.text().strip()

        if not sources:
            QMessageBox.warning(self, "No Sources", "Please add at least one source item.")
            return

        if not target:
            QMessageBox.warning(self, "No Target", "Please select a target directory.")
            return

        target_path = Path(target)
        if not target_path.exists():
            QMessageBox.warning(self, "Invalid Target", f"Target directory does not exist:\n{target}")
            return
        if not target_path.is_dir():
            QMessageBox.warning(self, "Invalid Target", f"Target path is not a directory:\n{target}")
            return

        # Validate each source
        errors = []
        valid_count = 0
        for source in sources:
            source_path = Path(source)
            if not source_path.exists():
                errors.append(f"Source does not exist: {source}")
            else:
                valid_count += 1

        if errors:
            msg = f"Validation complete: {valid_count} valid, {len(errors)} errors\n\n"
            msg += "\n".join(errors[:10])
            if len(errors) > 10:
                msg += f"\n... and {len(errors) - 10} more"
            QMessageBox.warning(self, "Validation Errors", msg)
        else:
            QMessageBox.information(
                self, "Validation Success",
                f"All {valid_count} source paths are valid.\n"
                f"Target directory: {target}"
            )

    # ---- Batch execution ----

    def run_batch(self):
        """Execute the batch symlink creation."""
        sources = self.get_sources()
        target = self.target_input.text().strip()

        if not sources:
            QMessageBox.warning(self, "No Sources", "Please add at least one source item.")
            return

        if not target:
            QMessageBox.warning(self, "No Target", "Please select a target directory.")
            return

        target_path = Path(target)
        if not target_path.exists():
            QMessageBox.warning(self, "Invalid Target", f"Target directory does not exist:\n{target}")
            return
        if not target_path.is_dir():
            QMessageBox.warning(self, "Invalid Target", f"Target path is not a directory:\n{target}")
            return

        # Gather options
        relative = self.relative_checkbox.isChecked()
        force = self.force_checkbox.isChecked()
        admin = self.admin_checkbox.isChecked() if self.admin_checkbox else False
        confirm_each = self.confirm_checkbox.isChecked()
        skip_errors = self.skip_errors_checkbox.isChecked()
        prefix = self.prefix_input.text().strip()

        # Confirm batch if not confirming each
        if not confirm_each:
            reply = QMessageBox.question(
                self,
                "Confirm Batch Operation",
                f"Create {len(sources)} symlink(s) in:\n{target}\n\n"
                f"Options: Relative={relative}, Force={force}, "
                f"Admin={admin}, Skip Errors={skip_errors}",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        # Clear previous results
        self.results_table.setRowCount(0)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(sources))
        self.run_batch_btn.setEnabled(False)

        # Pre-compute all target paths
        operations = []
        for source in sources:
            source_path = Path(source)
            source_name = source_path.name
            target_name = f"{prefix}{source_name}"
            target_path_full = str(target_path / target_name)
            operations.append((source, target_path_full))

        self._run_batch_direct(operations, relative, force, admin,
                               confirm_each, skip_errors)

    def _run_batch_direct(self, operations, relative, force, admin,
                          confirm_each, skip_errors):
        """Run each symlink creation individually."""
        # ---- Cross-platform batch path (no confirm-each) ----
        # Build all operations upfront and run them as a batch.
        if not confirm_each:
            batch_ops = []
            for source, target in operations:
                source_path = Path(source)
                is_dir = source_path.is_dir()
                batch_ops.append((source, target, is_dir, force, relative, admin))

            overall_success, message, results = self.symlink_manager.run_batch(batch_ops)

            for (source, target), (_, _, op_success, op_msg) in zip(operations, results):
                if op_success:
                    self._add_result(source, target, "Success", op_msg)
                    self.settings_manager.record_creation(source, target, True, op_msg)
                    self.settings_manager.add_to_history(source, 'source')
                    self.settings_manager.add_to_history(target, 'target')
                    self.settings_manager.add_symlink(source, target, notes="")
                else:
                    self._add_result(source, target, "Failed", op_msg)

            total = len(operations)
            success_count = sum(1 for _, _, ok, _ in results if ok)
            fail_count = total - success_count
            self._finish_batch(success_count, fail_count, total)
            return

        # ---- Confirm-each path ----
        success_count = 0
        fail_count = 0
        admin_offered = False

        for idx, (source, target_path_full) in enumerate(operations):
            # Confirm each if enabled
            if confirm_each:
                reply = QMessageBox.question(
                    self,
                    f"Confirm ({idx + 1}/{len(operations)})",
                    f"Create symlink?\n\nSource: {source}\nTarget: {target_path_full}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No |
                    QMessageBox.StandardButton.Cancel
                )
                if reply == QMessageBox.StandardButton.Cancel:
                    self._add_result(source, target_path_full, "Cancelled", "Batch cancelled by user")
                    fail_count += 1
                    break
                elif reply == QMessageBox.StandardButton.No:
                    self._add_result(source, target_path_full, "Skipped", "Skipped by user")
                    fail_count += 1
                    self.progress_bar.setValue(idx + 1)
                    continue

            # Create the symlink
            success, message = self.symlink_manager.create_symlink(
                source, target_path_full, relative, force, admin
            )

            # Handle admin-required response — offer to retry with admin mode
            if not success and message == "ADMIN_REQUIRED" and not admin_offered:
                admin_offered = True
                self.progress_bar.setValue(idx + 1)
                reply = QMessageBox.question(
                    self,
                    "Administrator Privileges Required",
                    "Creating symlinks on Windows requires administrator privileges.\n\n"
                    "Do you want to retry with Admin mode enabled?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    # Re-run the batch with admin=True
                    self.admin_checkbox.setChecked(True)
                    self.run_batch()
                else:
                    self._add_result(source, target_path_full, "Failed",
                                     "Admin privileges required")
                    fail_count += 1
                break

            if success:
                success_count += 1
                self._add_result(source, target_path_full, "Success", message)
                self.settings_manager.record_creation(source, target_path_full, success, message)
                self.settings_manager.add_to_history(source, 'source')
                self.settings_manager.add_to_history(target_path_full, 'target')
                self.settings_manager.add_symlink(source, target_path_full, notes="")
            else:
                fail_count += 1
                self._add_result(source, target_path_full, "Failed", message)
                if not skip_errors:
                    QMessageBox.critical(
                        self, "Error",
                        f"Failed to create symlink:\n{source}\n→ {target_path_full}\n\n{message}\n\nBatch stopped."
                    )
                    self.progress_bar.setValue(idx + 1)
                    break

            self.progress_bar.setValue(idx + 1)

        self._finish_batch(success_count, fail_count, len(operations))

    def _finish_batch(self, success_count, fail_count, total):
        """Show final summary after batch completes."""
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(100)
        self.run_batch_btn.setEnabled(True)

        QMessageBox.information(
            self, "Batch Complete",
            f"Batch symlink creation finished.\n\n"
            f"✓ Success: {success_count}\n"
            f"✗ Failed: {fail_count}\n"
            f"Total processed: {total}"
        )
        self.operation_completed.emit("", success_count > 0,
                                      f"Batch: {success_count} succeeded, {fail_count} failed")

    def _add_result(self, source: str, target: str, status: str, message: str):
        """Add a row to the results table."""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)

        source_item = QTableWidgetItem(source)
        source_item.setToolTip(source)
        self.results_table.setItem(row, 0, source_item)

        target_item = QTableWidgetItem(target)
        target_item.setToolTip(target)
        self.results_table.setItem(row, 1, target_item)

        status_item = QTableWidgetItem(status)
        if status == "Success":
            status_item.setForeground(QColor(166, 227, 161))  # green
        elif status == "Failed":
            status_item.setForeground(QColor(243, 139, 168))  # red
        elif status == "Cancelled":
            status_item.setForeground(QColor(249, 226, 175))  # yellow
        self.results_table.setItem(row, 2, status_item)

        msg_item = QTableWidgetItem(message)
        msg_item.setToolTip(message)
        self.results_table.setItem(row, 3, msg_item)

        # Scroll to the new row
        self.results_table.scrollToBottom()

    def clear_results(self):
        """Clear the results table."""
        self.results_table.setRowCount(0)
        self.progress_bar.setVisible(False)
        self.progress_bar.setValue(0)
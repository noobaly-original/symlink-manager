"""
Modern UI styling for the Symlink application.
Provides stylesheets for dark and light themes with transparency elements.
"""

DARK_THEME = """
QMainWindow {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 8px;
    selection-background-color: #585b70;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #89b4fa;
    background-color: #2a2a3a;
}

QPushButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 11pt;
}

QPushButton:hover {
    background-color: #a4c7f5;
}

QPushButton:pressed {
    background-color: #6fa1e0;
}

QPushButton#warningButton {
    background-color: #f38ba8;
}

QPushButton#warningButton:hover {
    background-color: #f5a3b8;
}

QPushButton#successButton {
    background-color: #a6e3a1;
}

QPushButton#successButton:hover {
    background-color: #b5ebad;
}

QGroupBox {
    color: #cdd6f4;
    border: 2px solid #45475a;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
}

QLabel {
    color: #cdd6f4;
}

QCheckBox, QRadioButton {
    color: #cdd6f4;
    spacing: 5px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
}

QCheckBox::indicator:unchecked {
    background-color: #313244;
    border: 2px solid #45475a;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border: 2px solid #89b4fa;
    border-radius: 3px;
}

QCheckBox::indicator:hover {
    border: 2px solid #89b4fa;
}

QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 6px 8px;
    min-height: 24px;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
    background-color: #313244;
}

QComboBox::down-arrow {
    image: none;
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    selection-background-color: #585b70;
    outline: none;
    padding: 4px;
    min-height: 24px;
}

QListWidget, QTableWidget {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 5px;
    gridline-color: #45475a;
}

QListWidget::item:hover, QTableWidget::item:hover {
    background-color: #45475a;
}

QListWidget::item:selected, QTableWidget::item:selected {
    background-color: #585b70;
}

QTabWidget::pane {
    border: 1px solid #45475a;
}

QTabBar::tab {
    background-color: #313244;
    color: #cdd6f4;
    padding: 8px 20px;
    border: 1px solid #45475a;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #45475a;
    border-bottom: 2px solid #89b4fa;
}

QTabBar::tab:hover {
    background-color: #3a3d4a;
}

QScrollBar:vertical {
    background-color: #313244;
    width: 12px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QScrollBar:horizontal {
    background-color: #313244;
    height: 12px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #45475a;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #585b70;
}

QScrollBar::add-line, QScrollBar::sub-line {
    border: none;
    background: none;
}

QMessageBox {
    background-color: #1e1e2e;
}

QMessageBox QLabel {
    color: #cdd6f4;
}

QDialog {
    background-color: #1e1e2e;
}

QStatusBar {
    background-color: #313244;
    color: #cdd6f4;
    border-top: 1px solid #45475a;
}

QMenuBar {
    background-color: #313244;
    color: #cdd6f4;
    border-bottom: 1px solid #45475a;
}

QMenuBar::item:selected {
    background-color: #45475a;
}

QMenu {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
}

QMenu::item:selected {
    background-color: #45475a;
}

QSpinBox, QDoubleSpinBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 5px;
    padding: 5px;
}
"""

LIGHT_THEME = """
QMainWindow {
    background-color: #f5f5f5;
    color: #333333;
}

QWidget {
    background-color: #f5f5f5;
    color: #333333;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #d0d0d0;
    border-radius: 5px;
    padding: 8px;
    selection-background-color: #e0e0e0;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #4a90e2;
    background-color: #ffffff;
}

QPushButton {
    background-color: #4a90e2;
    color: #ffffff;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 11pt;
}

QPushButton:hover {
    background-color: #5fa3ed;
}

QPushButton:pressed {
    background-color: #3a7fd4;
}

QPushButton#warningButton {
    background-color: #e74c3c;
}

QPushButton#warningButton:hover {
    background-color: #ec6452;
}

QPushButton#successButton {
    background-color: #27ae60;
}

QPushButton#successButton:hover {
    background-color: #31bb6e;
}

QGroupBox {
    color: #333333;
    border: 2px solid #d0d0d0;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
}

QLabel {
    color: #333333;
}

QCheckBox, QRadioButton {
    color: #333333;
    spacing: 5px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
}

QCheckBox::indicator:unchecked {
    background-color: #ffffff;
    border: 2px solid #d0d0d0;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    background-color: #4a90e2;
    border: 2px solid #4a90e2;
    border-radius: 3px;
}

QCheckBox::indicator:hover {
    border: 2px solid #4a90e2;
}

QComboBox {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #d0d0d0;
    border-radius: 5px;
    padding: 6px 8px;
    min-height: 24px;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
    background-color: #ffffff;
}

QComboBox::down-arrow {
    image: none;
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #d0d0d0;
    selection-background-color: #d0d0d0;
    outline: none;
    padding: 4px;
    min-height: 24px;
}

QListWidget, QTableWidget {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #d0d0d0;
    border-radius: 5px;
    gridline-color: #e0e0e0;
}

QListWidget::item:hover, QTableWidget::item:hover {
    background-color: #f0f0f0;
}

QListWidget::item:selected, QTableWidget::item:selected {
    background-color: #e0e0e0;
}

QTabWidget::pane {
    border: 1px solid #d0d0d0;
}

QTabBar::tab {
    background-color: #e8e8e8;
    color: #333333;
    padding: 8px 20px;
    border: 1px solid #d0d0d0;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    border-bottom: 2px solid #4a90e2;
}

QTabBar::tab:hover {
    background-color: #f0f0f0;
}

QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 12px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #d0d0d0;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #a0a0a0;
}

QScrollBar:horizontal {
    background-color: #f5f5f5;
    height: 12px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #d0d0d0;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #a0a0a0;
}

QScrollBar::add-line, QScrollBar::sub-line {
    border: none;
    background: none;
}

QMessageBox {
    background-color: #f5f5f5;
}

QMessageBox QLabel {
    color: #333333;
}

QDialog {
    background-color: #f5f5f5;
}

QStatusBar {
    background-color: #e8e8e8;
    color: #333333;
    border-top: 1px solid #d0d0d0;
}

QMenuBar {
    background-color: #e8e8e8;
    color: #333333;
    border-bottom: 1px solid #d0d0d0;
}

QMenuBar::item:selected {
    background-color: #d0d0d0;
}

QMenu {
    background-color: #e8e8e8;
    color: #333333;
    border: 1px solid #d0d0d0;
}

QMenu::item:selected {
    background-color: #d0d0d0;
}

QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #d0d0d0;
    border-radius: 5px;
    padding: 5px;
}
"""

def get_theme_stylesheet(theme: str = 'dark') -> str:
    """
    Get the stylesheet for a theme.
    
    Args:
        theme: 'dark' or 'light'
        
    Returns:
        CSS stylesheet string
    """
    return DARK_THEME if theme.lower() == 'dark' else LIGHT_THEME

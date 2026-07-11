"""
Modern UI styling for the Symlink application.
Provides stylesheets for dark and light themes with transparency elements.
"""

DARK_THEME = """
QMainWindow {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #45475a;
}

#framelessWindow {
    background-color: #1e1e2e;
}

#titleBar {
    background-color: #1e1e2e;
}

#titleLabel {
    color: #cdd6f4;
}

#minimizeButton, #maximizeButton {
    background-color: transparent;
    color: #cdd6f4;
    border: none;
    border-radius: 0px;
    font-size: 12pt;
    font-weight: normal;
    padding: 0px;
}

#minimizeButton:hover, #maximizeButton:hover {
    background-color: #45475a;
}

#closeButton {
    background-color: transparent;
    color: #cdd6f4;
    border: none;
    border-radius: 0px;
    font-size: 10pt;
    font-weight: normal;
    padding: 0px;
}

#closeButton:hover {
    background-color: #e64553;
    color: #ffffff;
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
    border: 1px solid #d0d0d0;
}

#framelessWindow {
    background-color: #f5f5f5;
}

#titleBar {
    background-color: #f5f5f5;
}

#titleLabel {
    color: #333333;
}

#minimizeButton, #maximizeButton {
    background-color: transparent;
    color: #333333;
    border: none;
    border-radius: 0px;
    font-size: 12pt;
    font-weight: normal;
    padding: 0px;
}

#minimizeButton:hover, #maximizeButton:hover {
    background-color: #d0d0d0;
}

#closeButton {
    background-color: transparent;
    color: #333333;
    border: none;
    border-radius: 0px;
    font-size: 10pt;
    font-weight: normal;
    padding: 0px;
}

#closeButton:hover {
    background-color: #e64553;
    color: #ffffff;
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

MONOKAI_THEME = """
QMainWindow {
    background-color: #272822;
    color: #f8f8f2;
    border: 1px solid #49483e;
}

#framelessWindow {
    background-color: #272822;
}

#titleBar {
    background-color: #272822;
}

#titleLabel {
    color: #f8f8f2;
}

#minimizeButton, #maximizeButton {
    background-color: transparent;
    color: #f8f8f2;
    border: none;
    border-radius: 0px;
    font-size: 12pt;
    font-weight: normal;
    padding: 0px;
}

#minimizeButton:hover, #maximizeButton:hover {
    background-color: #49483e;
}

#closeButton {
    background-color: transparent;
    color: #f8f8f2;
    border: none;
    border-radius: 0px;
    font-size: 10pt;
    font-weight: normal;
    padding: 0px;
}

#closeButton:hover {
    background-color: #f92672;
    color: #ffffff;
}

QWidget {
    background-color: #272822;
    color: #f8f8f2;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #3e3d32;
    color: #f8f8f2;
    border: 1px solid #49483e;
    border-radius: 5px;
    padding: 8px;
    selection-background-color: #49483e;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #66d9ef;
    background-color: #2d2d26;
}

QPushButton {
    background-color: #a6e22e;
    color: #272822;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 11pt;
}

QPushButton:hover {
    background-color: #b8f340;
}

QPushButton:pressed {
    background-color: #8fd41e;
}

QPushButton#warningButton {
    background-color: #f92672;
}

QPushButton#warningButton:hover {
    background-color: #fa4a87;
}

QPushButton#successButton {
    background-color: #a6e22e;
}

QPushButton#successButton:hover {
    background-color: #b8f340;
}

QGroupBox {
    color: #f8f8f2;
    border: 2px solid #49483e;
    border-radius: 8px;
    margin-top: 10px;
    padding-top: 10px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 10px;
    padding: 0 5px;
    color: #e6db74;
}

QLabel {
    color: #f8f8f2;
}

QCheckBox, QRadioButton {
    color: #f8f8f2;
    spacing: 5px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
}

QCheckBox::indicator:unchecked {
    background-color: #3e3d32;
    border: 2px solid #49483e;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    background-color: #66d9ef;
    border: 2px solid #66d9ef;
    border-radius: 3px;
}

QCheckBox::indicator:hover {
    border: 2px solid #66d9ef;
}

QComboBox {
    background-color: #3e3d32;
    color: #f8f8f2;
    border: 1px solid #49483e;
    border-radius: 5px;
    padding: 6px 8px;
    min-height: 24px;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
    background-color: #3e3d32;
}

QComboBox::down-arrow {
    image: none;
    width: 12px;
    height: 12px;
}

QComboBox QAbstractItemView {
    background-color: #3e3d32;
    color: #f8f8f2;
    border: 1px solid #49483e;
    selection-background-color: #49483e;
    outline: none;
    padding: 4px;
    min-height: 24px;
}

QListWidget, QTableWidget {
    background-color: #3e3d32;
    color: #f8f8f2;
    border: 1px solid #49483e;
    border-radius: 5px;
    gridline-color: #49483e;
}

QListWidget::item:hover, QTableWidget::item:hover {
    background-color: #49483e;
}

QListWidget::item:selected, QTableWidget::item:selected {
    background-color: #75715e;
}

QTabWidget::pane {
    border: 1px solid #49483e;
}

QTabBar::tab {
    background-color: #3e3d32;
    color: #f8f8f2;
    padding: 8px 20px;
    border: 1px solid #49483e;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #49483e;
    border-bottom: 2px solid #fd971f;
}

QTabBar::tab:hover {
    background-color: #4a493a;
}

QScrollBar:vertical {
    background-color: #3e3d32;
    width: 12px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #49483e;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #75715e;
}

QScrollBar:horizontal {
    background-color: #3e3d32;
    height: 12px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #49483e;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #75715e;
}

QScrollBar::add-line, QScrollBar::sub-line {
    border: none;
    background: none;
}

QMessageBox {
    background-color: #272822;
}

QMessageBox QLabel {
    color: #f8f8f2;
}

QDialog {
    background-color: #272822;
}

QStatusBar {
    background-color: #3e3d32;
    color: #f8f8f2;
    border-top: 1px solid #49483e;
}

QMenuBar {
    background-color: #3e3d32;
    color: #f8f8f2;
    border-bottom: 1px solid #49483e;
}

QMenuBar::item:selected {
    background-color: #49483e;
}

QMenu {
    background-color: #3e3d32;
    color: #f8f8f2;
    border: 1px solid #49483e;
}

QMenu::item:selected {
    background-color: #49483e;
}

QSpinBox, QDoubleSpinBox {
    background-color: #3e3d32;
    color: #f8f8f2;
    border: 1px solid #49483e;
    border-radius: 5px;
    padding: 5px;
}
"""

PASTEL_PINK_THEME = """
QMainWindow {
    background-color: #fff0f5;
    color: #5c4a5a;
    border: 1px solid #f5c6d0;
}

#framelessWindow {
    background-color: #fff0f5;
}

#titleBar {
    background-color: #fff0f5;
}

#titleLabel {
    color: #5c4a5a;
}

#minimizeButton, #maximizeButton {
    background-color: transparent;
    color: #5c4a5a;
    border: none;
    border-radius: 0px;
    font-size: 12pt;
    font-weight: normal;
    padding: 0px;
}

#minimizeButton:hover, #maximizeButton:hover {
    background-color: #f5c6d0;
}

#closeButton {
    background-color: transparent;
    color: #5c4a5a;
    border: none;
    border-radius: 0px;
    font-size: 10pt;
    font-weight: normal;
    padding: 0px;
}

#closeButton:hover {
    background-color: #e64553;
    color: #ffffff;
}

QWidget {
    background-color: #fff0f5;
    color: #5c4a5a;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #5c4a5a;
    border: 1px solid #f5c6d0;
    border-radius: 5px;
    padding: 8px;
    selection-background-color: #fce4ec;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #f4a0b0;
    background-color: #fffafc;
}

QPushButton {
    background-color: #f4a0b0;
    color: #ffffff;
    border: none;
    border-radius: 5px;
    padding: 8px 16px;
    font-weight: bold;
    font-size: 11pt;
}

QPushButton:hover {
    background-color: #f7b8c4;
}

QPushButton:pressed {
    background-color: #e88a9c;
}

QPushButton#warningButton {
    background-color: #e57373;
}

QPushButton#warningButton:hover {
    background-color: #ef9a9a;
}

QPushButton#successButton {
    background-color: #a8d8a8;
}

QPushButton#successButton:hover {
    background-color: #bce3bc;
}

QGroupBox {
    color: #5c4a5a;
    border: 2px solid #f5c6d0;
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
    color: #5c4a5a;
}

QCheckBox, QRadioButton {
    color: #5c4a5a;
    spacing: 5px;
}

QCheckBox::indicator, QRadioButton::indicator {
    width: 16px;
    height: 16px;
}

QCheckBox::indicator:unchecked {
    background-color: #ffffff;
    border: 2px solid #f5c6d0;
    border-radius: 3px;
}

QCheckBox::indicator:checked {
    background-color: #f4a0b0;
    border: 2px solid #f4a0b0;
    border-radius: 3px;
}

QCheckBox::indicator:hover {
    border: 2px solid #f4a0b0;
}

QComboBox {
    background-color: #ffffff;
    color: #5c4a5a;
    border: 1px solid #f5c6d0;
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
    color: #5c4a5a;
    border: 1px solid #f5c6d0;
    selection-background-color: #fce4ec;
    outline: none;
    padding: 4px;
    min-height: 24px;
}

QListWidget, QTableWidget {
    background-color: #ffffff;
    color: #5c4a5a;
    border: 1px solid #f5c6d0;
    border-radius: 5px;
    gridline-color: #fce4ec;
}

QListWidget::item:hover, QTableWidget::item:hover {
    background-color: #fce4ec;
}

QListWidget::item:selected, QTableWidget::item:selected {
    background-color: #f8d0da;
}

QTabWidget::pane {
    border: 1px solid #f5c6d0;
}

QTabBar::tab {
    background-color: #fce4ec;
    color: #5c4a5a;
    padding: 8px 20px;
    border: 1px solid #f5c6d0;
    border-bottom: none;
}

QTabBar::tab:selected {
    background-color: #ffffff;
    border-bottom: 2px solid #f4a0b0;
}

QTabBar::tab:hover {
    background-color: #fdf0f3;
}

QScrollBar:vertical {
    background-color: #fff0f5;
    width: 12px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #f5c6d0;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #f0a8b8;
}

QScrollBar:horizontal {
    background-color: #fff0f5;
    height: 12px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #f5c6d0;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #f0a8b8;
}

QScrollBar::add-line, QScrollBar::sub-line {
    border: none;
    background: none;
}

QMessageBox {
    background-color: #fff0f5;
}

QMessageBox QLabel {
    color: #5c4a5a;
}

QDialog {
    background-color: #fff0f5;
}

QStatusBar {
    background-color: #fce4ec;
    color: #5c4a5a;
    border-top: 1px solid #f5c6d0;
}

QMenuBar {
    background-color: #fce4ec;
    color: #5c4a5a;
    border-bottom: 1px solid #f5c6d0;
}

QMenuBar::item:selected {
    background-color: #f8d0da;
}

QMenu {
    background-color: #fce4ec;
    color: #5c4a5a;
    border: 1px solid #f5c6d0;
}

QMenu::item:selected {
    background-color: #f8d0da;
}

QSpinBox, QDoubleSpinBox {
    background-color: #ffffff;
    color: #5c4a5a;
    border: 1px solid #f5c6d0;
    border-radius: 5px;
    padding: 5px;
}
"""


def get_theme_stylesheet(theme: str = 'dark') -> str:
    """
    Get the stylesheet for a theme.
    
    Args:
        theme: 'dark', 'light', 'monokai', or 'pastel_pink'
        
    Returns:
        CSS stylesheet string
    """
    theme_lower = theme.lower()
    if theme_lower == 'dark':
        return DARK_THEME
    elif theme_lower == 'monokai':
        return MONOKAI_THEME
    elif theme_lower == 'pastel_pink':
        return PASTEL_PINK_THEME
    else:
        return LIGHT_THEME
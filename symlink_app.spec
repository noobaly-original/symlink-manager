# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file for Symlink Manager

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('symlink_manager_icon.png', '.')],
    hiddenimports=['PyQt6.QtCore', 'PyQt6.QtGui', 'PyQt6.QtWidgets'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SymlinkManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='symlink_manager_icon.png',
)

# macOS specific
app = BUNDLE(
    exe,
    name='SymlinkManager.app',
    icon='symlink_manager_icon.png',
    bundle_identifier='com.symlink.manager',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
    },
)

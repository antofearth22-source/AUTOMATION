# -*- mode: python ; coding: utf-8 -*-

from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=collect_data_files('src'),
    hiddenimports=[
        'tzdata',
        'certifi',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtSvg',
        'src.utils.paths',
        'src.utils.clock',
        'src.utils.logger',
        'src.security.credential_store',
        'keyring.backends.Windows',
        'win32cred',
        'win32api',
        'win32ctypes.pywin32_bootstrap',
        'playwright.driver.package'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    # Add this line to handle issue with multiprocessing
    win_no_prefer_redirects=False,
    win_private_assemblies=False
)

# Include data files from the 'assets' and 'ui' directories
a.datas += [
    ('assets/icons/*.svg', 'assets/icons'),
    ('ui/theme.qss', 'ui')
]


pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='IrctcPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False, # Set to False for GUI applications
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/app.ico' # Assuming an app icon exists
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='irctc_pro_final_build'
)

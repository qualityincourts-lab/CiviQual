# -*- mode: python ; coding: utf-8 -*-
"""
CiviQual Stats v2.0.0 - PyInstaller Spec File

Build command:
    pyinstaller CiviQualStats.spec

Output:
    dist/CiviQualStats/CiviQualStats.exe (plus dependencies)
"""

import os
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# Collect all hidden imports for the application
hidden_imports = [
    # PySide6 modules
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtPrintSupport',
    'PySide6.QtSvg',
    'PySide6.QtSvgWidgets',
    
    # Scientific computing
    'numpy',
    'pandas',
    'scipy',
    'scipy.stats',
    'scipy.optimize',
    'scipy.special',
    'statsmodels',
    'statsmodels.api',
    'statsmodels.stats',
    'statsmodels.stats.multicomp',
    'statsmodels.formula.api',
    
    # Visualization
    'matplotlib',
    'matplotlib.pyplot',
    'matplotlib.backends.backend_qtagg',
    'matplotlib.figure',
    
    # Cryptography for license validation
    'cryptography',
    'cryptography.hazmat.primitives',
    'cryptography.hazmat.primitives.asymmetric',
    'cryptography.hazmat.primitives.serialization',
    'cryptography.hazmat.backends',
    
    # Standard library
    'json',
    'csv',
    'datetime',
    'pathlib',
    'webbrowser',
]

# Analysis
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        # Include sample data files
        ('samples/*.csv', 'samples'),
        ('samples/*.md', 'samples'),
        ('samples/pro/*.csv', 'samples/pro'),
        # Include documentation
        ('docs/user_guide.html', 'docs'),
        # Include version info
        ('version.py', '.'),
        ('CHANGELOG.md', '.'),
        ('README.md', '.'),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Exclude unnecessary modules to reduce size
        'tkinter',
        'unittest',
        'email',
        'html',
        'http',
        'xml',
        'pydoc',
        'doctest',
        'argparse',
        'difflib',
        'inspect',
        'calendar',
        'pdb',
        'profile',
        'pstats',
        'test',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=block_cipher,
)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CiviQualStats',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windowed application (no console)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='civiqual_icon.ico',
    version='version_info.txt',  # Optional: Windows version info
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CiviQualStats',
)

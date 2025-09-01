"""
PyInstaller spec file for bundling PDF Accessibility Tool with veraPDF
"""
# -*- mode: python ; coding: utf-8 -*-

import os
import platform

block_cipher = None

# Platform-specific veraPDF paths
if platform.system() == "Darwin":  # macOS
    verapdf_path = "/Applications/veraPDF/verapdf"
    verapdf_data = [(verapdf_path, "verapdf")] if os.path.exists(verapdf_path) else []
elif platform.system() == "Windows":
    verapdf_path = "C:/Program Files/veraPDF/veraPDF.exe"
    verapdf_data = [(verapdf_path, "verapdf")] if os.path.exists(verapdf_path) else []
else:  # Linux
    verapdf_path = "/usr/local/bin/veraPDF"
    verapdf_data = [(verapdf_path, "verapdf")] if os.path.exists(verapdf_path) else []

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=verapdf_data,
    datas=[
        ('samples', 'samples'),
        ('docs', 'docs'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'fitz',
        'pikepdf'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='PDFAccessibilityTool',
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
    icon='icon.ico' if platform.system() == "Windows" else 'icon.icns'
)

# macOS App Bundle
if platform.system() == "Darwin":
    app = BUNDLE(
        exe,
        name='PDF Accessibility Tool.app',
        icon='icon.icns',
        bundle_identifier='com.yourcompany.pdfaccessibility',
        info_plist={
            'CFBundleDisplayName': 'PDF Accessibility Tool',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        }
    )

# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path

# Get the project root directory
project_root = Path.cwd()

# Add src directory to path for imports
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

block_cipher = None

a = Analysis(
    ['scripts/book_downloader.py'],
    pathex=[str(project_root), str(src_path)],
    binaries=[],
    datas=[
        ('README.md', '.'),
        ('LICENSE', '.'),
        ('docs/USAGE_GUIDE.md', '.'),
    ],
    hiddenimports=[
        'book_downloader',
        'book_downloader.cli',
        'book_downloader.core',
        'book_downloader.scraper',
        'book_downloader.epub_generator',
        'book_downloader.metadata',
        'book_downloader.utils',
        'book_downloader.config',
        'lxml',
        'lxml.etree',
        'lxml.html',
        'pydoll',
        'aiohttp',
        'aiofiles',
        'asyncio',
        'pathlib',
        'json',
        'zipfile',
        'tempfile',
        'shutil',
        'argparse',
        'typing',
        'dataclasses',
        'enum',
        'datetime',
        'time',
        'os',
        'sys',
        're',
        'urllib',
        'urllib.parse',
        'urllib.request',
        'html',
        'html.parser',
        'xml',
        'xml.etree',
        'xml.etree.ElementTree',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'torch',
        'tensorflow',
        'keras',
        'sklearn',
        'jupyter',
        'notebook',
        'IPython',
    ],
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
    name='book-downloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version=None,
)

# macOS specific: Create .app bundle
app = BUNDLE(
    exe,
    name='book-downloader.app',
    icon=None,
    bundle_identifier='com.bookdownloader.app',
    info_plist={
        'CFBundleName': 'Book Downloader',
        'CFBundleDisplayName': 'Book Downloader',
        'CFBundleIdentifier': 'com.bookdownloader.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleExecutable': 'book-downloader',
        'CFBundlePackageType': 'APPL',
        'NSHighResolutionCapable': True,
    },
)
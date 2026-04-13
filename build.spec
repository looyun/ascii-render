# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller spec for optimized binary builds."""

import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE
from pathlib import Path

ROOT = Path(SPECPATH)
ENTRY = str(ROOT / "run_cli.py")
NAME = os.environ.get("PYINSTALLER_NAME", "ascii-render")

a = Analysis(
    [ENTRY],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Heavy third-party libs not used at runtime
        "numpy",
        "cv2",
        # GUI toolkits
        "tkinter",
        "PyQt5",
        "PyQt6",
        "PySide2",
        "PySide6",
        "wx",
        # Testing / debugging / dev tools
        "unittest",
        "pydoc",
        "doctest",
        "bdb",
        "pdb",
        "py_compile",
        "symtable",
        "tabnanny",
        "tracemalloc",
        # Networking / web protocols not needed by urllib internals
        "xmlrpc",
        "html",
        # Other stdlib modules not used by this CLI app
        "idlelib",
        "lib2to3",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name=NAME,
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
    onefile=True,
)

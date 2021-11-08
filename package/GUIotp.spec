# -*- mode: python ; coding: utf-8 -*-

import os
from package.build_win_verinfo import fill_version_info
from gui_otp import VERSION

FILE_NAME = "GUIotp"
FILE_DESCRIPTION = "GUIotp application executable"
COMMENTS = "GUIotp : GUI 2FA TOTP desktop client"


pkgs_remove = [
    "sqlite3",
    "_sqlite3",
    "libopenblas",
    "libdgamln",
]

dataset = Analysis(
    ["../gui_otp.py"],
    binaries=[],
    datas=[("../res/guiotp-icon.png", "res/")],
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "curses",
        "pywin.debugger",
        "pywin.debugger.dbgcon",
        "pywin.dialogs",
        "libopenblas",
        "libdgamln",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

for pkg in pkgs_remove:
    dataset.binaries = [x for x in dataset.binaries if not x[0].startswith(pkg)]

pyz = PYZ(dataset.pure, dataset.zipped_data, cipher=None)

file_version = VERSION

fill_version_info(FILE_NAME, file_version, FILE_DESCRIPTION, COMMENTS)

exe = EXE(
    pyz,
    dataset.scripts,
    dataset.binaries,
    dataset.zipfiles,
    dataset.datas,
    [],
    name=FILE_NAME,
    debug=False,
    bootloader_ignore_signals=False,
    icon="../res/guiotp.ico",
    strip=False,
    upx=True,
    upx_exclude=[],
    console=False,
    version="version_info",
)

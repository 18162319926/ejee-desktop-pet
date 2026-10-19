# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ejee_pet.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/base.png', '.'), ('assets/base_body.png', '.'), ('assets/leaf.png', '.'), ('assets/leaf_dry.png', '.'), ('assets/eye_l.png', '.'), ('assets/eye_r.png', '.'), ('assets/mouth.png', '.'), ('assets/coords.json', '.'), ('assets/ejee_icon.png', '.'), ('assets/lines.json', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='EJEE',
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
    icon=['assets/ejee.ico'],
)

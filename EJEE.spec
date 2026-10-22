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
    # P3-14：应用只用到 QtWidgets/QtGui/QtCore，其余 PySide6 模块全部排除
    # （桌面宠不用网络/QML/SVG/PDF/多媒体/打印……）。每加一个排除项后
    # 必须跑 tools/check_preview.py --run + 打包冒烟，启动崩溃就回退该项。
    excludes=['PySide6.QtNetwork', 'PySide6.QtQml', 'PySide6.QtQuick',
              'PySide6.QtQuickWidgets', 'PySide6.QtQuickControls2',
              'PySide6.QtOpenGL', 'PySide6.QtOpenGLWidgets',
              'PySide6.QtSvg', 'PySide6.QtSvgWidgets',
              'PySide6.QtPdf', 'PySide6.QtPdfWidgets',
              'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets',
              'PySide6.QtSql', 'PySide6.QtTest', 'PySide6.QtXml',
              'PySide6.QtDesigner', 'PySide6.QtHelp', 'PySide6.QtUiTools',
              'PySide6.Qt3DCore', 'PySide6.QtCharts',
              'PySide6.QtDataVisualization', 'PySide6.QtRemoteObjects',
              'PySide6.QtSensors', 'PySide6.QtSerialPort',
              'PySide6.QtPositioning', 'PySide6.QtLocation',
              'PySide6.QtBluetooth', 'PySide6.QtNfc',
              'PySide6.QtWebSockets', 'PySide6.QtWebChannel',
              'PySide6.QtTextToSpeech', 'PySide6.QtScxml',
              'PySide6.QtStateMachine', 'PySide6.QtVirtualKeyboard',
              'PySide6.QtQuick3D', 'PySide6.QtDBus',
              'PySide6.QtPrintSupport',
              # numpy：PIL 钩子连带收集，本体用不到（只做 PIL 遮罩雕刻，
              # 无 fromarray/转 numpy 数组的操作），打包能省约 10MB
              'numpy'],
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

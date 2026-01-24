# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller 打包配置
不压缩，完整打包
"""

block_cipher = None

a = Analysis(
    ['desktop/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('desktop/resources', 'desktop/resources'),
        ('desktop/i18n', 'desktop/i18n'),
        ('data', 'data'),
        ('core', 'core'),
        ('data/standard_colors.json', 'data'),
        ('data/custom_colors.json', 'data'),
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'numpy',
        'PIL',
        'PIL._imaging',
        'skimage',
        'skimage.filters',
        'skimage.restoration',
        'sklearn',
        'sklearn.cluster',
        'sklearn.neighbors',
        'reportlab',
        'reportlab.pdfgen',
        'reportlab.lib',
        'requests',
        'packaging',
        'packaging.version',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'IPython',
        'jupyter',
        'scipy.spatial.transform.rotation',
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
    name='拼豆图案生成系统',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,  # 不使用UPX压缩
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='desktop/resources/icons/app_icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,  # 不压缩
    upx_exclude=[],
    name='拼豆图案生成系统',
)

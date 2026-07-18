# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('conversor/assets', 'conversor/assets')],
    hiddenimports=[
        'conversor.converters.documents',
        'conversor.converters.images',
        'conversor.converters.audio',
        'conversor.converters.video',
        'conversor.ui.app',
        'conversor.ui.file_panel',
        'conversor.ui.options_panel',
        'conversor.ui.progress_panel',
        'conversor.ui.themes',
        'conversor.core.engine',
        'conversor.core.registry',
        'conversor.core.validators',
        'conversor.utils.ffmpeg_check',
        'conversor.utils.file_utils',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ConversorDeArchivos',
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
    icon='conversor/assets/iconochoro.ico',
)

block_cipher = None

import realesrgan_ncnn_py
import os
models_path = os.path.join(os.path.dirname(realesrgan_ncnn_py.__file__), 'models')

model_files = []
for model_file in os.listdir(models_path):
    if model_file.endswith('.param') or model_file.endswith('.bin'):
        source_path = os.path.join(models_path, model_file)
        dest_path = os.path.join('realesrgan_ncnn_py', 'models')
        model_files.append((source_path, dest_path))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=model_files,
    hiddenimports=['PIL', 'PIL._imagingtk', 'PIL._tkinter_finder'],
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
    name='Zenith',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
)
# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None
datas = [("mca\\resources\\icons\\archeology.png", "mca\\resources\\icons"),
            ("mca\\resources\\icons\\bin.png", "mca\\resources\\icons"),
            ("mca\\resources\\icons\\copy.png", "mca\\resources\\icons"),
            ("mca\\resources\\icons\\cut-with-scissors.png", "mca\\resources\\icons"),
            ("mca\\resources\\icons\\increase.png", "mca\\resourceincreases\\icons"),
            ("mca\\resources\\icons\\magnifying-glass-minus.png", "mca\\resources\\icons"),
            ("mca\\resources\\icons\\magnifying-glass-plus.png", "mca\\resources\\icons\\icons"),
            ("mca\\resources\\icons\\paste.png", "mca\\resources\\icons"),
            ("mca\\resources\\connect_blocks.gif", "mca\\resources"),
            ("mca\\resources\\create_block.gif", "mca\\resources"),
            ("mca\\resources\\edit_parameters.gif", "mca\\resources"),
            ("mca\\resources\\plot_signal.gif", "mca\\resources"),
            ("mca\\resources\\emt_logo.png", "mca\\resources"),
            ("mca\\resources\\emt_logo_cropped.png", "mca\\resources"),
            ("mca\\locales\\de\\LC_MESSAGES\\messages.mo", "mca\\locales\\de\\LC_MESSAGES\\"),
            ("mca\\version.txt", "mca")]

a = Analysis(["mca\\main.py"],
             pathex=[],
             binaries=[],
             datas=datas,
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='mca',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=True,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='mca.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=False,
               upx_exclude=[],
               name='mca')

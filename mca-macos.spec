# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None
datas = [('mca/resources/gifs/*', 'mca/resources/gifs/'),
         ('mca/resources/icons/*', 'mca/resources/icons/'),
            ('mca/locales/de/LC_MESSAGES/messages.mo', 'mca/locales/de/LC_MESSAGES/'),
            ('mca/version.txt', 'mca')]


a = Analysis(['mca/main.py'],
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
          name='mca-exec',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=False,
          console=False,
          argv_emulation=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None)
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas, 
               strip=False,
               upx=True,
               upx_exclude=[],
               name='mca')
app = BUNDLE(coll,
             name='mca.app',
             icon='mca.icns',
             bundle_identifier=None)

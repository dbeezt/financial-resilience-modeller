# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Application/GUI.py'],
             pathex=['/Users/a9887715/dissertation/submission/financial-resilience-modeller/Application'],
             binaries=[],
             datas=[],
             hiddenimports=['cmath', 'chromedriver_autoinstaller'],
             hookspath=[],
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
          name='FRM',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='Static/icon.icns'
        )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='FRM')
app = BUNDLE(exe,
        name='FRM.app',
        icon='Static/icon.icns',
        bundle_identifier='com.financial-resilience-modeller',
        info_plist={
          'NSPrincipalClass': 'NSApplication',
          'NSAppleScriptEnabled': False,
          'CFBundleDocumentTypes': [
              {
                  'CFBundleTypeName': '',
                  'CFBundleTypeIconFile': 'Static/icon.icns',
                  'LSItemContentTypes': ['com.financial-resilience-modeller'],
                  'LSHandlerRank': 'Owner'
                  }
              ]
          },
        )

# -*- mode: python -*-

block_cipher = None


a = Analysis(['main.py'],
             pathex=['C:\\boulot\\works\\dwarf fortress\\dfhack_ookpy'],
             binaries=[("C:\\Anaconda3\\Lib\\site-packages\\harfang\\*.dll", ".")],
             datas=[('assets/', "."), ('environment_kit/', "."), ('environment_kit_inca/', "."), ('minecraft_assets/', "."), ('proto/build', 'proto/build')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=True,
             cipher=block_cipher)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='Harfang_DFHack',
          debug=False,
          strip=False,
          upx=False,
          console=True)

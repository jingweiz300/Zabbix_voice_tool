# -*- mode: python -*-

block_cipher = None


a = Analysis(['entry.py'],
             pathex=['listen.py', 'log.py', 'MainWindow.py', 'sqlite_local.py', 'VARIABLE.py', 'D:\\Zabbix_voice_tool\\zabbix_voice_server'],
             binaries=[],
             datas=[],
             hiddenimports=['listen', 'log', 'MainWindow', 'sqlite_local', 'VARIABLE'],
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
          name='entry',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False , icon='zabbix_voice_server.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='entry')

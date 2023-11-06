# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['SortSiteIterator.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\dhazzard\\Desktop\\SortSiteIterator\\SiteInfo.py', '.'), ('C:\\Users\\dhazzard\\Desktop\\SortSiteIterator\\SortSiteSetup.py', '.'), ('C:\\Users\\dhazzard\\Desktop\\SortSiteIterator\\SortSiteIteratorRunner.py', '.'), ('C:\\Users\\dhazzard\\Desktop\\SortSiteIterator\\SortSiteIteratorThread.py', '.'), ('C:\\Users\\dhazzard\\Desktop\\SortSiteIterator\\baseConfig.sset', '.'), ('C:\\Users\\dhazzard\\Desktop\\SortSiteIterator\\SortSiteIteratorAppShell.py', '.')],
    hiddenimports=[],
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
    name='SortSite Iterator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['IteratorIconNew.ico'],
)

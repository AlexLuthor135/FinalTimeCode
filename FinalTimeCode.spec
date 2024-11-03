# -*- mode: python ; coding: utf-8 -*-
a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('resources/icon.icns', 'resources')],
    hiddenimports=['tkinter', 'tkinter.ttk', 'platform', 'subprocess'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=True,
    optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [('v', None, 'OPTION')],
    name='FinalTimeCode',
    debug=True,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['resources/icon.icns'],
)
app = BUNDLE(
    exe,
    name='FinalTimeCode.app',
    icon='./resources/icon.icns',
    bundle_identifier='com.finaltimecode.app',
    info_plist={
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'LSMinimumSystemVersion': '10.12',
        'NSAppleEventsUsageDescription': 'This app needs access to read FCPXML files.',
        'CFBundleDocumentTypes': [
            {
                'CFBundleTypeName': 'Final Cut Pro XML Library',
                'CFBundleTypeIconFile': 'icon.icns',
                'CFBundleTypeExtensions': ['fcpxmld'],
                'CFBundleTypeRole': 'Viewer',
                'LSHandlerRank': 'Alternate',
                'LSItemContentTypes': ['com.apple.finalcutpro.fcpxmld']
            }
        ],
        'UTExportedTypeDeclarations': [
            {
                'UTTypeIdentifier': 'com.apple.finalcutpro.fcpxmld',
                'UTTypeDescription': 'Final Cut Pro XML Library',
                'UTTypeIconFile': 'icon.icns',
                'UTTypeConformsTo': ['public.data'],
                'UTTypeTagSpecification': {
                    'public.filename-extension': ['fcpxmld'],
                    'public.mime-type': ['application/x-fcpxmld']
                }
            }
        ],
        'LSEnvironment': {
            'PATH': '/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin'
        }
    }
)
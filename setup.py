from setuptools import setup
import os
import shutil

if os.path.exists('build'):
    shutil.rmtree('build')

APP = ['laura_app.py']
DATA_FILES = [
    ('resources', ['./resources/image.png']),
]
OPTIONS = {
    'argv_emulation': False,
    'packages': ['markdown2', 'PyQt5', 'PIL', 'packaging', 'platformdirs', 'weasyprint'],
    'includes': ['markdown2', 'jaraco'],
    'excludes': ['Carbon'],
    'force': True,
    'strip': False,
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
#python setup.py py2app

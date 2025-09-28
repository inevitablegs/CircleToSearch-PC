import PyInstaller.__main__
import os
import shutil

def build_executable():
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    PyInstaller.__main__.run([
        'main.py',
        '--name=DirectSearch',
        '--onefile',
        '--windowed',
        '--add-data=core;core',
        '--add-data=utils;utils',
        '--add-data=overlay.py;.',
        '--hidden-import=PySide6.QtCore',
        '--hidden-import=PySide6.QtGui',
        '--hidden-import=PySide6.QtWidgets',
        '--hidden-import=easyocr',
        '--hidden-import=selenium',
        '--hidden-import=webdriver_manager',
        '--hidden-import=requests',
        '--hidden-import=urllib3',
        '--hidden-import=chardet',
        '--hidden-import=idna',
        '--clean',
        '--noconfirm',
    ])

if __name__ == "__main__":
    build_executable()
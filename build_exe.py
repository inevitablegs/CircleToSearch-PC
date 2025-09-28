import PyInstaller.__main__
import os
import shutil

def build_executable():
    # Clean previous builds
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    
    # Check if icon exists
    icon_path = None
    possible_icon_paths = [
        'assets/icon.ico',
        'assets/tray_icon.ico', 
        'icon.ico',
        'tray_icon.ico'
    ]
    
    for path in possible_icon_paths:
        if os.path.exists(path):
            icon_path = path
            break
    
    pyinstaller_args = [
        'main.py',
        '--name=DirectSearch',
        '--onefile',
        '--windowed',
        '--add-data=core;core',
        '--add-data=utils;utils',
        '--add-data=overlay.py;.',
        '--add-data=assets;assets' if os.path.exists('assets') else '',
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
    ]
    
    # Add icon if found
    if icon_path:
        pyinstaller_args.append(f'--icon={icon_path}')
        print(f"[INFO] Using icon: {icon_path}")
    else:
        print("[WARNING] No icon file found, using default")
    
    # Remove empty arguments
    pyinstaller_args = [arg for arg in pyinstaller_args if arg]
    
    PyInstaller.__main__.run(pyinstaller_args)

if __name__ == "__main__":
    build_executable()
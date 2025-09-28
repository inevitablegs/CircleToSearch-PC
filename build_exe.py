import PyInstaller.__main__
import os
import shutil

def build_executables():
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
    
    # Build main application
    print("🔨 Building Main Application...")
    main_app_args = [
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
    
    if icon_path:
        main_app_args.append(f'--icon={icon_path}')
    
    PyInstaller.__main__.run([arg for arg in main_app_args if arg])
    
    # Build launcher
    print("🔨 Building Launcher...")
    launcher_args = [
        'launcher.py',
        '--name=DirectSearchLauncher',
        '--onefile',
        '--console',  # Keep console for debugging
        '--hidden-import=pynput',
        '--clean',
        '--noconfirm',
    ]
    
    if icon_path:
        launcher_args.append(f'--icon={icon_path}')
    
    PyInstaller.__main__.run([arg for arg in launcher_args if arg])
    
    print("✅ Build completed!")
    print("📁 Files created:")
    print("   - dist/DirectSearch.exe (Main application)")
    print("   - dist/DirectSearchLauncher.exe (Lightweight launcher)")

if __name__ == "__main__":
    build_executables()
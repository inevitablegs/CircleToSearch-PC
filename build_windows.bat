@echo off
title Building Direct Search Application
echo ========================================
echo    Direct Search - Build Script
echo ========================================
echo.

echo Step 1: Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo Step 2: Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo Step 3: Building executable...
python build_exe.py
if errorlevel 1 (
    echo ERROR: Failed to build executable
    pause
    exit /b 1
)

echo Step 4: Checking if Inno Setup is installed...
if not exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo WARNING: Inno Setup not found at default location
    echo Please install Inno Setup from: https://jrsoftware.org/isdl.php
    echo OR manually compile setup_script.iss using Inno Setup Compiler
    echo.
    echo Build completed without installer.
    echo Executable: dist\DirectSearch.exe
) else (
    echo Creating installer...
    if not exist "Output" mkdir "Output"
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_script.iss
    if errorlevel 1 (
        echo WARNING: Installer creation failed, but executable was built
        echo Executable: dist\DirectSearch.exe
    ) else (
        echo.
        echo ✅ Build completed successfully!
        echo 📦 Installer: Output\DirectSearchSetup.exe
    )
)

echo.
echo ========================================
echo    Build Process Complete
echo ========================================
echo.
pause
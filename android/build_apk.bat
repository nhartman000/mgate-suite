@echo off
@setlocal enableextensions enabledelayedexpansion

echo ==============================================
echo NYCH ANDROID APK BUILDER
echo ==============================================
echo.

echo Checking for build dependencies...
where termux-setup-storage >nul 2>&1
if %errorlevel% equ 0 (
    echo Running on Termux - native Android build
    pkg update -y
    pkg install python openjdk-17 wget -y
) else (
    echo Running on Windows - cross compile APK
    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/bee-san/pyAndroid/releases/download/v1.0.0/pyandroid.exe' -OutFile 'pyandroid.exe'}"
)

echo.
echo Building Nych APK...
pip install buildozer python-for-android >nul 2>&1

if not exist buildozer.spec (
    buildozer init >nul
)

echo.
echo Compiling APK...
buildozer android debug > build_log.txt 2>&1

echo.
echo APK created at: bin/Nych-1.0-arm64-v8a-debug.apk
echo.
pause

@echo off
@setlocal enableextensions enabledelayedexpansion

:: ==============================================
:: Nych One-Click Windows Installer
:: ==============================================
cls
echo ==============================================
echo NYCH SUBSYSTEM - ONE CLICK WINDOWS INSTALLER
echo ==============================================
echo.

:: Check admin privileges
fltmc >nul 2>&1 || (
    echo Requesting administrator privileges...
    powershell start -verb runas '%0'
    exit /b
)

echo.
echo [1/7] Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing Python 3.12...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe' -OutFile 'python_installer.exe'}"
    start /wait python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del python_installer.exe
    refreshenv >nul 2>&1
)

for /f "tokens=2" %%i in ('python --version 2^>nul') do set PYVER=%%i
echo Python version: !PYVER!

echo.
echo [2/7] Creating installation directory...
mkdir "C:\Program Files\Nych" >nul 2>&1
cd /d "%~dp0"

echo.
echo [3/7] Copying Nych subsystem files...
xcopy /e /y nych "C:\Program Files\Nych\nych\" >nul
copy /y cli\run_project.py "C:\Program Files\Nych\" >nul
copy /y test_nych.py "C:\Program Files\Nych\" >nul

echo.
echo [4/7] Installing dependencies...
pip install -r requirements.txt --quiet

echo.
echo [5/7] Adding Nych to system PATH...
setx PATH "%PATH%;C:\Program Files\Nych" /M >nul

echo.
echo [6/7] Creating desktop shortcut...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Nych.lnk'); $Shortcut.TargetPath = 'C:\Program Files\Nych\nych.exe'; $Shortcut.Save()" >nul 2>&1

echo.
echo [7/7] Running system verification...
cd "C:\Program Files\Nych"
python test_nych.py > test_result.txt 2>&1

echo.
echo ==============================================
echo INSTALLATION COMPLETE
echo ==============================================
echo.
echo Nych subsystem installed successfully.
echo Installation location: C:\Program Files\Nych
echo Desktop shortcut created.
echo.
echo To run: nych ^<project.mg8^>
echo.
pause

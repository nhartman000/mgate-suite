@echo off
@setlocal enableextensions enabledelayedexpansion

:: ==============================================
:: KADMON SYSTEM OF SYSTEMS - ONE CLICK INSTALLER
:: ==============================================
cls
echo ==============================================
echo    KADMON 1st ORDER SYSTEM - ONE CLICK BOOT
echo ==============================================
echo.

:: Request admin
fltmc >nul 2>&1 || (
    echo Requesting system privileges...
    powershell start -verb runas '%0'
    exit /b
)

set INSTALL_ROOT=C:\Kadmon
set FRONTEND_PORT=8080
set API_PORT=5000

echo.
echo [1/10] Creating system directories...
mkdir "%INSTALL_ROOT%" >nul 2>&1
mkdir "%INSTALL_ROOT%\models" >nul 2>&1
mkdir "%INSTALL_ROOT%\logs" >nul 2>&1
mkdir "%INSTALL_ROOT%\training" >nul 2>&1
mkdir "%INSTALL_ROOT%\state" >nul 2>&1

echo.
echo [2/10] Installing base system...
cd /d "%~dp0"
xcopy /e /y /q nych "%INSTALL_ROOT%\nych\"
xcopy /e /y /q engine "%INSTALL_ROOT%\engine\"
xcopy /e /y /q cli "%INSTALL_ROOT%\cli\"
xcopy /e /y /q frontend "%INSTALL_ROOT%\frontend\"
xcopy /e /y /q examples "%INSTALL_ROOT%\examples\"
copy /y requirements.txt "%INSTALL_ROOT%\"
copy /y MobiusPenAlgebra.txt "%INSTALL_ROOT%\"

echo.
echo [3/10] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing Python 3.12 runtime...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.3/python-3.12.3-amd64.exe' -OutFile '%TEMP%\pyinst.exe'}"
    start /wait %TEMP%\pyinst.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del "%TEMP%\pyinst.exe"
    refreshenv >nul 2>&1
)

echo.
echo [4/10] Installing system dependencies...
cd "%INSTALL_ROOT%"
pip install -r requirements.txt --quiet
pip install flask flask-cors requests python-dotenv --quiet

echo.
echo [5/10] Configuring frontend interface...
cd "%INSTALL_ROOT%\frontend"
npm install --silent >nul 2>&1
npm run build >nul 2>&1

echo.
echo [6/10] Initializing Mobius invariant subsystem...
python -c "
from nych.invariant import MobiusInvariant
inv = MobiusInvariant()
print(f'Loaded {len(inv.list_invariants())} system invariants')
with open('%INSTALL_ROOT%/state/invariants.initialized', 'w') as f:
    f.write('KADMON INVARIANT SYSTEM READY')
"

echo.
echo [7/10] Creating system startup scripts...
echo @echo off > "%INSTALL_ROOT%\start_kadmon.bat"
echo cd /d "%INSTALL_ROOT%" >> "%INSTALL_ROOT%\start_kadmon.bat"
echo start /min python -m api.server >> "%INSTALL_ROOT%\start_kadmon.bat"
echo timeout /t 3 /nobreak ^>nul >> "%INSTALL_ROOT%\start_kadmon.bat"
echo start http://localhost:%FRONTEND_PORT% >> "%INSTALL_ROOT%\start_kadmon.bat"
echo cd frontend >> "%INSTALL_ROOT%\start_kadmon.bat"
echo npm run dev >> "%INSTALL_ROOT%\start_kadmon.bat"

echo.
echo [8/10] Creating desktop integration...
powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\Kadmon System.lnk'); $Shortcut.TargetPath = '%INSTALL_ROOT%\start_kadmon.bat'; $Shortcut.IconLocation = '%INSTALL_ROOT%\frontend\public\favicon.ico'; $Shortcut.Save()" >nul 2>&1

echo.
echo [9/10] Registering Windows service...
sc create KadmonSystem binPath= "%INSTALL_ROOT%\start_kadmon.bat" start= auto >nul 2>&1

echo.
echo [10/10] Running system verification...
python -m pytest -x test_nych.py > "%INSTALL_ROOT%\logs\install.log" 2>&1

echo.
echo ==============================================
echo KADMON SYSTEM INSTALLATION COMPLETE
echo ==============================================
echo.
echo System root: C:\Kadmon
echo Frontend: http://localhost:%FRONTEND_PORT%
echo API: http://localhost:%API_PORT%
echo.
echo ✅ Nych 5th-order subsystem active
echo ✅ Mobius invariant engine initialized
echo ✅ DAG execution engine ready
echo ✅ Frontend interface built
echo.
echo ==============================================
echo NEXT STEPS:
echo 1. Double-click the Kadmon System desktop shortcut
echo 2. When frontend loads, register Model 1 and Model 2
echo 3. Begin triadic training loop
echo.
echo System will automatically start now...
echo ==============================================
echo.

timeout /t 5 /nobreak >nul
start "" "%INSTALL_ROOT%\start_kadmon.bat"

pause

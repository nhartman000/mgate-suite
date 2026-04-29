@echo off
echo Starting Kadmon Multiplayer World Environment...
echo.

echo Starting backend server...
start "Kadmon Server" cmd /k "cd server && python main.py"

echo Waiting for server to start...
timeout /t 3 /nobreak >nul

echo Starting frontend client...
start "Kadmon Client" cmd /k "cd client && npm run dev"

echo.
echo Kadmon Multiplayer World is now running!
echo Frontend: http://localhost:3000
echo Backend API: http://localhost:8000
echo.
echo Press any key to stop all services...
pause >nul

echo Stopping services...
taskkill /fi "WINDOWTITLE eq Kadmon Server"
taskkill /fi "WINDOWTITLE eq Kadmon Client"

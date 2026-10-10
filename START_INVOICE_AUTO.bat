@echo off
REM Auto-restart launcher for Invoice Automation Web GUI
REM If the server stops/crashes, it will automatically restart after 3 seconds
setlocal
set "PYTHON_EXE=%USERPROFILE%\.workbuddy-ai\binaries\python\envs\default\Scripts\python.exe"
set "SCRIPT=%~dp0invoice_web_gui.py"
echo ============================================
echo  Invoice Automation Server (Auto-Restart)
echo ============================================
echo  Server will auto-restart if it stops.
echo  Press Ctrl+C twice to fully stop.
echo ============================================
echo.
:loop
start /wait "" "%PYTHON_EXE%" "%SCRIPT%"
echo.
echo [Watchdog] Server stopped. Restarting in 3 seconds...
echo [Watchdog] Press Ctrl+C to cancel.
timeout /t 3 /nobreak >nul
goto loop
endlocal

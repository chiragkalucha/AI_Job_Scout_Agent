@echo off
color 0A
title AI Job Scout - Complete Installation

echo.
echo ========================================================
echo          AI JOB SCOUT - INSTALLATION
echo ========================================================
echo.

cd /d "%~dp0"

REM Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.9+ from python.org
    pause
    exit /b 1
)
echo       Python found!

REM Create venv
echo.
echo [2/6] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
)
echo       Virtual environment ready!

REM Activate and install
echo.
echo [3/6] Installing dependencies...
call venv\Scripts\activate.bat
pip install --upgrade pip >nul 2>&1
pip install -r requirements_chatbot.txt
echo       Dependencies installed!

REM Build executable
echo.
echo [4/6] Building executable...
python build_exe.py
echo       Executable built!

REM Create desktop shortcut
echo.
echo [5/6] Creating desktop shortcut...
set DESKTOP=%USERPROFILE%\Desktop
set EXE_PATH=%~dp0dist\AI_Job_Scout.exe

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%DESKTOP%\AI Job Scout.lnk'); $s.TargetPath = '%EXE_PATH%'; $s.WorkingDirectory = '%~dp0dist'; $s.Description = 'AI Job Scout - Automated Job Hunter'; $s.Save()"

echo       Desktop shortcut created!

REM Setup auto-start (optional)
echo.
echo [6/6] Setup auto-start?
set /p AUTOSTART="Start on Windows boot? (Y/N): "

if /i "%AUTOSTART%"=="Y" (
    set STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
    powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTUP%\AI Job Scout.lnk'); $s.TargetPath = '%EXE_PATH%'; $s.WorkingDirectory = '%~dp0dist'; $s.Save()"
    echo       Auto-start configured!
) else (
    echo       Skipped auto-start
)

echo.
echo ========================================================
echo          INSTALLATION COMPLETE!
echo ========================================================
echo.
echo Next steps:
echo   1. Configure settings in: dist\config\.env
echo   2. Launch from Desktop: "AI Job Scout"
echo   3. Start hunting!
echo.
echo Desktop shortcut created: %DESKTOP%\AI Job Scout.lnk
echo Executable location: dist\AI_Job_Scout.exe
echo.
pause
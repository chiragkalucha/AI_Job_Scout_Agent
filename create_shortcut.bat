@echo off
echo Creating FIXED desktop shortcut...

set PROJECT_DIR=C:\Users\LENOVO\Desktop\ai_job_scout
set DESKTOP=%USERPROFILE%\Desktop
set PYTHON_EXE=%PROJECT_DIR%\venv\Scripts\pythonw.exe

:: Create VBScript to make shortcut
echo Set ws = CreateObject("WScript.Shell") > "%TEMP%\mkshortcut.vbs"
echo Set sc = ws.CreateShortcut("%DESKTOP%\AI Job Scout.lnk") >> "%TEMP%\mkshortcut.vbs"
echo sc.TargetPath = "%PYTHON_EXE%" >> "%TEMP%\mkshortcut.vbs"
echo sc.Arguments = "-X utf8 chatbot\main_app.py" >> "%TEMP%\mkshortcut.vbs"

:: ✅ KEY: Set working directory to project root
echo sc.WorkingDirectory = "%PROJECT_DIR%" >> "%TEMP%\mkshortcut.vbs"

echo sc.Description = "AI Job Scout - Automated Job Hunter" >> "%TEMP%\mkshortcut.vbs"
echo sc.Save >> "%TEMP%\mkshortcut.vbs"
cscript //nologo "%TEMP%\mkshortcut.vbs"
del "%TEMP%\mkshortcut.vbs"

echo.
echo ✅ Desktop shortcut created!
echo.
echo Shortcut runs from: %PROJECT_DIR%
echo.

:: Test it
echo Testing launch...
start "" "%DESKTOP%\AI Job Scout.lnk"

pause



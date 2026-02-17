@echo off
:: ✅ KEY FIX: Change to project directory FIRST
cd /d "C:\Users\LENOVO\Desktop\ai_job_scout"

:: Verify we're in right place
if not exist "chatbot\main_app.py" (
    echo ERROR: Wrong directory!
    echo Expected: C:\Users\LENOVO\Desktop\ai_job_scout
    echo Got: %CD%
    pause
    exit /b 1
)

:: Set encoding
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

:: Run with venv Python
echo Starting AI Job Scout...
"C:\Users\LENOVO\Desktop\ai_job_scout\venv\Scripts\pythonw.exe" -X utf8 chatbot\main_app.py

exit
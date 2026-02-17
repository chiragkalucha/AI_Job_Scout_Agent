@echo off
echo Creating distribution package...
echo.

REM Create package folder
if not exist "AI_Job_Scout_Package" mkdir "AI_Job_Scout_Package"

REM Copy exe and config
xcopy /E /I /Y dist\* "AI_Job_Scout_Package\"

REM Remove your personal .env
del "AI_Job_Scout_Package\config\.env" 2>nul

REM Create template .env
echo # AI Job Scout Configuration > "AI_Job_Scout_Package\config\.env"
echo. >> "AI_Job_Scout_Package\config\.env"
echo # REQUIRED - Get from Google Sheets >> "AI_Job_Scout_Package\config\.env"
echo GOOGLE_SHEET_ID=your_google_sheet_id_here >> "AI_Job_Scout_Package\config\.env"
echo. >> "AI_Job_Scout_Package\config\.env"
echo # REQUIRED - Get from console.groq.com >> "AI_Job_Scout_Package\config\.env"
echo GROQ_API_KEY=your_groq_api_key_here >> "AI_Job_Scout_Package\config\.env"
echo. >> "AI_Job_Scout_Package\config\.env"
echo # Job Search Settings >> "AI_Job_Scout_Package\config\.env"
echo MIN_SALARY_LPA=15 >> "AI_Job_Scout_Package\config\.env"
echo MAX_EXPERIENCE_YEARS=2 >> "AI_Job_Scout_Package\config\.env"
echo JOB_ROLES=Data Analyst,Business Analyst >> "AI_Job_Scout_Package\config\.env"

REM Create README
echo AI JOB SCOUT - QUICK START > "AI_Job_Scout_Package\README.txt"
echo ================================ >> "AI_Job_Scout_Package\README.txt"
echo. >> "AI_Job_Scout_Package\README.txt"
echo SETUP: >> "AI_Job_Scout_Package\README.txt"
echo 1. Edit config\.env >> "AI_Job_Scout_Package\README.txt"
echo 2. Add your GOOGLE_SHEET_ID >> "AI_Job_Scout_Package\README.txt"
echo 3. Add your GROQ_API_KEY >> "AI_Job_Scout_Package\README.txt"
echo 4. Save file >> "AI_Job_Scout_Package\README.txt"
echo. >> "AI_Job_Scout_Package\README.txt"
echo RUN: >> "AI_Job_Scout_Package\README.txt"
echo Double-click: AI_Job_Scout.exe >> "AI_Job_Scout_Package\README.txt"
echo. >> "AI_Job_Scout_Package\README.txt"
echo USAGE: >> "AI_Job_Scout_Package\README.txt"
echo Type in chat: >> "AI_Job_Scout_Package\README.txt"
echo - start hunt    (starts continuous hunting) >> "AI_Job_Scout_Package\README.txt"
echo - stop hunt     (stops hunting) >> "AI_Job_Scout_Package\README.txt"
echo - status        (shows settings) >> "AI_Job_Scout_Package\README.txt"
echo - help          (shows commands) >> "AI_Job_Scout_Package\README.txt"

echo.
echo ✅ Package created: AI_Job_Scout_Package\
echo.
echo Send this folder to your friend!
echo.
pause
# build_exe.py - Build standalone executable (UPDATED)

import PyInstaller.__main__
import os
import shutil

print("="*70)
print("BUILDING AI JOB SCOUT EXECUTABLE")
print("="*70)
print()

# Clean previous builds
print("[1/5] Cleaning previous builds...")
for folder in ['build', 'dist', '__pycache__']:
    if os.path.exists(folder):
        shutil.rmtree(folder)
        print(f"   Removed {folder}/")

# Clean spec file
if os.path.exists('AI_Job_Scout.spec'):
    os.remove('AI_Job_Scout.spec')
    print("   Removed AI_Job_Scout.spec")

print()
print("[2/5] Collecting all Python files...")

# Get all Python files
python_files = []
for root, dirs, files in os.walk('.'):
    # Skip venv and build folders
    if 'venv' in root or 'build' in root or 'dist' in root:
        continue
    
    for file in files:
        if file.endswith('.py'):
            python_files.append(os.path.join(root, file))

print(f"   Found {len(python_files)} Python files")

print()
print("[3/5] Building executable...")

# Build arguments
build_args = [
    'chatbot/main_app.py',
    '--name=AI_Job_Scout',
    '--onefile',
    '--windowed',
    '--noconfirm',
    '--clean',
    
    # Icon (if exists)
    '--icon=icon.ico' if os.path.exists('icon.ico') else '--icon=NONE',
    
    # Add all project folders as data
    '--add-data=config;config',
    '--add-data=scrapers;scrapers',
    '--add-data=utils;utils',
    '--add-data=ai_analysis;ai_analysis',
    '--add-data=sheets_integration;sheets_integration',
    '--add-data=chatbot;chatbot',
    '--add-data=logs;logs',
    
    # Hidden imports
    '--hidden-import=PyQt5',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=PyQt5.QtWidgets',
    '--hidden-import=apscheduler',
    '--hidden-import=apscheduler.schedulers.background',
    '--hidden-import=selenium',
    '--hidden-import=selenium.webdriver',
    '--hidden-import=dotenv',
    '--hidden-import=groq',
    '--hidden-import=fuzzywuzzy',
    '--hidden-import=google.auth',
    '--hidden-import=googleapiclient',
    '--hidden-import=bs4',
    
    # Collect all submodules
    '--collect-all=PyQt5',
    '--collect-all=selenium',
    
    # Console options
    '--noconsole',
    
    # Exclude unnecessary modules
    '--exclude-module=matplotlib',
    '--exclude-module=numpy',
    '--exclude-module=pandas',
]

# Run PyInstaller
PyInstaller.__main__.run(build_args)

print()
print("[4/5] Copying required files...")

# Create dist structure
os.makedirs('dist/config', exist_ok=True)
os.makedirs('dist/logs', exist_ok=True)

# Copy config template (without sensitive data)
if os.path.exists('config/.env.example'):
    shutil.copy('config/.env.example', 'dist/config/.env.example')
elif os.path.exists('config/.env'):
    # Copy but remove sensitive values
    with open('config/.env', 'r') as f:
        lines = f.readlines()
    
    with open('dist/config/.env', 'w') as f:
        for line in lines:
            if '=' in line and not line.strip().startswith('#'):
                key, _ = line.split('=', 1)
                # Keep structure but clear sensitive values
                if 'API_KEY' in key or 'SHEET_ID' in key:
                    f.write(f'{key}=YOUR_VALUE_HERE\n')
                else:
                    f.write(line)
            else:
                f.write(line)

print("   Copied config/")

print()
print("[5/5] Creating distribution package...")

# Create README
readme = """# AI Job Scout - Standalone Application

## Quick Start

1. **Configure Settings:**
   - Open: config/.env
   - Add your GOOGLE_SHEET_ID
   - Add your GROQ_API_KEY
   - Set MIN_SALARY_LPA (default: 15)
   - Set JOB_ROLES (default: Data Analyst)

2. **Run:**
   - Double-click: AI_Job_Scout.exe
   - Chat window opens
   - Icon appears in system tray

3. **Usage:**
   Type in chat:
   - "start hunt" → Starts continuous hunting (every 30 min)
   - "stop hunt" → Stops all hunting
   - "change salary to 20" → Updates min salary
   - "add Data Scientist" → Adds new role
   - "status" → Shows current settings
   - "help" → Shows all commands

## Features

✅ Continuous job hunting (runs every 30 minutes)
✅ Natural language commands
✅ Smart intent detection
✅ Quick action buttons
✅ System tray integration
✅ Real-time progress updates
✅ Desktop notifications
✅ No Python installation needed

## Commands

**Hunting:**
- start hunt → Continuous mode (every 30 min)
- stop hunt → Stop completely

**Settings:**
- change salary to X → Update minimum salary
- change roles to X, Y → Replace all roles
- add ROLE → Add new role to list
- remove ROLE → Remove role from list

**Data:**
- clean jobs → Remove checked rows from sheet
- open sheet → Open Google Sheet in browser
- status → Show current settings

## System Requirements

- Windows 10/11
- Internet connection
- Google Chrome (for web scraping)
- 2GB RAM minimum
- 500MB free disk space

## Troubleshooting

**Icon not showing?**
- Check system tray hidden icons (^ arrow)
- Right-click taskbar → Taskbar settings → Show all icons

**Hunt not starting?**
- Check config/.env is properly configured
- Check internet connection
- View logs/ folder for errors

**"Stop hunt" not working?**
- Wait a few seconds, process is terminating
- Check system tray status

**No jobs found?**
- Lower MIN_SALARY_LPA in config/.env
- Check job roles are correct
- Verify scrapers are working (check logs/)

## Distribution

To share with others:
1. Copy entire folder (including AI_Job_Scout.exe and config/)
2. Send to friend
3. They configure config/.env
4. Run AI_Job_Scout.exe

## Support

For issues:
1. Check logs/ folder for error details
2. Verify config/.env settings
3. Ensure Google Sheets API is enabled
4. Check GROQ API key is valid

## Version

AI Job Scout v1.0.0
Built: """ + str(__import__('datetime').datetime.now().strftime('%Y-%m-%d'))

with open('dist/README.txt', 'w', encoding='utf-8') as f:
    f.write(readme)

print("   Created README.txt")

# Create example .env if doesn't exist
if not os.path.exists('dist/config/.env'):
    example_env = """# AI Job Scout Configuration

# Google Sheets (REQUIRED)
GOOGLE_SHEET_ID=your_google_sheet_id_here

# Groq AI API (REQUIRED)
GROQ_API_KEY=your_groq_api_key_here

# Job Search Settings
MIN_SALARY_LPA=15
MAX_EXPERIENCE_YEARS=2
JOB_ROLES=Data Analyst,Business Analyst

# Optional: Add more roles separated by commas
# JOB_ROLES=Data Analyst,Business Analyst,Data Scientist,ML Engineer
"""
    
    with open('dist/config/.env', 'w') as f:
        f.write(example_env)
    
    print("   Created config/.env template")

print()
print("="*70)
print("BUILD COMPLETE!")
print("="*70)
print()

# Get file size
exe_path = 'dist/AI_Job_Scout.exe'
if os.path.exists(exe_path):
    size_mb = os.path.getsize(exe_path) / 1024 / 1024
    print(f"📦 Executable: {exe_path}")
    print(f"📏 Size: {size_mb:.1f} MB")
else:
    print("⚠️  Warning: Executable not found!")

print()
print("📂 Distribution folder: dist/")
print()
print("✅ Ready to distribute!")
print()
print("Next steps:")
print("1. Configure: dist/config/.env")
print("2. Test: dist/AI_Job_Scout.exe")
print("3. Share: Send entire dist/ folder")
print()
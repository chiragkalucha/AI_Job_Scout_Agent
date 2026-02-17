# 🤖 AI Job Scout

Automated job hunting assistant with AI-powered matching and continuous monitoring.

## Features

- 🔄 Continuous job hunting (runs every 30 minutes)
- 🤖 Natural language chat interface
- 🎯 AI-powered job matching using Groq
- 📊 Google Sheets integration
- 🔔 Desktop notifications
- 💬 Smart NLP command processing
- 🖥️ Standalone executable (no Python needed)

## Quick Start

### For Users (Windows)

1. Download latest release
2. Extract to folder
3. Edit `config/.env`:
```env
   GOOGLE_SHEET_ID=your_sheet_id
   GROQ_API_KEY=your_api_key
```
4. Run `AI_Job_Scout.exe`
5. Type "start hunt" in chat

### For Developers
```bash
# Clone
git clone https://github.com/yourusername/ai-job-scout.git
cd ai-job-scout

# Install
pip install -r requirements.txt
pip install -r requirements_chatbot.txt

# Configure
cp config/.env.example config/.env
# Edit config/.env

# Run
python chatbot/main_app.py

# Build
python build_exe.py
```

## Commands

- `start hunt` - Start continuous hunting
- `stop hunt` - Stop hunting
- `change salary to X` - Update min salary
- `add ROLE` - Add job role
- `status` - Show settings
- `help` - Show all commands

## Tech Stack

- **GUI**: PyQt5
- **NLP**: FuzzyWuzzy
- **AI**: Groq (Llama 3.3)
- **Scraping**: Selenium, BeautifulSoup
- **Sheets**: Google Sheets API
- **Scheduling**: APScheduler

## License

MIT License
```

---

## **COMPLETE CHECKLIST:**
```
✅ BUILD COMPLETED
├── ✅ Executable created (dist/AI_Job_Scout.exe)
├── ✅ Config template (dist/config/.env)
└── ✅ README included

✅ TESTING
├── ✅ Configure dist/config/.env
├── ✅ Run AI_Job_Scout.exe
├── ✅ Test "status" command
├── ✅ Test "start hunt" command
├── ✅ Test "stop hunt" command
└── ✅ Test all other commands

✅ DEPLOYMENT
├── ✅ Create desktop shortcut
├── ✅ Setup auto-start (optional)
└── ✅ Package for distribution

✅ SHARING
├── ✅ Create package for friend
├── ✅ Compress to .zip
└── ✅ Send with instructions

🔜 NEXT PHASE
├── 🔜 Docker containerization
├── 🔜 GitHub repository
└── 🔜 Documentation
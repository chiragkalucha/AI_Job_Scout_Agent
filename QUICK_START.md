# AI Job Scout - Quick Start Guide

## Installation

1. **Run Installation:**
```
   Double-click: INSTALL_COMPLETE.bat
   Wait 5-10 minutes for completion
```

2. **Configure Settings:**
```
   Open: dist/config/.env
   
   Add:
   GOOGLE_SHEET_ID=your_sheet_id
   GROQ_API_KEY=your_api_key
   MIN_SALARY_LPA=15
   JOB_ROLES=Data Analyst,Business Analyst
```

3. **Launch:**
```
   Desktop → Double-click "AI Job Scout"
```

## Usage

### Starting Continuous Hunt
```
You: start hunt

Bot: Continuous hunting activated!
     Will run every 30 minutes...
```

### Stopping Hunt
```
You: stop hunt

Bot: Hunting fully stopped!
```

### Changing Settings
```
You: change salary to 25
You: change roles to Data Scientist, ML Engineer
You: add Software Engineer
```

### Managing Jobs
```
You: clean jobs      # Remove checked rows
You: open sheet      # View Google Sheet
You: status          # Show current settings
```

## Commands

| Command | Action |
|---------|--------|
| `start hunt` | Start continuous hunting (30 min intervals) |
| `start hunt once` | Run one time only |
| `stop hunt` | Stop all hunting |
| `change salary to X` | Update minimum salary |
| `change roles to X, Y` | Update job roles |
| `add ROLE` | Add new role |
| `clean jobs` | Remove checked jobs from sheet |
| `open sheet` | Open Google Sheet |
| `status` | Show current settings |
| `help` | Show all commands |

## Features

✅ Continuous job hunting (every 30 minutes)
✅ Natural language commands
✅ Smart NLP understanding
✅ Quick action buttons
✅ System tray integration
✅ Desktop notifications
✅ Auto-start on Windows boot
✅ Standalone executable (no Python needed)

## Distribution

**To share with others:**
1. Copy entire `dist/` folder
2. Send to friend
3. They just double-click `AI_Job_Scout.exe`
4. Configure their `.env` file
5. Start hunting!

## Troubleshooting

**Icon not showing?**
- Check system tray hidden icons (^ arrow)

**Not finding jobs?**
- Lower MIN_SALARY_LPA
- Check internet connection

**Commands not working?**
- Use quick action buttons instead
- Type "help" for command list
```


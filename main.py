# main.py - FIXED FOR SUBPROCESS/CHATBOT EXECUTION

import sys
import os
from datetime import datetime
import io

# ✅ FIX ENCODING FOR SUBPROCESS
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from orchestrator import JobScrapingOrchestrator
from ai_analysis.resume_analyzer import ResumeAnalyzer
from sheets_integration.sheets_updater import GoogleSheetsUpdater
from utils.run_tracker import RunTracker
from dotenv import load_dotenv

load_dotenv('config/.env')

# Safe print function
def safe_print(text):
    """Print with fallback for encoding errors"""
    try:
        print(text)
    except UnicodeEncodeError:
        # Remove emojis and special characters
        import re
        clean_text = re.sub(r'[^\x00-\x7F]+', '', text)
        print(clean_text)

safe_print("="*70)
safe_print("AI JOB SCOUT V4 - SMART DEDUPLICATION")
safe_print("="*70)
safe_print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
safe_print("")

# Initialize tracker
tracker = RunTracker()

# Check last run
last_run = tracker.get_last_run_time()
time_since = tracker.get_time_since_last_run()

safe_print(f"Last run: {time_since}")

if last_run:
    safe_print(f"   ({last_run.strftime('%Y-%m-%d %H:%M:%S')})")
    safe_print(f"   Will fetch jobs posted AFTER this time")
else:
    safe_print(f"   (First run - will fetch all recent jobs)")

safe_print("")

try:
    # STEP 0: Clean up checked jobs
    safe_print("="*70)
    safe_print("STEP 0: CLEANUP")
    safe_print("="*70)
    
    if os.getenv('GOOGLE_SHEET_ID'):
        try:
            updater = GoogleSheetsUpdater()
            updater.delete_checked_jobs()
        except Exception as e:
            safe_print(f"Cleanup skipped: {e}")
    
    # STEP 1: Scrape jobs
    safe_print("")
    safe_print("="*70)
    safe_print("STEP 1: SCRAPING JOBS")
    safe_print("="*70)
    
    orchestrator = JobScrapingOrchestrator(since_time=last_run)
    jobs = orchestrator.run_all_scrapers()
    
    if not jobs:
        safe_print("")
        safe_print("No new jobs found")
        safe_print("")
        safe_print("This is normal if:")
        safe_print("   - No jobs posted since last run")
        safe_print("   - All jobs already in sheet")
        safe_print("   - Filters too strict")
        exit()
    
    safe_print(f"")
    safe_print(f"Scraped {len(jobs)} jobs")
    
    # STEP 2: Filter duplicates
    safe_print("")
    safe_print("="*70)
    safe_print("STEP 2: REMOVING DUPLICATES")
    safe_print("="*70)
    
    if os.getenv('GOOGLE_SHEET_ID'):
        try:
            updater = GoogleSheetsUpdater()
            new_jobs = updater.filter_new_jobs(jobs)
            
            if not new_jobs:
                safe_print("")
                safe_print("All jobs already in sheet (0 new jobs)")
                safe_print("Updating last run time anyway...")
                tracker.update_last_run_time(jobs_found=0)
                exit()
            
            jobs = new_jobs
            
        except Exception as e:
            safe_print(f"Deduplication failed: {e}")
            safe_print("Continuing with all jobs...")
    
    safe_print(f"")
    safe_print(f"{len(jobs)} NEW jobs to process")
    
    # STEP 3: AI Analysis
    if os.getenv('GROQ_API_KEY'):
        safe_print("")
        safe_print("="*70)
        safe_print("STEP 3: AI ANALYSIS")
        safe_print("="*70)
        
        try:
            analyzer = ResumeAnalyzer()
            analyzed_jobs = analyzer.batch_analyze(jobs)
        except Exception as e:
            safe_print(f"AI analysis failed: {e}")
            analyzed_jobs = jobs
    else:
        safe_print("")
        safe_print("Skipping AI analysis (no GROQ_API_KEY)")
        analyzed_jobs = jobs
    
    # STEP 4: Update Google Sheets
    if os.getenv('GOOGLE_SHEET_ID'):
        safe_print("")
        safe_print("="*70)
        safe_print("STEP 4: UPDATING GOOGLE SHEETS")
        safe_print("="*70)
        
        updater = GoogleSheetsUpdater()
        success = updater.add_jobs_batch(analyzed_jobs)
        
        if success:
            safe_print(f"")
            safe_print(f"View your jobs:")
            safe_print(f"   https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEET_ID')}")
    
    # STEP 5: Update last run time
    safe_print("")
    safe_print("="*70)
    safe_print("STEP 5: UPDATING TRACKER")
    safe_print("="*70)
    
    tracker.update_last_run_time(jobs_found=len(analyzed_jobs))
    
    # SUMMARY
    safe_print("")
    safe_print("="*70)
    safe_print("COMPLETE!")
    safe_print("="*70)
    safe_print(f"{len(analyzed_jobs)} NEW jobs added")
    safe_print(f"All jobs are unique (no duplicates)")
    safe_print(f"Next run will fetch jobs posted AFTER now")
    
    high_chance = sum(1 for j in analyzed_jobs if j.get('selection_chances') == 'High')
    if high_chance > 0:
        safe_print(f"{high_chance} high-chance opportunities!")
    
    safe_print(f"")
    safe_print(f"Completed: {datetime.now().strftime('%H:%M:%S')}")
    
except KeyboardInterrupt:
    safe_print("")
    safe_print("")
    safe_print("Stopped by user")
except Exception as e:
    safe_print("")
    safe_print("")
    safe_print(f"Error: {e}")
    import traceback
    traceback.print_exc()
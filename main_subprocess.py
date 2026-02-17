# main_subprocess.py - SUBPROCESS-SAFE VERSION (No emoji crashes)

import sys
import os
import io
from datetime import datetime

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ✅ ALSO set environment variable
os.environ['PYTHONIOENCODING'] = 'utf-8'

# ✅ FIX 1: Add project root to path FIRST
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

print("="*70)
print("AI JOB SCOUT - RUNNING")
print("="*70)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Project root: {PROJECT_ROOT}")
print()

# ✅ FIX 2: Force UTF-8 output (prevents emoji crashes)
import io
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except AttributeError:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Now import project modules
from orchestrator import JobScrapingOrchestrator
from ai_analysis.resume_analyzer import ResumeAnalyzer
from sheets_integration.sheets_updater import GoogleSheetsUpdater
from utils.run_tracker import RunTracker
from dotenv import load_dotenv

# Load environment
load_dotenv(os.path.join(PROJECT_ROOT, 'config', '.env'))

# Initialize tracker
tracker = RunTracker()
last_run = tracker.get_last_run_time()
time_since = tracker.get_time_since_last_run()

print(f"Last run: {time_since}")
if last_run:
    print(f"   ({last_run.strftime('%Y-%m-%d %H:%M:%S')})")
print()

try:
    # STEP 0: Cleanup checked jobs
    print("="*70)
    print("STEP 0: CLEANUP")
    print("="*70)
    
    if os.getenv('GOOGLE_SHEET_ID'):
        try:
            updater = GoogleSheetsUpdater()
            deleted = updater.delete_checked_jobs()
            if deleted:
                print(f"   Deleted {deleted} checked jobs")
            else:
                print("   No checked jobs to delete")
        except Exception as e:
            print(f"   Cleanup error: {e}")
    else:
        print("   Skipping cleanup (no GOOGLE_SHEET_ID)")
    
    # STEP 1: Scrape jobs
    print()
    print("="*70)
    print("STEP 1: SCRAPING JOBS")
    print("="*70)
    
    orchestrator = JobScrapingOrchestrator(since_time=last_run)
    jobs = orchestrator.run_all_scrapers()
    
    if not jobs:
        print()
        print("No new jobs found")
        print()
        print("Possible reasons:")
        print("   - No jobs posted since last run")
        print("   - All jobs already in sheet")
        print("   - Filters too strict (MIN_SALARY_LPA, MAX_EXPERIENCE_YEARS)")
        print()
        # Update tracker even if no jobs found
        tracker.update_last_run_time(jobs_found=0)
        sys.exit(0)
    
    print(f"")
    print(f"Scraped {len(jobs)} jobs total")
    
    # STEP 2: Filter duplicates (URL-based)
    print()
    print("="*70)
    print("STEP 2: REMOVING DUPLICATES")
    print("="*70)
    
    if os.getenv('GOOGLE_SHEET_ID'):
        try:
            updater = GoogleSheetsUpdater()
            
            # Get existing URLs from sheet
            existing_count = len(updater.get_existing_job_urls())
            print(f"   Found {existing_count} existing jobs in sheet")
            
            # Filter out duplicates
            new_jobs = updater.filter_new_jobs(jobs)
            
            if not new_jobs:
                print()
                print(f"All {len(jobs)} jobs already in sheet (0 new jobs)")
                print()
                print("This is normal if:")
                print("   - Recently ran the hunt")
                print("   - No new jobs have been posted")
                print()
                # Update tracker
                tracker.update_last_run_time(jobs_found=0)
                sys.exit(0)
            
            skipped = len(jobs) - len(new_jobs)
            print(f"   Filtered: {len(new_jobs)} NEW jobs (skipped {skipped} duplicates)")
            
            jobs = new_jobs
            
        except Exception as e:
            print(f"   Deduplication failed: {e}")
            print("   Continuing with all jobs...")
    else:
        print("   Skipping deduplication (no GOOGLE_SHEET_ID)")
    
    print(f"")
    print(f"{len(jobs)} NEW jobs to process")
    
    # STEP 3: AI Analysis (only if GROQ_API_KEY exists)
    print()
    print("="*70)
    print("STEP 3: AI ANALYSIS")
    print("="*70)
    
    if os.getenv('GROQ_API_KEY'):
        try:
            analyzer = ResumeAnalyzer()
            print(f"   Analyzing {len(jobs)} jobs...")
            analyzed_jobs = analyzer.batch_analyze(jobs)
            print(f"   Analysis complete!")
        except Exception as e:
            print(f"   AI analysis failed: {e}")
            print("   Continuing without AI analysis...")
            analyzed_jobs = jobs
    else:
        print("   Skipping AI analysis (no GROQ_API_KEY)")
        analyzed_jobs = jobs
    
    # STEP 4: Update Google Sheets
    print()
    print("="*70)
    print("STEP 4: UPDATING GOOGLE SHEETS")
    print("="*70)
    
    if os.getenv('GOOGLE_SHEET_ID'):
        try:
            updater = GoogleSheetsUpdater()
            success = updater.add_jobs_batch(analyzed_jobs)
            
            if success:
                print(f"   Successfully added {len(analyzed_jobs)} jobs")
                print()
                print(f"   View your jobs:")
                print(f"   https://docs.google.com/spreadsheets/d/{os.getenv('GOOGLE_SHEET_ID')}")
        except Exception as e:
            print(f"   Failed to update sheet: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("   Skipping sheet update (no GOOGLE_SHEET_ID)")
    
    # STEP 5: Update tracker
    print()
    print("="*70)
    print("STEP 5: UPDATING TRACKER")
    print("="*70)
    
    tracker.update_last_run_time(jobs_found=len(analyzed_jobs))
    print(f"   Tracker updated successfully")
    
    # FINAL SUMMARY
    print()
    print("="*70)
    print("COMPLETE!")
    print("="*70)
    print(f"{len(analyzed_jobs)} NEW jobs added")
    print(f"All jobs are unique (no duplicates)")
    print(f"Next run will fetch jobs posted AFTER now")
    
    # High chance count
    high_chance = sum(1 for j in analyzed_jobs if j.get('selection_chances') == 'High')
    if high_chance > 0:
        print(f"{high_chance} high-chance opportunities!")
    
    print(f"")
    print(f"Completed: {datetime.now().strftime('%H:%M:%S')}")
    print()

except KeyboardInterrupt:
    print()
    print()
    print("Stopped by user (Ctrl+C)")
    sys.exit(1)
    
except Exception as e:
    print()
    print()
    print(f"FATAL ERROR: {e}")
    print()
    import traceback
    traceback.print_exc()
    sys.exit(1)
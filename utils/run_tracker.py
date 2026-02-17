# utils/run_tracker.py - Track last successful run

import os
import json
from datetime import datetime

class RunTracker:
    """Track when scraping was last run"""
    
    def __init__(self, tracker_file='logs/last_run.json'):
        self.tracker_file = tracker_file
        
        # Ensure logs directory exists
        os.makedirs(os.path.dirname(tracker_file), exist_ok=True)
    
    def get_last_run_time(self):
        """Get timestamp of last successful run"""
        
        if not os.path.exists(self.tracker_file):
            # First run - return None (get all jobs)
            return None
        
        try:
            with open(self.tracker_file, 'r') as f:
                data = json.load(f)
                
            last_run = data.get('last_successful_run')
            
            if last_run:
                # Convert to datetime
                return datetime.fromisoformat(last_run)
            else:
                return None
                
        except Exception as e:
            print(f"⚠️  Error reading last run time: {e}")
            return None
    
    def update_last_run_time(self, jobs_found=0):
        """Update last run timestamp"""
        
        now = datetime.now()
        
        data = {
            'last_successful_run': now.isoformat(),
            'timestamp_readable': now.strftime('%Y-%m-%d %H:%M:%S'),
            'jobs_found': jobs_found
        }
        
        try:
            with open(self.tracker_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            print(f"✅ Last run updated: {data['timestamp_readable']}")
            return True
            
        except Exception as e:
            print(f"⚠️  Error updating last run time: {e}")
            return False
    
    def get_time_since_last_run(self):
        """Get human-readable time since last run"""
        
        last_run = self.get_last_run_time()
        
        if not last_run:
            return "Never (first run)"
        
        now = datetime.now()
        delta = now - last_run
        
        hours = delta.total_seconds() / 3600
        
        if hours < 1:
            return f"{int(delta.total_seconds() / 60)} minutes ago"
        elif hours < 24:
            return f"{int(hours)} hours ago"
        else:
            return f"{int(hours / 24)} days ago"


# Test
if __name__ == "__main__":
    tracker = RunTracker()
    
    print("="*70)
    print("RUN TRACKER TEST")
    print("="*70)
    
    last_run = tracker.get_last_run_time()
    print(f"\nLast run: {last_run}")
    print(f"Time since: {tracker.get_time_since_last_run()}")
    
    print("\nUpdating to now...")
    tracker.update_last_run_time(jobs_found=25)
    
    print(f"\nNew last run: {tracker.get_last_run_time()}")
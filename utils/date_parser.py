# utils/date_parser.py - Extract real posting dates

from datetime import datetime, timedelta
import re

class JobDateParser:
    """Parse job posting dates from various formats"""
    
    @staticmethod
    def parse_relative_date(text):
        """
        Convert relative dates to actual datetime
        
        Examples:
        "2 hours ago" → 2026-02-14 17:00:00
        "1 day ago" → 2026-02-13 19:00:00
        "Just posted" → 2026-02-14 19:00:00
        "Posted today" → 2026-02-14 09:00:00
        """
        
        if not text:
            return datetime.now()
        
        text = text.lower().strip()
        now = datetime.now()
        
        # Pattern 1: "X hours ago"
        hours_match = re.search(r'(\d+)\s*hour', text)
        if hours_match:
            hours = int(hours_match.group(1))
            return now - timedelta(hours=hours)
        
        # Pattern 2: "X minutes ago"
        mins_match = re.search(r'(\d+)\s*min', text)
        if mins_match:
            mins = int(mins_match.group(1))
            return now - timedelta(minutes=mins)
        
        # Pattern 3: "X days ago"
        days_match = re.search(r'(\d+)\s*day', text)
        if days_match:
            days = int(days_match.group(1))
            return now - timedelta(days=days)
        
        # Pattern 4: "X weeks ago"
        weeks_match = re.search(r'(\d+)\s*week', text)
        if weeks_match:
            weeks = int(weeks_match.group(1))
            return now - timedelta(weeks=weeks)
        
        # Pattern 5: "Just posted" or "Posted today"
        if any(word in text for word in ['just', 'today', 'recent']):
            # Assume posted 2 hours ago (morning postings)
            return now - timedelta(hours=2)
        
        # Pattern 6: "Posted yesterday"
        if 'yesterday' in text:
            return now - timedelta(days=1)
        
        # Pattern 7: "30+ days ago"
        if '30+' in text or 'month' in text:
            return now - timedelta(days=30)
        
        # Default: assume posted today morning
        return now.replace(hour=9, minute=0, second=0)
    
    @staticmethod
    def format_datetime(dt):
        """
        Format datetime for Google Sheets
        Returns: (date_str, time_str)
        """
        date_str = dt.strftime('%d-%b-%Y')  # "14-Feb-2026"
        time_str = dt.strftime('%I:%M %p')  # "08:00 PM"
        
        return date_str, time_str


# Test
if __name__ == "__main__":
    parser = JobDateParser()
    
    test_cases = [
        "2 hours ago",
        "1 day ago",
        "Just posted",
        "Posted today",
        "3 weeks ago",
        "30+ days ago"
    ]
    
    print("="*70)
    print("DATE PARSER TEST")
    print("="*70)
    
    for test in test_cases:
        dt = parser.parse_relative_date(test)
        date_str, time_str = parser.format_datetime(dt)
        
        print(f"\n'{test}'")
        print(f"  → {date_str} at {time_str}")
# utils/job_deduplicator.py

from difflib import SequenceMatcher
import hashlib

class JobDeduplicator:
    """Detect and remove duplicate jobs from different sources"""
    
    def __init__(self):
        self.seen_jobs = set()  # Store hashes of seen jobs
    
    def is_duplicate(self, job):
        """
        Check if job is duplicate based on:
        1. Exact URL match
        2. Very similar title + company (>90% match)
        """
        
        # Method 1: Exact URL match
        if job.get('url') and job['url'].strip():
            url_hash = hashlib.md5(job['url'].encode()).hexdigest()
            if url_hash in self.seen_jobs:
                return True
            self.seen_jobs.add(url_hash)
        
        # Method 2: Title + Company match (stricter threshold)
        title = job.get('title', '').lower().strip()
        company = job.get('company', '').lower().strip()
        
        # Skip if title is too generic
        if not title or len(title) < 5 or title == 'unknown':
            return False
        
        # Create signature
        signature = f"{title}_{company}"
        signature_clean = ''.join(c for c in signature if c.isalnum())
        
        # Check against all seen (STRICTER: 0.95 instead of 0.85)
        for seen_sig in list(self.seen_jobs):
            if isinstance(seen_sig, str) and len(seen_sig) > 10:  # It's a signature, not hash
                similarity = self.similarity(signature_clean, seen_sig)
                if similarity > 0.95:  # CHANGED from 0.85 to 0.95
                    return True
        
        # Not duplicate - add to seen
        self.seen_jobs.add(signature_clean)
        
        return False
        
    def similarity(self, str1, str2):
        """Calculate similarity ratio between two strings"""
        return SequenceMatcher(None, str1, str2).ratio()
    
    def deduplicate_list(self, jobs):
        """Remove duplicates from a list of jobs"""
        unique_jobs = []
        
        for job in jobs:
            if not self.is_duplicate(job):
                unique_jobs.append(job)
        
        return unique_jobs


# Test
if __name__ == "__main__":
    jobs = [
        {'title': 'Data Analyst', 'company': 'Amazon', 'url': 'http://example.com/1'},
        {'title': 'Data Analyst', 'company': 'Amazon', 'url': 'http://example.com/1'},  # Duplicate URL
        {'title': 'Data Analyst at Amazon', 'company': 'Amazon Inc', 'url': 'http://example.com/2'},  # Similar
        {'title': 'Senior Data Analyst', 'company': 'Google', 'url': 'http://example.com/3'},  # Unique
    ]
    
    deduplicator = JobDeduplicator()
    unique = deduplicator.deduplicate_list(jobs)
    
    print(f"Original: {len(jobs)} jobs")
    print(f"After deduplication: {len(unique)} jobs")
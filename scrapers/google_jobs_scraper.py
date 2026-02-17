# scrapers/google_jobs_scraper.py - FIXED VERSION

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.salary_extractor import SalaryExtractor
from dotenv import load_dotenv

load_dotenv('config/.env')

class GoogleJobsScraper:
    def __init__(self,since_time=None):
        """Initialize Google search-based scraper"""
        self.jobs_found = []
        
        self.job_roles = os.getenv('JOB_ROLES', 'Data Analyst').split(',')
        self.min_salary = int(os.getenv('MIN_SALARY_LPA', 15))
        
        self.since_time = since_time
        print("✅ Google Jobs Scraper initialized (API-free)")
    
    def search_jobs(self):
        """Search using direct Google search URLs"""
        
        all_jobs = []
        
        for role in self.job_roles:
            role = role.strip()
            print(f"\n🔎 Searching Google for: {role}")
            
            # Build Google search URL
            query = f"{role} job India site:linkedin.com OR site:naukri.com"
            if self.since_time:
            # Calculate hours since last run
                from datetime import datetime
                now = datetime.now()
                hours_ago = int((now - self.since_time).total_seconds() / 3600)
                
                # LinkedIn time filters:
                # r86400 = last 24 hours
                # r604800 = last week
                # r2592000 = last month
                
                if hours_ago <= 24:
                    time_filter = 'r86400'  # Last 24 hours
                elif hours_ago <= 168:  # 7 days
                    time_filter = 'r604800'  # Last week
                else:
                    time_filter = 'r2592000'  # Last month
                
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={role}&location=India&sortBy=DD&f_TPR={time_filter}"
            else:
                # No filter - get recent jobs
                search_url = f"https://www.linkedin.com/jobs/search/?keywords={role}&location=India&sortBy=DD"
            
            
            try:
                # Make request with headers
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(search_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    
                    # Find all result links
                    links = soup.find_all('a', href=True)
                    
                    job_count = 0
                    for link in links:
                        href = link.get('href', '')
                        
                        # Filter job URLs
                        if any(site in href for site in ['linkedin.com/jobs', 'naukri.com']):
                            if href.startswith('/url?q='):
                                href = href.split('/url?q=')[1].split('&')[0]
                            
                            if href.startswith('http'):
                                job_data = {
                                    'date_found': datetime.now().strftime('%d-%b-%Y'),
                                    'time_found': datetime.now().strftime('%I:%M %p'),
                                    'company': 'Unknown',
                                    'title': f"{role} (via Google)",
                                    'salary': 'Not mentioned',
                                    'location': 'India',
                                    'portal': 'Google Search',
                                    'url': href,
                                    'description': '',
                                    'search_role': role
                                }
                                
                                all_jobs.append(job_data)
                                job_count += 1
                                
                                if job_count >= 5:  # Limit to 5 per role
                                    break
                    
                    print(f"   ✅ Found {job_count} job links")
                else:
                    print(f"   ⚠️  Google returned status {response.status_code}")
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:80]}")
        
        self.jobs_found = all_jobs
        print(f"\n🎯 Total Google Jobs: {len(all_jobs)}")
        return all_jobs
    
    def close(self):
        """No browser to close"""
        print("✅ Google Search scraper complete")


if __name__ == "__main__":
    scraper = GoogleJobsScraper()
    jobs = scraper.search_jobs()
    scraper.close()
    
    if jobs:
        print("\n📋 Sample jobs:")
        for job in jobs[:3]:
            print(f"  • {job['url'][:80]}")
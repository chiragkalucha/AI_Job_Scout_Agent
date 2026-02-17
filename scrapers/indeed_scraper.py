# scrapers/indeed_scraper.py

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.salary_extractor import SalaryExtractor
from dotenv import load_dotenv

load_dotenv('config/.env')

class IndeedScraper:
    def __init__(self,since_time=None):
        """Initialize Indeed RSS scraper"""
        self.jobs_found = []
        
        self.job_roles = os.getenv('JOB_ROLES', 'Data Analyst').split(',')
        self.min_salary = int(os.getenv('MIN_SALARY_LPA', 20))
        
        self.since_time = since_time
        print("✅ Indeed RSS Scraper initialized")
    
    def search_jobs(self):
        """Search using Indeed RSS feeds"""
        
        all_jobs = []
        
        for role in self.job_roles:
            role = role.strip()
            print(f"\n🔎 Searching Indeed RSS for: {role}")
            
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
                
                rss_url = f"https://www.linkedin.com/jobs/search/?keywords={role}&location=India&sortBy=DD&f_TPR={time_filter}"
            else:
                # No filter - get recent jobs
                rss_url = f"https://www.linkedin.com/jobs/search/?keywords={role}&location=India&sortBy=DD"
            
            try:
                # Parse RSS feed
                feed = feedparser.parse(rss_url)
                
                print(f"   Found {len(feed.entries)} jobs in RSS feed")
                
                if len(feed.entries) == 0:
                    # Try alternative URL
                    alt_url = f"https://www.indeed.co.in/rss?q={role.replace(' ', '+')}&l=&sort=date"
                    feed = feedparser.parse(alt_url)
                    print(f"   Trying alternative feed... Found {len(feed.entries)} jobs")
                
                for idx, entry in enumerate(feed.entries[:20], 1):
                    try:
                        job_data = self.extract_job_from_entry(entry, role)
                        
                        if job_data and SalaryExtractor.meets_criteria(job_data['salary'], self.min_salary):
                            all_jobs.append(job_data)
                            print(f"   ✅ {idx}. {job_data['title'][:40]} - {job_data['salary']}")
                        
                    except Exception as e:
                        print(f"   ⚠️  Error on job {idx}: {str(e)[:60]}")
                        continue
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}")
        
        self.jobs_found = all_jobs
        print(f"\n🎯 Total Indeed jobs: {len(all_jobs)}")
        return all_jobs
        
    def extract_job_from_entry(self, entry, search_role):
        """Extract job details from RSS entry"""
        
        # Title
        title = entry.title if hasattr(entry, 'title') else 'Unknown'
        
        # URL
        url = entry.link if hasattr(entry, 'link') else ''
        
        # Description
        description = entry.summary if hasattr(entry, 'summary') else ''
        
        # Parse description HTML
        soup = BeautifulSoup(description, 'html.parser')
        description_text = soup.get_text(strip=True, separator=' ')
        
        # Extract company from description
        company = 'Unknown'
        try:
            # Indeed RSS usually has company in <b> tag
            company_tag = soup.find('b')
            if company_tag:
                company = company_tag.text.strip()
        except:
            pass
        
        # Extract location
        location = 'India'
        try:
            location_match = soup.find(string=lambda text: text and (',' in text or 'India' in text))
            if location_match:
                location = location_match.strip()
        except:
            pass
        
        # Extract salary
        salary = SalaryExtractor.extract(description_text)
        
        # Published date
        published = entry.published if hasattr(entry, 'published') else datetime.now().strftime('%Y-%m-%d')
        
        return {
            'date_found': datetime.now().strftime('%Y-%m-%d'),
            'time_found': datetime.now().strftime('%H:%M:%S'),
            'company': company,
            'title': title,
            'salary': salary,
            'location': location,
            'portal': 'Indeed',
            'url': url,
            'description': description_text[:500],
            'published': published,
            'search_role': search_role
        }
    
    def close(self):
        """No browser to close"""
        print("✅ Indeed RSS scraper complete")


if __name__ == "__main__":
    scraper = IndeedScraper()
    jobs = scraper.search_jobs()
    
    print("\n📋 INDEED JOBS:")
    for idx, job in enumerate(jobs, 1):
        print(f"\n{idx}. {job['title']}")
        print(f"   {job['company']} | {job['salary']}")
        print(f"   {job['url'][:80]}...")
    
    scraper.close()
# scrapers/naukri_scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.salary_extractor import SalaryExtractor
from dotenv import load_dotenv

load_dotenv('config/.env')

class NaukriScraper:
    def __init__(self,since_time=None):
        """Initialize Naukri scraper in SILENT mode"""
        
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils.silent_browser import get_silent_driver
        
        self.driver = get_silent_driver()
        self.wait = WebDriverWait(self.driver, 10)
        self.jobs_found = []
        
        self.job_roles = os.getenv('JOB_ROLES', 'Data Analyst').split(',')
        self.min_salary = int(os.getenv('MIN_SALARY_LPA', 15))
        
        self.since_time = since_time
        print("✅ Naukri Scraper initialized (SILENT MODE)")
    
    def search_jobs(self):
        """Search for jobs on Naukri"""
        
        all_jobs = []
        
        for role in self.job_roles:
            role = role.strip()
            print(f"\n🔎 Searching Naukri for: {role}")
            
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
                self.driver.get(search_url)
                time.sleep(4)
                
                # Scroll to load more jobs
                for _ in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                
                # Find job cards
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'article.jobTuple')
                if not job_cards:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'div.srp-jobtuple-wrapper')

                
                print(f"   Found {len(job_cards)} job cards")
                
                for idx, card in enumerate(job_cards[:20], 1):
                    try:
                        job_data = self.extract_job_details(card, role)
                        
                        if job_data and SalaryExtractor.meets_criteria(job_data['salary'], self.min_salary):
                            all_jobs.append(job_data)
                            print(f"   ✅ {idx}. {job_data['title'][:40]} - {job_data['company'][:25]} - {job_data['salary']}")
                        else:
                            print(f"   ⏭️  {idx}. Salary below threshold or invalid")
                        
                    except Exception as e:
                        print(f"   ⚠️  Error on job {idx}: {str(e)[:60]}")
                        continue
                
            except Exception as e:
                print(f"   ❌ Error searching: {str(e)[:100]}")
        
        self.jobs_found = all_jobs
        print(f"\n🎯 Total Naukri jobs: {len(all_jobs)}")
        return all_jobs
    
    def extract_job_details(self, card, search_role):
        """Extract details from Naukri job card"""
        
        # Title
        try:
            title_elem = card.find_element(By.CSS_SELECTOR, 'a.title')
            title = title_elem.text.strip()
            url = title_elem.get_attribute('href')
        except:
            return None
        
        # Company
        try:
            company = card.find_element(By.CSS_SELECTOR, 'a.subTitle').text.strip()
        except:
            company = 'Unknown'
        
        # Experience
        try:
            experience = card.find_element(By.CSS_SELECTOR, 'span.expwdth').text.strip()
        except:
            experience = 'Not mentioned'
        
        # Salary
        try:
            salary_elem = card.find_element(By.CSS_SELECTOR, 'span.sal')
            salary_text = salary_elem.text.strip()
            salary = SalaryExtractor.extract(salary_text)
        except:
            salary = 'Not mentioned'
        
        # Location
        try:
            location = card.find_element(By.CSS_SELECTOR, 'span.loc').text.strip()
        except:
            location = 'India'
        
        # Job description (brief)
        try:
            desc = card.find_element(By.CSS_SELECTOR, 'div.job-description').text.strip()
        except:
            desc = ''
        
        # Posted date
        try:
            posted_elem = card.find_element(By.CSS_SELECTOR, 'span.sim-posted span')
            posted_text = posted_elem.text.strip()  # "Posted today", "Posted 2 days ago"
        except:
            posted_text = 'Posted today'

        # Parse it
        from utils.date_parser import JobDateParser
        parser = JobDateParser()
        posted_dt = parser.parse_relative_date(posted_text)
        date_str, time_str = parser.format_datetime(posted_dt)

        
        return {
            'date_found': date_str,
            'time_found': time_str,
            'company': company,
            'title': title,
            'salary': salary,
            'location': location,
            'portal': 'Naukri',
            'url': url,
            'description': desc,
            'experience': experience,
            'posted': posted_elem,
            'search_role': search_role
        }
    
    def close(self):
        """Close browser"""
        self.driver.quit()
        print("🔒 Naukri browser closed")


if __name__ == "__main__":
    scraper = NaukriScraper()
    jobs = scraper.search_jobs()
    
    print("\n📋 NAUKRI JOBS FOUND:")
    for idx, job in enumerate(jobs, 1):
        print(f"\n{idx}. {job['title']}")
        print(f"   {job['company']} | {job['salary']}")
        print(f"   {job['location']} | Posted: {job.get('posted', 'N/A')}")
        print(f"   {job['url'][:80]}...")
    
    scraper.close()
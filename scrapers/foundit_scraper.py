# scrapers/foundit_scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.salary_extractor import SalaryExtractor
from dotenv import load_dotenv

load_dotenv('config/.env')

class FounditScraper:
    def __init__(self,since_time=None):
        """Initialize Foundit scraper in SILENT mode"""
        
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils.silent_browser import get_silent_driver
        
        self.driver = get_silent_driver()
        self.jobs_found = []
        
        self.job_roles = os.getenv('JOB_ROLES', 'Data Analyst').split(',')
        self.min_salary = int(os.getenv('MIN_SALARY_LPA', 15))
        
        self.since_time = since_time
        print("✅ Foundit Scraper initialized (SILENT MODE)")
    
    def search_jobs(self):
        """Search for jobs on Foundit"""
        
        all_jobs = []
        
        for role in self.job_roles:
            role = role.strip()
            print(f"\n🔎 Searching Foundit for: {role}")
            
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
                time.sleep(5)
                
                # Scroll
                for _ in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                
                # Find job cards
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="jobCard"]')
                
                if not job_cards:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'article.job-result')
                
                print(f"   Found {len(job_cards)} job cards")
                
                for idx, card in enumerate(job_cards[:20], 1):
                    try:
                        job_data = self.extract_job_details(card, role)
                        
                        if job_data and SalaryExtractor.meets_criteria(job_data['salary'], self.min_salary):
                            all_jobs.append(job_data)
                            print(f"   ✅ {idx}. {job_data['title'][:40]} - {job_data['salary']}")
                        
                    except Exception as e:
                        print(f"   ⚠️  Error on job {idx}: {str(e)[:60]}")
                        continue
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}")
        
        self.jobs_found = all_jobs
        print(f"\n🎯 Total Foundit jobs: {len(all_jobs)}")
        return all_jobs
    
    def extract_job_details(self, card, search_role):
        """Extract details from Foundit job card"""
        
        # Title
        try:
            title_elem = card.find_element(By.CSS_SELECTOR, 'a[data-testid="job-title"]')
            title = title_elem.text.strip()
            url = title_elem.get_attribute('href')
        except:
            return None
        
        # Company
        try:
            company = card.find_element(By.CSS_SELECTOR, 'a[data-testid="company-name"]').text.strip()
        except:
            company = 'Unknown'
        
        # Salary
        try:
            salary_elem = card.find_element(By.CSS_SELECTOR, 'div[data-testid="salary"]')
            salary = SalaryExtractor.extract(salary_elem.text)
        except:
            salary = 'Not mentioned'
        
        # Location
        try:
            location = card.find_element(By.CSS_SELECTOR, 'div[data-testid="location"]').text.strip()
        except:
            location = 'India'
        
        # Experience
        try:
            experience = card.find_element(By.CSS_SELECTOR, 'div[data-testid="experience"]').text.strip()
        except:
            experience = 'Not mentioned'
        
        return {
            'date_found': datetime.now().strftime('%Y-%m-%d'),
            'time_found': datetime.now().strftime('%H:%M:%S'),
            'company': company,
            'title': title,
            'salary': salary,
            'location': location,
            'portal': 'Foundit',
            'url': url if url.startswith('http') else f"https://www.foundit.in{url}",
            'description': '',
            'experience': experience,
            'search_role': search_role
        }
    
    def close(self):
        """Close browser"""
        self.driver.quit()
        print("🔒 Foundit browser closed")


if __name__ == "__main__":
    scraper = FounditScraper()
    jobs = scraper.search_jobs()
    
    print("\n📋 FOUNDIT JOBS:")
    for idx, job in enumerate(jobs, 1):
        print(f"\n{idx}. {job['title']}")
        print(f"   {job['company']} | {job['salary']}")
    
    scraper.close()
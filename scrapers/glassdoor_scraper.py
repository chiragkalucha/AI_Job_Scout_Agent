# scrapers/glassdoor_scraper.py

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.salary_extractor import SalaryExtractor
from dotenv import load_dotenv

load_dotenv('config/.env')

class GlassdoorScraper:
    def __init__(self,since_time=None):
        """Initialize Glassdoor scraper in SILENT mode"""
        
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
        print("✅ Glassdoor Scraper initialized (SILENT MODE)")
    
    def search_jobs(self):
        """Search for jobs on Glassdoor"""
        
        all_jobs = []
        
        for role in self.job_roles:
            role = role.strip()
            print(f"\n🔎 Searching Glassdoor for: {role}")
            
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
                
                # Close popup if present
                try:
                    close_btn = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[alt="Close"]')))
                    close_btn.click()
                    time.sleep(1)
                except:
                    pass
                
                # Scroll to load jobs
                for _ in range(2):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                
                # Find job cards
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'li[data-test="jobListing"]')
                
                if not job_cards:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'div.JobsList_jobListItem__JBBUV')
                
                print(f"   Found {len(job_cards)} job cards")
                
                for idx, card in enumerate(job_cards[:15], 1):
                    try:
                        job_data = self.extract_job_details(card, role)
                        
                        if job_data and SalaryExtractor.meets_criteria(job_data['salary'], self.min_salary):
                            all_jobs.append(job_data)
                            print(f"   ✅ {idx}. {job_data['title'][:35]} - {job_data['salary']}")
                        
                    except Exception as e:
                        print(f"   ⚠️  Error on job {idx}: {str(e)[:60]}")
                        continue
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:100]}")
        
        self.jobs_found = all_jobs
        print(f"\n🎯 Total Glassdoor jobs: {len(all_jobs)}")
        return all_jobs
    
    def extract_job_details(self, card, search_role):
        """Extract details from Glassdoor job card"""
        
        # Click card to load details
        try:
            card.click()
            time.sleep(2)
        except:
            pass
        
        # Title and URL
        # FIXED: Better title extraction
        title = None
        url = None

        try:
            # Method 1: Direct link
            title_elem = card.find_element(By.CSS_SELECTOR, 'a[data-test="job-link"]')
            title = title_elem.text.strip()
            url = title_elem.get_attribute('href')
        except:
            try:
                # Method 2: Alternative selector
                title_elem = card.find_element(By.CSS_SELECTOR, 'a.JobCard_jobTitle__GLqEV')
                title = title_elem.text.strip()
                url = title_elem.get_attribute('href')
            except:
                try:
                    # Method 3: Get from card text
                    card_text = card.text.strip().split('\n')
                    if len(card_text) > 0:
                        title = card_text[0]
                except:
                    pass

        if not title or len(title) < 5:
            return None

        # Don't click card (causes issues), just use card data
                
        # Company
        try:
            company = card.find_element(By.CSS_SELECTOR, 'span[data-test="employer-name"]').text.strip()
        except:
            try:
                company = card.find_element(By.CSS_SELECTOR, 'div.EmployerProfile_employerName__Xemli').text.strip()
            except:
                company = 'Unknown'
        
        # Location
        try:
            location = card.find_element(By.CSS_SELECTOR, 'span[data-test="emp-location"]').text.strip()
        except:
            location = 'India'
        
        # Salary - try from card first, then from detail panel
        salary = 'Not mentioned'
        try:
            salary_elem = card.find_element(By.CSS_SELECTOR, 'span[data-test="detailSalary"]')
            salary = SalaryExtractor.extract(salary_elem.text)
        except:
            # Try from detail panel
            try:
                detail_salary = self.driver.find_element(By.CSS_SELECTOR, 'span.SalaryEstimate_salaryEstimate__vZYCr')
                salary = SalaryExtractor.extract(detail_salary.text)
            except:
                pass
        
        # Description from detail panel
        description = ''
        try:
            desc_elem = self.driver.find_element(By.CSS_SELECTOR, 'div.JobDetails_jobDescription__uW_fK')
            description = desc_elem.text.strip()
            
            # Extract salary from description if not found yet
            if salary == 'Not mentioned':
                salary = SalaryExtractor.extract(description)
        except:
            pass
        
        return {
            'date_found': datetime.now().strftime('%Y-%m-%d'),
            'time_found': datetime.now().strftime('%H:%M:%S'),
            'company': company,
            'title': title,
            'salary': salary,
            'location': location,
            'portal': 'Glassdoor',
            'url': f"https://www.glassdoor.co.in{url}" if not url.startswith('http') else url,
            'description': description,
            'search_role': search_role
        }
    
    def close(self):
        """Close browser"""
        self.driver.quit()
        print("🔒 Glassdoor browser closed")


if __name__ == "__main__":
    scraper = GlassdoorScraper()
    jobs = scraper.search_jobs()
    
    print("\n📋 GLASSDOOR JOBS FOUND:")
    for idx, job in enumerate(jobs, 1):
        print(f"\n{idx}. {job['title']}")
        print(f"   {job['company']} | {job['salary']}")
        print(f"   {job['url'][:80]}...")
    
    scraper.close()
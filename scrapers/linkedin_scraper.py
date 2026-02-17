# scrapers/linkedin_scraper.py - FIXED VERSION

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
import time
from datetime import datetime
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv('config/.env')

class LinkedInJobScraper:
    def __init__(self,since_time=None):
        """Initialize LinkedIn scraper in SILENT mode"""
        
        # Import silent browser
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from utils.silent_browser import get_silent_driver
        
        # Use silent driver
        self.driver = get_silent_driver()
        self.wait = WebDriverWait(self.driver, 10)
        self.jobs_found = []
        
        # Load filters
        self.job_roles = os.getenv('JOB_ROLES', 'Data Analyst').split(',')
        self.min_salary = int(os.getenv('MIN_SALARY_LPA', 15))
        
        self.since_time = since_time
        print("✅ LinkedIn Scraper initialized (SILENT MODE - no windows)")
    def check_login_status(self):
        """Check if user is logged in"""
        
        self.driver.get("https://www.linkedin.com")
        time.sleep(3)
        
        # Check if we're on login page
        if "login" in self.driver.current_url or "authwall" in self.driver.current_url:
            print("\n⚠️  LinkedIn login required!")
            print("   A browser window is open.")
            print("   Please login manually, then press ENTER here.\n")
            
            input("Press ENTER after logging in...")
            
            print("✅ Login successful! Session saved for future use.")
    def search_jobs(self):
        """Search for jobs on LinkedIn"""
        
        all_jobs = []
        
        for role in self.job_roles:
            role = role.strip()
            print(f"\n🔎 Searching LinkedIn for: {role}")
            
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
                print("   ⏳ Loading page...")
                time.sleep(5)  # Wait for page to fully load
                
                # Handle "See more jobs" button if present
                try:
                    see_more_btn = self.driver.find_element(By.CSS_SELECTOR, "button[aria-label='See more jobs']")
                    see_more_btn.click()
                    time.sleep(2)
                except:
                    pass  # Button not present or already expanded
                
                # Scroll to load more jobs
                print("   📜 Scrolling to load jobs...")
                for i in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    print(f"      Scroll {i+1}/3")
                
                # FIXED: Use different selectors that work better
                job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'div.base-card')
                
                if not job_cards:
                    # Try alternative selector
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'li.jobs-search-results__list-item')
                
                print(f"   Found {len(job_cards)} job cards")
                
                if len(job_cards) == 0:
                    print("   ⚠️  No job cards found. Saving screenshot for debugging...")
                    self.driver.save_screenshot('logs/linkedin_debug.png')
                    print("   📸 Screenshot saved to logs/linkedin_debug.png")
                
                for idx, card in enumerate(job_cards[:20], 1):  # Limit to 20 per role
                    try:
                        # FIXED: Better element extraction with multiple fallbacks
                        job_data = self.extract_job_details(card, idx, role)
                        
                        if job_data:
                            # Filter by salary
                            if self.meets_salary_criteria(job_data['salary']):
                                all_jobs.append(job_data)
                                print(f"   ✅ Job {idx}: {job_data['title'][:50]} at {job_data['company'][:30]} - {job_data['salary']}")
                            else:
                                print(f"   ⏭️  Job {idx}: {job_data['title'][:50]} - Salary too low or not mentioned")
                        
                    except Exception as e:
                        print(f"   ⚠️  Error parsing job card {idx}: {str(e)[:100]}")
                        continue
                
            except Exception as e:
                print(f"   ❌ Error searching for {role}: {str(e)[:150]}")
                continue
        
        self.jobs_found = all_jobs
        print(f"\n🎯 Total jobs found matching criteria: {len(all_jobs)}")
        return all_jobs
    
    def extract_job_details(self, card, idx, search_role):
    
    
        job_data = {
            'date_found': datetime.now().strftime('%Y-%m-%d'),
            'time_found': datetime.now().strftime('%H:%M:%S'),
            'company': 'Unknown',
            'title': 'Unknown',
            'salary': 'Not mentioned',
            'location': 'Unknown',
            'portal': 'LinkedIn',
            'url': '',
            'description': '',
            'search_role': search_role
        }
        
        try:
            # FIXED: Better title extraction with multiple selectors
            title = None
            try:
                # Try method 1
                title_elem = card.find_element(By.CSS_SELECTOR, 'h3.base-search-card__title')
                title = title_elem.text.strip()
            except:
                try:
                    # Try method 2
                    title_elem = card.find_element(By.CSS_SELECTOR, 'a.base-card__full-link')
                    title = title_elem.get_attribute('aria-label')
                    if title and ' at ' in title:
                        title = title.split(' at ')[0].strip()
                except:
                    try:
                        # Try method 3 - get all text and take first line
                        all_text = card.text.strip().split('\n')
                        if len(all_text) > 0:
                            title = all_text[0]
                    except:
                        pass
            
            if not title or len(title) < 5:
                return None
            
            job_data['title'] = title
            
            # FIXED: Better company extraction
            company = 'Unknown'
            try:
                company_elem = card.find_element(By.CSS_SELECTOR, 'h4.base-search-card__subtitle')
                company = company_elem.text.strip()
            except:
                try:
                    company_elem = card.find_element(By.CSS_SELECTOR, 'a.hidden-nested-link')
                    company = company_elem.text.strip()
                except:
                    # Get from text - usually second line
                    all_text = card.text.strip().split('\n')
                    if len(all_text) > 1:
                        company = all_text[1]
            
            job_data['company'] = company if company else 'Unknown'
            
            # Location
            try:
                location_elem = card.find_element(By.CSS_SELECTOR, 'span.job-search-card__location')
                job_data['location'] = location_elem.text.strip()
            except:
                pass
            
            # URL - CRITICAL
            try:
                url_elem = card.find_element(By.CSS_SELECTOR, 'a.base-card__full-link')
                url = url_elem.get_attribute('href')
                if url and '?' in url:
                    url = url.split('?')[0]
                job_data['url'] = url
            except:
                pass
            
            # SKIP opening job page for now (too slow)
            # Just use card data
            
            return job_data
            
        except Exception as e:
            print(f"      ⚠️  Extraction error: {str(e)[:60]}")
            return None
        posted_text = 'Unknown'
        try:
            # LinkedIn shows posted date in various places
            posted_elem = card.find_element(By.CSS_SELECTOR, 'time.job-search-card__listdate')
            posted_text = posted_elem.get_attribute('datetime')  # ISO format
            
            if not posted_text:
                # Try alternative: text format
                posted_elem = card.find_element(By.CSS_SELECTOR, 'time')
                posted_text = posted_elem.text  # "2 hours ago"
        except:
            # Try another selector
            try:
                posted_elem = card.find_element(By.XPATH, ".//time")
                posted_text = posted_elem.text
            except:
                posted_text = 'Just posted'  # Default
        
        # Parse the posted date
        from utils.date_parser import JobDateParser
        parser = JobDateParser()
        posted_dt = parser.parse_relative_date(posted_text)
        date_str, time_str = parser.format_datetime(posted_dt)
        
        return {
            'date_found': date_str,  # Real posting date!
            'time_found': time_str,  # Real posting time!
            'company': company,
            'title': title,
            'salary': salary,
            'location': location,
            'portal': 'LinkedIn',
            'url': url,
            'description': description,
            'search_role': search_role,
            'posted_raw': posted_text  # Keep original for debugging
        }
        
    def extract_salary(self, text):
        """Extract salary from job description"""
        
        if not text:
            return "Not mentioned"
        
        # Pattern 1: "20-25 LPA" or "20-25 Lakhs"
        pattern1 = r'(\d+)\s*-\s*(\d+)\s*(?:LPA|Lakhs|Lacs|L\.?P\.?A\.?)'
        match1 = re.search(pattern1, text, re.IGNORECASE)
        if match1:
            min_sal = int(match1.group(1))
            max_sal = int(match1.group(2))
            return f"{min_sal}-{max_sal} LPA"
        
        # Pattern 2: "₹20-25 Lakhs" or "INR 20-25 Lakhs"
        pattern2 = r'(?:₹|INR|Rs\.?)\s*(\d+)\s*-\s*(\d+)\s*(?:Lakhs?|Lacs?|LPA)'
        match2 = re.search(pattern2, text, re.IGNORECASE)
        if match2:
            min_sal = int(match2.group(1))
            max_sal = int(match2.group(2))
            return f"{min_sal}-{max_sal} LPA"
        
        # Pattern 3: "Up to 30 LPA"
        pattern3 = r'(?:up to|upto)\s*(\d+)\s*(?:LPA|Lakhs|Lacs)'
        match3 = re.search(pattern3, text, re.IGNORECASE)
        if match3:
            max_sal = int(match3.group(1))
            return f"Up to {max_sal} LPA"
        
        # Pattern 4: Just "25 LPA" or "25 Lakhs"
        pattern4 = r'(?:^|\s)(\d+)\s*(?:LPA|Lakhs|Lacs)(?:\s|$)'
        match4 = re.search(pattern4, text, re.IGNORECASE)
        if match4:
            salary = int(match4.group(1))
            return f"{salary} LPA"
        
        # Pattern 5: "2000000-2500000" (in numbers)
        pattern5 = r'(\d{7,8})\s*-\s*(\d{7,8})'
        match5 = re.search(pattern5, text)
        if match5:
            min_sal = int(match5.group(1)) // 100000
            max_sal = int(match5.group(2)) // 100000
            return f"{min_sal}-{max_sal} LPA"
        
        return "Not mentioned"
    
    def meets_salary_criteria(self, salary_str):
        """Check if salary meets minimum criteria"""
        if salary_str == "Not mentioned":
            return True  # Include for manual review (AI will analyze)
        
        numbers = re.findall(r'\d+', salary_str)
        if numbers:
            # Take the minimum salary mentioned
            min_salary = int(numbers[0])
            return min_salary >= self.min_salary
        
        return True  # If can't determine, include it
    
    def close(self):
        """Close the browser"""
        self.driver.quit()
        print("🔒 Browser closed")


# Run if executed directly (for testing)
if __name__ == "__main__":
    print("=" * 60)
    print("LINKEDIN JOB SCRAPER - TEST RUN")
    print("=" * 60)
    
    scraper = LinkedInJobScraper()
    
    try:
        jobs = scraper.search_jobs()
        
        print("\n" + "=" * 60)
        print("📋 JOBS FOUND SUMMARY")
        print("=" * 60)
        
        if jobs:
            for idx, job in enumerate(jobs, 1):
                print(f"\n🔷 JOB {idx}:")
                print(f"   Title: {job['title']}")
                print(f"   Company: {job['company']}")
                print(f"   Salary: {job['salary']}")
                print(f"   Location: {job['location']}")
                print(f"   URL: {job['url'][:80]}...")
                print(f"   Description length: {len(job['description'])} chars")
        else:
            print("\n⚠️  No jobs found matching criteria.")
            print("\n🔍 TROUBLESHOOTING:")
            print("   1. Check internet connection")
            print("   2. Look at screenshot: logs/linkedin_debug.png")
            print("   3. LinkedIn might be blocking automated access")
            print("   4. Try running again after 5 minutes")
            
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\n⏳ Waiting 5 seconds before closing browser...")
        time.sleep(5)
        scraper.close()
        print("\n✅ Test complete!")
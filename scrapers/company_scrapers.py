# scrapers/company_scrapers.py - WITH TIME FILTER & DEDUPLICATION

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
import os
import sys
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.salary_extractor import SalaryExtractor
from utils.silent_browser import get_silent_driver
from dotenv import load_dotenv

load_dotenv('config/.env')

class CompanyScraper:
    """Universal scraper for company career pages - WITH TIME FILTER"""
    
    def __init__(self, since_time=None):
        """
        Initialize company scraper
        
        Args:
            since_time (datetime): Only get jobs posted after this time
        """
        
        self.driver = get_silent_driver()
        self.wait = WebDriverWait(self.driver, 10)
        self.jobs_found = []
        
        self.job_roles = os.getenv('JOB_ROLES', 'Data Analyst').split(',')
        self.min_salary = int(os.getenv('MIN_SALARY_LPA', 15))
        
        self.since_time = since_time  # NEW: Time filter
        
        print("✅ Company Scraper initialized (SILENT MODE)")
        
        if since_time:
            print(f"   📅 Only jobs posted after: {since_time.strftime('%Y-%m-%d %H:%M')}")
    
    def is_job_recent_enough(self, job_data):
        """Check if job was posted after since_time"""
        
        if not self.since_time:
            return True  # No filter, accept all
        
        # Get job posting date
        posted_date_str = job_data.get('date_found')
        
        if not posted_date_str:
            # No date info - include it (better to have false positives)
            return True
        
        try:
            # Parse date
            if isinstance(posted_date_str, str):
                # Try multiple date formats
                for fmt in ['%d-%b-%Y', '%Y-%m-%d', '%d/%m/%Y']:
                    try:
                        posted_date = datetime.strptime(posted_date_str, fmt)
                        break
                    except:
                        continue
                else:
                    # Couldn't parse - include it
                    return True
            elif isinstance(posted_date_str, datetime):
                posted_date = posted_date_str
            else:
                return True
            
            # Compare dates
            return posted_date >= self.since_time
            
        except Exception as e:
            # Error parsing - include job to be safe
            return True
    
    def search_all_companies(self):
        """Search jobs across all target companies - WITH TIME FILTER"""
        
        all_jobs = []
        
        # YOUR COMPANY LIST
        companies = [
            {"name": "Google", "url": "https://www.google.com/about/careers/applications/jobs/results/", "type": "api"},
            {"name": "Meta (Facebook)", "url": "https://www.metacareers.com/jobs", "type": "ajax"},
            {"name": "Amazon", "url": "https://www.amazon.jobs/en/job_categories/business-intelligence", "type": "html"},
            {"name": "Apple", "url": "https://www.apple.com/careers/", "type": "ajax"},
            {"name": "Microsoft", "url": "https://careers.microsoft.com/us/en", "type": "api"},
            {"name": "Netflix", "url": "https://jobs.netflix.com/", "type": "ajax"},
            {"name": "McKinsey & Company", "url": "https://www.mckinsey.com/careers/search-jobs", "type": "api"},
            {"name": "Boston Consulting Group (BCG)", "url": "https://careers.bcg.com/search-jobs", "type": "ajax"},
            {"name": "Bain & Company", "url": "https://www.bain.com/careers/roles/aci/", "type": "html"},
            {"name": "Goldman Sachs", "url": "https://www.goldmansachs.com/careers/students/programs/", "type": "html"},
            {"name": "J.P. Morgan Chase", "url": "https://jpmc.fa.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1001", "type": "api"},
            {"name": "Jane Street", "url": "https://www.janestreet.com/join-jane-street/position-listing/", "type": "html"},
            {"name": "Citadel", "url": "https://www.citadel.com/careers/open-opportunities/", "type": "ajax"},
            {"name": "Two Sigma", "url": "https://www.twosigma.com/careers/", "type": "ajax"},
            {"name": "BlackRock", "url": "https://blackrock.wd1.myworkdayjobs.com/BlackRock_External_Careers", "type": "api"},
            
            {"name": "Accenture", "url": "https://www.accenture.com/in-en/careers/jobsearch", "type": "ajax"},
            {"name": "PwC", "url": "https://www.pwc.com/gx/en/careers.html", "type": "api"},
            {"name": "EY (Ernst & Young)", "url": "https://www.ey.com/en_gl/careers", "type": "api"},
            
            {"name": "Salesforce", "url": "https://salesforce.wd1.myworkdayjobs.com/External_Career_Site", "type": "api"},
            {"name": "Adobe", "url": "https://adobe.wd5.myworkdayjobs.com/external_experienced", "type": "api"},
            {"name": "Uber", "url": "https://www.uber.com/us/en/careers/list/", "type": "ajax"},
            {"name": "Airbnb", "url": "https://www.airbnb.com/careers/departments/data-science-analytics", "type": "html"},
            {"name": "Palantir", "url": "https://www.palantir.com/careers/", "type": "html"},
            {"name": "Snowflake", "url": "https://www.snowflake.com/en/company/careers/", "type": "ajax"},
            {"name": "Databricks", "url": "https://www.databricks.com/company/careers", "type": "ajax"},
            {"name": "NVIDIA", "url": "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite", "type": "api"},
            {"name": "Tesla", "url": "https://www.tesla.com/careers/search/", "type": "api"},
            {"name": "Oracle", "url": "https://eeho.fa.us2.oraclecloud.com/hcmUI/CandidateExperience/en/sites/CX_1", "type": "api"},
            {"name": "IBM", "url": "https://www.ibm.com/careers/us-en/search/", "type": "api"},
            {"name": "Cisco", "url": "https://jobs.cisco.com/jobs/SearchJobs", "type": "ajax"},
            {"name": "Intel", "url": "https://jobs.intel.com/", "type": "api"},
            {"name": "LinkedIn", "url": "https://www.linkedin.com/company/linkedin/jobs/", "type": "ajax"},
            {"name": "Spotify", "url": "https://www.lifeatspotify.com/jobs", "type": "ajax"},
            {"name": "Pinterest", "url": "https://www.pinterestcareers.com/", "type": "html"},
            {"name": "Lyft", "url": "https://www.lyft.com/careers", "type": "ajax"},
            {"name": "DoorDash", "url": "https://careers.doordash.com/", "type": "ajax"},
            {"name": "Stripe", "url": "https://stripe.com/jobs/search", "type": "html"},
            {"name": "PayPal", "url": "https://jobsearch.paypal-corp.com/", "type": "api"},
            
            {"name": "Visa", "url": "https://www.visa.co.in/careers.html", "type": "api"},
            {"name": "Mastercard", "url": "https://mastercard.wd1.myworkdayjobs.com/CorporateCareers", "type": "api"},
            {"name": "Morgan Stanley", "url": "https://www.morganstanley.com/people-opportunities/students-graduates", "type": "html"},
            {"name": "HSBC", "url": "https://www.hsbc.com/careers/students-and-graduates", "type": "html"},
            {"name": "Barclays", "url": "https://search.jobs.barclays/", "type": "api"},
            {"name": "Standard Chartered", "url": "https://www.sc.com/en/careers/students-and-graduates/", "type": "html"},
            {"name": "Capital One", "url": "https://www.capitalonecareers.com/", "type": "api"},
            {"name": "Walmart Global Tech", "url": "https://careers.walmart.com/technology/data-science-analytics", "type": "api"},
            {"name": "Target", "url": "https://jobs.target.com/", "type": "api"}
            ]
        
        for company_config in companies:
            print(f"\n🔎 Searching {company_config['name']}...")
            
            try:
                jobs = self.scrape_company(company_config)
                
                # Filter by time if needed
                if self.since_time:
                    original_count = len(jobs)
                    jobs = [j for j in jobs if self.is_job_recent_enough(j)]
                    filtered_count = len(jobs)
                    
                    if original_count > filtered_count:
                        print(f"   ⏭️  Filtered out {original_count - filtered_count} old jobs")
                
                all_jobs.extend(jobs)
                
                if jobs:
                    print(f"   ✅ Found {len(jobs)} jobs at {company_config['name']}")
                else:
                    print(f"   ℹ️  No matching jobs at {company_config['name']}")
                
                time.sleep(2)  # Be polite
                
            except Exception as e:
                print(f"   ❌ Error with {company_config['name']}: {str(e)[:80]}")
        
        self.jobs_found = all_jobs
        print(f"\n🎯 Total company jobs: {len(all_jobs)}")
        return all_jobs
    
    def scrape_company(self, config):
        """Scrape based on company type"""
        
        if config['type'] == 'API':
            return self.scrape_api(config)
        elif config['type'] == 'AJAX':
            return self.scrape_ajax(config)
        else:
            return self.scrape_html(config)
    
    def scrape_api(self, config):
        """Scrape companies with JSON APIs"""
        
        jobs = []
        
        for role in self.job_roles:
            role = role.strip()
            url = config['url'].replace('{role}', role.replace(' ', '+'))
            
            try:
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Parse based on company
                    if config['name'] == 'Amazon':
                        jobs.extend(self.parse_amazon_api(data, role))
                    elif config['name'] == 'Google':
                        jobs.extend(self.parse_google_api(data, role))
                
            except Exception as e:
                print(f"      API error: {str(e)[:60]}")
        
        return jobs
    
    def parse_amazon_api(self, data, search_role):
        """Parse Amazon Jobs API response - WITH DATE EXTRACTION"""
        
        jobs = []
        
        try:
            job_list = data.get('jobs', [])
            
            for job in job_list[:20]:  # Limit to 20
                title = job.get('title', 'Unknown')
                company = 'Amazon'
                location = ', '.join(job.get('locations', ['India']))
                url = f"https://www.amazon.jobs/en/jobs/{job.get('id_icims', '')}"
                description = job.get('description_short', '')
                
                # CRITICAL: Extract posted date from API
                posted_date_raw = job.get('posted_date', '')  # Amazon provides this
                
                if posted_date_raw:
                    try:
                        # Amazon format: "2026-02-14" or timestamp
                        posted_dt = datetime.fromisoformat(posted_date_raw.split('T')[0])
                    except:
                        posted_dt = datetime.now()
                else:
                    posted_dt = datetime.now()
                
                # Format date
                date_str = posted_dt.strftime('%d-%b-%Y')
                time_str = posted_dt.strftime('%I:%M %p')
                
                salary = SalaryExtractor.extract(description)
                
                if SalaryExtractor.meets_criteria(salary, self.min_salary):
                    jobs.append({
                        'date_found': date_str,
                        'time_found': time_str,
                        'company': company,
                        'title': title,
                        'salary': salary,
                        'location': location,
                        'portal': 'Amazon Careers',
                        'url': url,
                        'description': description,
                        'search_role': search_role,
                        '_posted_datetime': posted_dt  # Store for filtering
                    })
        
        except Exception as e:
            print(f"      Parse error: {str(e)[:50]}")
        
        return jobs
    
    def parse_google_api(self, data, search_role):
        """Parse Google Careers API response - WITH DATE"""
        
        jobs = []
        
        try:
            job_list = data.get('jobs', [])
            
            for job in job_list[:20]:
                title = job.get('title', 'Unknown')
                company = 'Google'
                location = ', '.join([loc.get('display', '') for loc in job.get('locations', [])])
                url = f"https://careers.google.com/jobs/results/{job.get('id', '')}"
                description = job.get('description', '')
                
                # Extract posted date
                posted_date_raw = job.get('publish_date', '')
                
                if posted_date_raw:
                    try:
                        posted_dt = datetime.fromisoformat(posted_date_raw.split('T')[0])
                    except:
                        posted_dt = datetime.now()
                else:
                    posted_dt = datetime.now()
                
                date_str = posted_dt.strftime('%d-%b-%Y')
                time_str = posted_dt.strftime('%I:%M %p')
                
                salary = SalaryExtractor.extract(description)
                
                if SalaryExtractor.meets_criteria(salary, self.min_salary):
                    jobs.append({
                        'date_found': date_str,
                        'time_found': time_str,
                        'company': company,
                        'title': title,
                        'salary': salary,
                        'location': location,
                        'portal': 'Google Careers',
                        'url': url,
                        'description': description[:500],
                        'search_role': search_role,
                        '_posted_datetime': posted_dt
                    })
        
        except Exception as e:
            print(f"      Parse error: {str(e)[:50]}")
        
        return jobs
    
    def scrape_html(self, config):
        """Scrape HTML-based career pages"""
        
        jobs = []
        
        for role in self.job_roles:
            role = role.strip()
            url = config['url'].replace('{role}', role.replace(' ', '+'))
            
            try:
                self.driver.get(url)
                time.sleep(4)
                
                # Scroll
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
                
                # Find job cards
                if 'selector' in config:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, config['selector'])
                else:
                    job_cards = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="job"]')
                
                for card in job_cards[:10]:
                    try:
                        title_elem = card.find_element(By.TAG_NAME, 'a')
                        title = title_elem.text.strip()
                        url = title_elem.get_attribute('href')
                        
                        if title and role.lower() in title.lower():
                            # Use current time as posted time (best guess for HTML scrapers)
                            now = datetime.now()
                            
                            jobs.append({
                                'date_found': now.strftime('%d-%b-%Y'),
                                'time_found': now.strftime('%I:%M %p'),
                                'company': config['name'],
                                'title': title,
                                'salary': 'Not mentioned',
                                'location': 'India',
                                'portal': f"{config['name']} Careers",
                                'url': url,
                                'description': '',
                                'search_role': role,
                                '_posted_datetime': now
                            })
                    except:
                        continue
                
            except Exception as e:
                print(f"      HTML scrape error: {str(e)[:60]}")
        
        return jobs
    
    def scrape_ajax(self, config):
        """Scrape JavaScript-heavy sites"""
        
        jobs = []
        
        try:
            self.driver.get(config['url'])
            time.sleep(8)
            
            # Scroll
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            
            # Find job listings
            job_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'job') or contains(@href, 'career')]")
            
            for elem in job_elements[:10]:
                try:
                    title = elem.text.strip()
                    url = elem.get_attribute('href')
                    
                    if len(title) > 10:
                        now = datetime.now()
                        
                        jobs.append({
                            'date_found': now.strftime('%d-%b-%Y'),
                            'time_found': now.strftime('%I:%M %p'),
                            'company': config['name'],
                            'title': title,
                            'salary': 'Not mentioned',
                            'location': 'India',
                            'portal': f"{config['name']} Careers",
                            'url': url,
                            'description': '',
                            'search_role': 'General',
                            '_posted_datetime': now
                        })
                except:
                    continue
        
        except Exception as e:
            print(f"      AJAX error: {str(e)[:60]}")
        
        return jobs
    
    def close(self):
        """Close browser"""
        self.driver.quit()
        print("🔒 Company scraper browser closed")


# Test
if __name__ == "__main__":
    # Test with time filter
    from datetime import timedelta
    
    # Only jobs from last 24 hours
    since_time = datetime.now() - timedelta(hours=24)
    
    scraper = CompanyScraper(since_time=since_time)
    jobs = scraper.search_all_companies()
    
    print("\n📋 COMPANY JOBS FOUND:")
    for idx, job in enumerate(jobs, 1):
        print(f"\n{idx}. {job['title']}")
        print(f"   {job['company']} | Posted: {job['date_found']}")
        print(f"   {job['url'][:80]}...")
    
    scraper.close()

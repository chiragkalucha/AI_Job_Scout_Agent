# orchestrator.py - THE MASTER CONTROLLER - FIXED VERSION

import sys
import os
from datetime import datetime
import time

# Add scrapers to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scrapers.linkedin_scraper import LinkedInJobScraper
from scrapers.naukri_scraper import NaukriScraper
from scrapers.glassdoor_scraper import GlassdoorScraper
from scrapers.foundit_scraper import FounditScraper
from scrapers.indeed_scraper import IndeedScraper
from scrapers.google_jobs_scraper import GoogleJobsScraper

from scrapers.company_scrapers import CompanyScraper

from utils.job_deduplicator import JobDeduplicator
from dotenv import load_dotenv

load_dotenv('config/.env')

class JobScrapingOrchestrator:
    """Master controller for all job scrapers"""
    
    def __init__(self, since_time=None):
        print("=" * 70)
        print("AI JOB SCOUT - HYBRID SCRAPING SYSTEM")
        print("=" * 70)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        if since_time:
            print(f"⏰ Time filter: Jobs posted after {since_time.strftime('%Y-%m-%d %H:%M')}")
        
        print()
        
        self.all_jobs = []
        self.deduplicator = JobDeduplicator()
        self.since_time = since_time  # ✅ CRITICAL FIX - ADD THIS LINE!
        
        # Configuration
        self.enable_scrapers = True
        self.enable_companies = True
    
    def run_all_scrapers(self):
        """Execute all scrapers in priority order"""
        
        # TIER 2: JOB AGGREGATORS (10-15 min delay)
        if self.enable_scrapers:
            print("\n" + "="*70)
            print("TIER 2: JOB PORTALS (Medium Priority)")
            print("="*70)
            
            # Run in parallel-ish fashion (one after another)
            scrapers = [
                ("LinkedIn", LinkedInJobScraper),
                ("Naukri", NaukriScraper),
                ("Indeed", IndeedScraper),
                ("Glassdoor", GlassdoorScraper),
                ("Foundit", FounditScraper),
                # ("Google Jobs", GoogleJobsScraper),  # ✅ DISABLED - has issues
            ]
            
            for name, ScraperClass in scrapers:
                try:
                    print(f"\n▶️  Running {name} scraper...")
                    
                    # ✅ FIXED - Proper since_time handling with fallback
                    try:
                        if self.since_time:
                            scraper = ScraperClass(since_time=self.since_time)
                        else:
                            scraper = ScraperClass()
                    except TypeError as e:
                        # Scraper doesn't support since_time yet - use without it
                        print(f"   ⚠️  {name} doesn't support time filter (using all jobs)")
                        scraper = ScraperClass()
                    
                    jobs = scraper.search_jobs()
                    scraper.close()
                    
                    self.all_jobs.extend(jobs)
                    print(f"✅ {name} complete: {len(jobs)} jobs")
                    
                    time.sleep(2)  # Delay between scrapers
                    
                except Exception as e:
                    print(f"❌ {name} failed: {str(e)[:100]}")
            
            print(f"\n✅ Portal tier complete: {len(self.all_jobs)} total jobs so far")
        
        # TIER 3: COMPANY CAREER PAGES (30-45 min delay)
        if self.enable_companies:
            print("\n" + "="*70)
            print("TIER 3: COMPANY CAREER PAGES (Bonus)")
            print("="*70)
            
            try:
                # ✅ FIXED - Pass since_time to company scraper with fallback
                try:
                    if self.since_time:
                        company_scraper = CompanyScraper(since_time=self.since_time)
                    else:
                        company_scraper = CompanyScraper()
                except TypeError:
                    print(f"   ⚠️  Company scraper doesn't support time filter")
                    company_scraper = CompanyScraper()
                
                company_jobs = company_scraper.search_all_companies()
                company_scraper.close()
                
                self.all_jobs.extend(company_jobs)
                print(f"✅ Company tier complete: {len(company_jobs)} jobs")
                
            except Exception as e:
                print(f"❌ Company scraping failed: {str(e)[:100]}")
        
        # DEDUPLICATION
        print("\n" + "="*70)
        print("DEDUPLICATION")
        print("="*70)
        
        print(f"Before deduplication: {len(self.all_jobs)} jobs")
        unique_jobs = self.deduplicator.deduplicate_list(self.all_jobs)
        print(f"After deduplication: {len(unique_jobs)} unique jobs")
        
        # EXPERIENCE FILTERING
        print("\n" + "="*70)
        print("EXPERIENCE FILTERING (0-2 Years)")
        print("="*70)

        from utils.job_filter import JobFilter

        filtered_jobs = []

        for job in unique_jobs:
            suitable, reason = JobFilter.is_suitable_for_fresher(job)
            
            if suitable:
                # If no salary mentioned, estimate or verify it
                if job.get('salary') == 'Not mentioned':
                    company = job.get('company', '')
                    
                    # Try static estimate first (faster)
                    estimated = JobFilter.estimate_fresher_salary(company, role="Data Analyst")
                    
                    if estimated and estimated >= 15:
                        job['salary'] = f"Est. {estimated} LPA"
                        job['salary_estimated'] = True
                        filtered_jobs.append(job)
                        print(f"   ✅ {job['title'][:40]} at {company[:20]} - Est. {estimated} LPA")
                    else:
                        # Try AI verification for unknown companies
                        try:
                            estimated = JobFilter.verify_unknown_company_salary(company, role="Data Analyst", min_lpa=15)
                            
                            if estimated and estimated >= 15:
                                job['salary'] = f"Est. {estimated} LPA (AI-verified)"
                                job['salary_estimated'] = True
                                filtered_jobs.append(job)
                                print(f"   ✅ {job['title'][:40]} at {company[:20]} - AI-verified: {estimated} LPA")
                            else:
                                print(f"   ⏭️  {job['title'][:40]} at {company[:20]} - Below threshold")
                        except Exception as e:
                            # AI verification failed - skip job
                            print(f"   ❌ {job['title'][:40]} - Verification failed")
                else:
                    # Salary mentioned, include
                    filtered_jobs.append(job)
                    print(f"   ✅ {job['title'][:40]} at {job['company'][:20]} - {job['salary']}")
            else:
                print(f"   ❌ {job['title'][:40]} - {reason}")

        print(f"\nFiltered: {len(unique_jobs)} → {len(filtered_jobs)} fresher-suitable jobs")

        self.all_jobs = filtered_jobs
        
        return self.all_jobs
    
    def save_results(self):
        """Save all jobs to file"""
        
        if not self.all_jobs:
            print("\n⚠️  No jobs found to save")
            return
        
        # Save to JSON
        output_file = f"logs/jobs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        import json
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_jobs, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_file}")
    
    def display_summary(self):
        """Display summary of findings"""
        
        print("\n" + "="*70)
        print("SCRAPING SUMMARY")
        print("="*70)
        
        print(f"\n📊 Total unique jobs found: {len(self.all_jobs)}")
        
        if self.all_jobs:
            # Group by portal
            by_portal = {}
            for job in self.all_jobs:
                portal = job.get('portal', 'Unknown')
                by_portal[portal] = by_portal.get(portal, 0) + 1
            
            print("\n📍 Jobs by portal:")
            for portal, count in sorted(by_portal.items(), key=lambda x: x[1], reverse=True):
                print(f"   {portal}: {count} jobs")
            
            # Group by company
            by_company = {}
            for job in self.all_jobs:
                company = job.get('company', 'Unknown')
                by_company[company] = by_company.get(company, 0) + 1
            
            print("\n🏢 Top 10 companies:")
            top_companies = sorted(by_company.items(), key=lambda x: x[1], reverse=True)[:10]
            for company, count in top_companies:
                print(f"   {company}: {count} jobs")
            
            # Salary breakdown
            with_salary = sum(1 for job in self.all_jobs if job.get('salary') != 'Not mentioned')
            print(f"\n💰 Jobs with salary info: {with_salary}/{len(self.all_jobs)} ({with_salary/len(self.all_jobs)*100:.1f}%)")
        
        print("\n" + "="*70)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)


def main():
    """Main execution"""
    
    orchestrator = JobScrapingOrchestrator()
    
    try:
        # Run all scrapers
        jobs = orchestrator.run_all_scrapers()
        
        # Save results
        orchestrator.save_results()
        
        # Display summary
        orchestrator.display_summary()
        
        # Return jobs for next processing (Google Sheets, AI analysis)
        return jobs
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraping interrupted by user")
        print(f"   Partial results: {len(orchestrator.all_jobs)} jobs")
        orchestrator.save_results()
        
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    jobs = main()
    
    print("\n✅ Orchestrator finished!")
    print(f"   Total jobs collected: {len(jobs) if jobs else 0}")
    
    print("\n🔜 Next steps:")
    print("   1. Run AI analysis on jobs")
    print("   2. Update Google Sheets")
    print("   3. Send notifications")

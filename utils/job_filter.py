# utils/job_filter.py

import re

class JobFilter:
    """Filter jobs by experience level"""
    
    @staticmethod
    def extract_experience(text):
        """
        Extract years of experience from job description
        Returns: (min_years, max_years) or (None, None)
        """
        
        if not text:
            return None, None
        
        text = text.lower()
        
        # Patterns for experience
        patterns = [
            r'(\d+)\s*-\s*(\d+)\s*(?:years?|yrs?)',  # "2-4 years"
            r'(\d+)\+?\s*(?:years?|yrs?)',  # "3+ years" or "3 years"
            r'minimum\s+(\d+)\s+(?:years?|yrs?)',  # "minimum 3 years"
            r'at least\s+(\d+)\s+(?:years?|yrs?)',  # "at least 2 years"
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                if len(match.groups()) == 2:
                    return int(match.group(1)), int(match.group(2))
                else:
                    years = int(match.group(1))
                    return years, years
        
        # Check for keywords
        if any(keyword in text for keyword in ['fresher', 'entry level', 'entry-level', 'graduate', 'trainee']):
            return 0, 1
        
        if any(keyword in text for keyword in ['senior', 'lead', 'principal', 'architect']):
            return 5, 99
        
        if any(keyword in text for keyword in ['junior', 'associate']):
            return 0, 3
        
        return None, None
    
    @staticmethod
    def is_suitable_for_fresher(job_data):
        """
        Check if job is suitable for fresher/0-2 years experience
        """
        
        title = job_data.get('title', '').lower()
        description = job_data.get('description', '').lower()
        company = job_data.get('company', '').lower()
        
        # Red flags in title (REJECT)
        reject_keywords = [
            'senior', 'sr.', 'lead', 'principal', 'architect', 
            'manager', 'head', 'director', 'vp', 'chief',
            '5+ years', '3+ years', 'experienced'
        ]
        
        if any(keyword in title for keyword in reject_keywords):
            return False, "Senior role"
        
        # Green flags in title (ACCEPT)
        accept_keywords = [
            'fresher', 'entry', 'junior', 'associate', 'analyst i',
            'trainee', 'graduate', 'intern'
        ]
        
        if any(keyword in title for keyword in accept_keywords):
            return True, "Entry-level keyword"
        
        # Check experience in description
        min_exp, max_exp = JobFilter.extract_experience(description)
        
        if min_exp is not None:
            if min_exp <= 2 and max_exp <= 5:
                return True, f"{min_exp}-{max_exp} years suitable"
            elif min_exp > 2:
                return False, f"{min_exp}+ years required"
        
        # If no experience mentioned, assume it's open to all
        return True, "No experience mentioned - might be open"
    
    @staticmethod
    def estimate_fresher_salary(company, role="Data Analyst"):
        """
        Estimate salary for freshers at specific companies
        Returns: estimated_min_lpa or None
        """
        
        company = company.lower()
        
        # Known fresher salaries (in LPA)
        fresher_salaries = {
            'amazon': 28,
            'google': 30,
            'microsoft': 25,
            'meta': 30,
            'flipkart': 20,
            'swiggy': 18,
            'zomato': 16,
            'paytm': 15,
            'phonepe': 18,
            'razorpay': 16,
            'cred': 18,
            'uber': 22,
            'ola': 15,
            'myntra': 16,
            'linkedin': 28,
            'netflix': 35,
            'adobe': 24,
            'salesforce': 22,
            'oracle': 18,
            'sap': 20,
            'vmware': 20,
            'intuit': 22,
            'walmart': 18,
            'tcs': 7,
            'infosys': 8,
            'wipro': 7,
            'hcl': 8,
            'cognizant': 8,
            'accenture': 9,
            'capgemini': 8,
            'deloitte': 10,
            'ey': 9,
            'pwc': 10,
            'kpmg': 9,
        }
        
        # Find matching company
        for comp_name, salary in fresher_salaries.items():
            if comp_name in company:
                return salary
        
        # Default: Unknown company, assume average
        return None
    @staticmethod
    def verify_unknown_company_salary(company, role="Data Analyst", min_lpa=15):
        """
        For unknown startups, verify salary using AI
        """
        
        # Check if company is in known list
        known_companies = [
            'amazon', 'google', 'microsoft', 'meta', 'flipkart', 'swiggy',
            'zomato', 'paytm', 'phonepe', 'razorpay', 'cred', 'uber',
            'tcs', 'infosys', 'wipro', 'hcl', 'cognizant', 'accenture'
        ]
        
        is_known = any(known in company.lower() for known in known_companies)
        
        if is_known:
            # Use static estimate
            return JobFilter.estimate_fresher_salary(company, role)
        else:
            # Unknown company - verify using AI
            try:
                from utils.salary_verifier import SalaryVerifier
                verifier = SalaryVerifier()
                
                pays_above, salary_range, confidence = verifier.check_company_salary(company, role, min_lpa)
                
                if pays_above and confidence in ['High', 'Medium']:
                    # Extract min salary
                    import re
                    numbers = re.findall(r'\d+', salary_range)
                    if numbers:
                        return int(numbers[0])
                
                return None  # Reject
                
            except Exception as e:
                print(f"   ⚠️  AI verification failed, defaulting to INCLUDE")
                return min_lpa  # When in doubt, include


# Test
if __name__ == "__main__":
    test_jobs = [
        {
            'title': 'Data Analyst',
            'description': 'We are looking for a data analyst with 0-2 years of experience',
            'company': 'Amazon'
        },
        {
            'title': 'Senior Data Analyst',
            'description': 'Must have 5+ years of experience in data analysis',
            'company': 'Google'
        },
        {
            'title': 'Junior Business Analyst',
            'description': 'Fresh graduates welcome. Training provided.',
            'company': 'Flipkart'
        }
    ]
    
    for job in test_jobs:
        suitable, reason = JobFilter.is_suitable_for_fresher(job)
        estimated = JobFilter.estimate_fresher_salary(job['company'])
        
        print(f"\n{job['title']} at {job['company']}")
        print(f"  Suitable: {suitable} ({reason})")
        print(f"  Est. Salary: {estimated} LPA" if estimated else "  Est. Salary: Unknown")
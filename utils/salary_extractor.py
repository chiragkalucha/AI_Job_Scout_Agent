# utils/salary_extractor.py

import re

class SalaryExtractor:
    """Extract salary from job descriptions with multiple patterns"""
    
    @staticmethod
    def extract(text):
        """
        Extract salary from text
        Returns: "20-25 LPA" or "Not mentioned"
        """
        
        if not text:
            return "Not mentioned"
        
        # Clean text
        text = text.replace(',', '')  # Remove commas from numbers
        
        patterns = [
            # Pattern 1: "20-25 LPA" or "20-25 Lakhs"
            (r'(\d+)\s*-\s*(\d+)\s*(?:LPA|Lakhs?|Lacs?|L\.?P\.?A\.?)', 
             lambda m: f"{m.group(1)}-{m.group(2)} LPA"),
            
            # Pattern 2: "₹20-25 Lakhs" or "INR 20-25 Lakhs"
            (r'(?:₹|INR|Rs\.?)\s*(\d+)\s*-\s*(\d+)\s*(?:Lakhs?|Lacs?|LPA)', 
             lambda m: f"{m.group(1)}-{m.group(2)} LPA"),
            
            # Pattern 3: "Up to 30 LPA"
            (r'(?:up to|upto|max)\s*(\d+)\s*(?:LPA|Lakhs?|Lacs?)', 
             lambda m: f"Up to {m.group(1)} LPA"),
            
            # Pattern 4: Just "25 LPA" or "25 Lakhs"
            (r'(?:^|\s)(\d+)\s*(?:LPA|Lakhs?|Lacs?)(?:\s|$)', 
             lambda m: f"{m.group(1)} LPA"),
            
            # Pattern 5: "2000000-2500000" (in raw numbers)
            (r'(?:₹|INR|Rs\.?)?\s*(\d{7,8})\s*-\s*(\d{7,8})', 
             lambda m: f"{int(m.group(1))//100000}-{int(m.group(2))//100000} LPA"),
            
            # Pattern 6: "20L-25L" or "20L - 25L"
            (r'(\d+)\s*L\s*-\s*(\d+)\s*L', 
             lambda m: f"{m.group(1)}-{m.group(2)} LPA"),
            
            # Pattern 7: "$80K-$100K" (convert to INR)
            (r'\$\s*(\d+)K?\s*-\s*\$?\s*(\d+)K?', 
             lambda m: f"{int(m.group(1))*0.8}-{int(m.group(2))*0.8} LPA"),  # $1 ≈ 83 INR, $100K ≈ 8.3L
        ]
        
        for pattern, formatter in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return formatter(match)
                except:
                    continue
        
        return "Not mentioned"
    
    @staticmethod
    def get_min_salary(salary_str):
        """Extract minimum salary as integer"""
        if salary_str == "Not mentioned":
            return 0
        
        numbers = re.findall(r'\d+', salary_str)
        if numbers:
            return int(numbers[0])
        return 0
    
    @staticmethod
    def meets_criteria(salary_str, min_lpa):
        """Check if salary meets minimum criteria"""
        min_sal = SalaryExtractor.get_min_salary(salary_str)
        
        if min_sal == 0:
            return True  # Include for AI analysis
        
        return min_sal >= min_lpa


# Test
if __name__ == "__main__":
    test_cases = [
        "Salary: 20-25 LPA",
        "Package: ₹30 Lakhs per annum",
        "Up to 40 LPA",
        "Compensation: 2000000-2500000 per annum",
        "$80K-$100K annually",
        "25L - 30L CTC"
    ]
    
    for case in test_cases:
        result = SalaryExtractor.extract(case)
        print(f"'{case}' → {result}")
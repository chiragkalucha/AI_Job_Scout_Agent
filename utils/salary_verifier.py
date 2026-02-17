# utils/salary_verifier.py - FIXED WITH CORRECT MODEL

from groq import Groq
import os
import json
from dotenv import load_dotenv

load_dotenv('config/.env')

class SalaryVerifier:
    """AI-powered salary verification"""
    
    # ✅ CORRECT MODEL
    MODEL = "llama-3.3-70b-versatile"
    
    def __init__(self):
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY required")
        
        self.client = Groq(api_key=api_key)
    
    def check_company_salary(self, company_name, role="Data Analyst", min_lpa=15):
        """Check if company pays above threshold"""
        
        print(f"🔍 Checking: {company_name} ({role})...", end=' ')
        
        try:
            prompt = f"""Does {company_name} in India pay ABOVE {min_lpa} LPA to freshers (0-2 years) for {role}?

Respond ONLY in JSON:
{{
  "pays_above_threshold": true,
  "estimated_min_lpa": 18,
  "estimated_max_lpa": 25,
  "confidence": "High",
  "reasoning": "brief explanation"
}}"""

            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": "You are a salary research expert. Respond only in JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            result = json.loads(result_text.strip())
            
            pays_above = result.get('pays_above_threshold', False)
            est_min = result.get('estimated_min_lpa', 0)
            est_max = result.get('estimated_max_lpa', 0)
            confidence = result.get('confidence', 'Low')
            
            salary_range = f"{est_min}-{est_max} LPA"
            
            if pays_above:
                print(f"✅ YES ({salary_range}, {confidence})")
            else:
                print(f"❌ NO ({salary_range}, {confidence})")
            
            return pays_above, salary_range, confidence
            
        except Exception as e:
            print(f"⚠️ Failed ({str(e)[:40]})")
            return True, f"Est. {min_lpa}+ LPA", "Low"


if __name__ == "__main__":
    print("="*70)
    print("SALARY VERIFIER TEST")
    print("="*70)
    print()
    
    verifier = SalaryVerifier()
    
    test_companies = [
        "Razorpay",
        "Zepto", 
        "Meesho",
        "PhonePe"
    ]
    
    for company in test_companies:
        pays, salary, conf = verifier.check_company_salary(company)
        print()
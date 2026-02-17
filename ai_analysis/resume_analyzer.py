# ai_analysis/resume_analyzer.py - FIXED WITH CORRECT MODEL

from groq import Groq
import os
import sys
from datetime import datetime
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv('config/.env')

class ResumeAnalyzer:
    """AI-powered resume analysis using Groq"""
    
    # ✅ CORRECT MODEL
    MODEL = "llama-3.3-70b-versatile"
    
    def __init__(self, resume_path='resumes/chirag_kalucha_resume.txt'):
        """Initialize with resume"""
        
        self.resume_path = resume_path
        
        # Initialize Groq
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in .env")
        
        self.client = Groq(api_key=api_key)
        
        # Load resume
        try:
            with open(resume_path, 'r', encoding='utf-8') as f:
                self.resume_text = f.read()
            print(f"✅ Resume loaded: {len(self.resume_text)} characters")
        except FileNotFoundError:
            raise FileNotFoundError(f"Resume not found at: {resume_path}")
        
        # Extract skills
        self.resume_skills = self.extract_skills()
    
    def extract_skills(self):
        """Extract skills from resume"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": "Extract technical skills. Return comma-separated list only."},
                    {"role": "user", "content": f"Extract skills:\n{self.resume_text[:2000]}"}
                ],
                max_tokens=200,
                temperature=0
            )
            
            skills_text = response.choices[0].message.content.strip()
            skills_list = [s.strip() for s in skills_text.split(',') if s.strip()]
            
            print(f"✅ Extracted {len(skills_list)} skills")
            return skills_list[:20]
            
        except Exception as e:
            print(f"⚠️  Skill extraction failed: {str(e)[:80]}")
            return ['Python', 'SQL', 'Data Analysis', 'Power BI', 'Machine Learning']
    
    def analyze_job(self, job_data):
        """Analyze job-resume match"""
        
        job_title = job_data.get('title', 'Unknown')[:100]
        job_description = job_data.get('description', '')[:2000]
        company = job_data.get('company', 'Unknown')[:50]
        
        if not job_description or len(job_description) < 50:
            job_description = f"Role: {job_title} at {company}"
        
        print(f"🤖 Analyzing: {job_title[:40]}...", end=' ')
        
        try:
            prompt = f"""Analyze job-resume match.

JOB:
Title: {job_title}
Company: {company}
Description: {job_description}

CANDIDATE SKILLS: {', '.join(self.resume_skills[:10])}

Respond ONLY in JSON format:
{{
  "ats_score": 75,
  "selection_chances": "High",
  "skills_match_percentage": 80,
  "missing_skills": ["skill1", "skill2"],
  "resume_changes": "brief suggestion",
  "project_emphasis": "which project to highlight"
}}"""

            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[
                    {"role": "system", "content": "You are an ATS analyzer. Always respond in valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Extract JSON
            if '```json' in result_text:
                result_text = result_text.split('```json')[1].split('```')[0]
            elif '```' in result_text:
                result_text = result_text.split('```')[1].split('```')[0]
            
            result_text = result_text.strip()
            
            try:
                analysis = json.loads(result_text)
            except json.JSONDecodeError:
                result_text = result_text.replace("'", '"')
                analysis = json.loads(result_text)
            
            analysis['analysis_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"✅ ATS: {analysis.get('ats_score', 0)}/100")
            
            return analysis
            
        except Exception as e:
            print(f"⚠️ Failed ({str(e)[:40]})")
            
            return {
                'ats_score': 65,
                'selection_chances': 'Medium',
                'skills_match_percentage': 60,
                'missing_skills': [],
                'resume_changes': 'Manual review recommended',
                'project_emphasis': 'Highlight relevant projects',
                'analysis_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def batch_analyze(self, jobs_list):
        """Analyze multiple jobs"""
        
        print(f"\n{'='*70}")
        print(f"AI ANALYSIS ({len(jobs_list)} jobs)")
        print(f"{'='*70}")
        
        analyzed_jobs = []
        
        for idx, job in enumerate(jobs_list, 1):
            print(f"[{idx}/{len(jobs_list)}] ", end='')
            
            analysis = self.analyze_job(job)
            job_with_analysis = {**job, **analysis}
            analyzed_jobs.append(job_with_analysis)
            
            if idx < len(jobs_list):
                import time
                time.sleep(0.3)
        
        print(f"\n{'='*70}")
        print(f"✅ ANALYSIS COMPLETE")
        print(f"{'='*70}")
        
        high_chance = sum(1 for j in analyzed_jobs if j.get('selection_chances') == 'High')
        avg_ats = sum(j.get('ats_score', 0) for j in analyzed_jobs) / len(analyzed_jobs) if analyzed_jobs else 0
        
        print(f"\n📊 Summary:")
        print(f"   High-chance jobs: {high_chance}/{len(analyzed_jobs)}")
        print(f"   Average ATS score: {avg_ats:.1f}/100")
        
        return analyzed_jobs


if __name__ == "__main__":
    print("="*70)
    print("RESUME ANALYZER TEST")
    print("="*70)
    
    try:
        analyzer = ResumeAnalyzer()
        
        test_job = {
            'title': 'Data Analyst',
            'company': 'Amazon',
            'description': 'Looking for Data Analyst with Python, SQL, Power BI skills. 0-2 years experience.'
        }
        
        result = analyzer.analyze_job(test_job)
        
        print(f"\n✅ Test Result:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
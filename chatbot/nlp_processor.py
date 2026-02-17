# chatbot/nlp_processor.py - FIXED

import re
from enum import Enum
from fuzzywuzzy import fuzz

class Intent(Enum):
    START_HUNT = "start_hunt"
    STOP_HUNT = "stop_hunt"
    CHANGE_SALARY = "change_salary"
    CHANGE_ROLES = "change_roles"
    ADD_ROLE = "add_role"
    REMOVE_ROLE = "remove_role"
    CLEAN_JOBS = "clean_jobs"
    OPEN_SHEET = "open_sheet"
    SHOW_STATUS = "show_status"
    HELP = "help"
    UNKNOWN = "unknown"

class NLPProcessor:
    """Lightweight NLP processor with priority-based intent detection"""
    
    def __init__(self):
        # Intent patterns (ORDERED BY PRIORITY)
        self.intent_patterns = [
            # STOP patterns FIRST (highest priority)
            (Intent.STOP_HUNT, [
                r'\bstop\s+hunt',
                r'\bhalt\s+hunt',
                r'\bcancel\s+hunt',
                r'\bend\s+hunt',
                r'\bpause\s+hunt',
                r'\bdisable\s+hunt',
                r'\bquit\s+hunt',
                r'\bstop\s+hunting',
                r'\b(stop|halt|cancel|end|pause|quit)\b(?!.*start)',
            ]),
            
            # ADD/REMOVE before CHANGE (more specific)
            (Intent.ADD_ROLE, [
                r'\badd\s+\w+',  # ✅ FIXED: "add X" pattern
                r'\badd\s+role',
                r'\badd\s+position',
                r'\binclude\s+role',
                r'\bappend\s+role',
                r'\badd\s+[A-Z]',  # "add Data Scientist"
            ]),
            
            (Intent.REMOVE_ROLE, [
                r'\bremove\s+\w+',
                r'\bremove\s+role',
                r'\bdelete\s+role',
                r'\bdrop\s+role',
            ]),
            
            # START patterns
            (Intent.START_HUNT, [
                r'\bstart\s+hunt',
                r'\bbegin\s+hunt',
                r'\blaunch\s+hunt',
                r'\brun\s+hunt',
                r'\bstart\s+hunting',
                r'\bbegin\s+searching',
                r'\bhunt\s+jobs',
                r'\bfind\s+jobs',
                r'\b(start|begin|go)\b.*\b(hunt|search)',
            ]),
            
            # Other intents
            (Intent.CHANGE_SALARY, [
                r'\bchange\s+salary',
                r'\bupdate\s+salary',
                r'\bset\s+salary',
                r'\bmodify\s+salary',
                r'\bsalary\s+to\s+\d+',
                r'\bminimum\s+salary',
            ]),
            
            (Intent.CHANGE_ROLES, [
                r'\bchange\s+roles',
                r'\bupdate\s+roles',
                r'\bset\s+roles',
                r'\bmodify\s+roles',
                r'\broles\s+to\s+',
            ]),
            
            (Intent.CLEAN_JOBS, [
                r'\bclean\s+jobs',
                r'\bdelete\s+checked',
                r'\bremove\s+checked',
                r'\bclear\s+checked',
                r'\bclean\s+sheet',
            ]),
            
            (Intent.OPEN_SHEET, [
                r'\bopen\s+sheet',
                r'\bshow\s+sheet',
                r'\bview\s+sheet',
                r'\bdisplay\s+sheet',
                r'\bopen\s+spreadsheet',
            ]),
            
            (Intent.SHOW_STATUS, [
                r'\bstatus\b',
                r'\bshow\s+status',
                r'\bcurrent\s+status',
                r'\binfo\b',
                r'\bsettings\b',
            ]),
            
            (Intent.HELP, [
                r'\bhelp\b',
                r'\bcommands\b',
                r'\bwhat\s+can\s+you\s+do',
            ]),
        ]
    
    def detect_intent(self, text):
        """Detect intent using pattern matching with priority"""
        
        text = text.lower().strip()
        
        if not text:
            return Intent.UNKNOWN
        
        # Try each intent pattern IN ORDER
        for intent, patterns in self.intent_patterns:
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    return intent
        
        return Intent.UNKNOWN
    
    def extract_number(self, text):
        """Extract number from text"""
        numbers = re.findall(r'\b(\d+)\b', text)
        return int(numbers[0]) if numbers else None
    
    def extract_roles(self, text):
        """Extract job roles from text"""
        
        # Look for quoted roles: "Data Analyst", "ML Engineer"
        quoted = re.findall(r'["\']([^"\']+)["\']', text)
        if quoted:
            return quoted
        
        # Look for roles after keywords
        # "add Data Scientist" -> "Data Scientist"
        for keyword in ['add', 'remove', 'include', 'exclude', 'to']:
            pattern = rf'\b{keyword}\s+(.+?)(?:\s+to|\s+from|$)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                role_text = match.group(1).strip()
                # Handle comma-separated
                if ',' in role_text:
                    return [r.strip().title() for r in role_text.split(',')]
                else:
                    return [role_text.title()]
        
        # Look for roles after "to"
        after_to = re.search(r'\bto\s+(.+)', text, re.IGNORECASE)
        if after_to:
            roles_text = after_to.group(1)
            roles = re.split(r',\s*|\s+and\s+', roles_text)
            return [r.strip().title() for r in roles if r.strip()]
        
        # Common job titles as fallback
        job_titles = [
            'data analyst', 'business analyst', 'data scientist',
            'ml engineer', 'machine learning engineer', 'software engineer',
            'data engineer', 'analyst', 'scientist', 'engineer',
            'developer', 'sde', 'consultant'
        ]
        
        found = []
        for title in job_titles:
            if title in text.lower():
                found.append(title.title())
        
        return found if found else None


# Test
if __name__ == "__main__":
    processor = NLPProcessor()
    
    test_commands = [
        "start hunt",
        "stop hunt",
        "please stop the hunt",
        "halt hunting",
        "start hunting for jobs",
        "change salary to 25",
        "update roles to Data Analyst, ML Engineer",
        "add Data Scientist",
        "add ML Engineer",
        "remove Business Analyst",
        "clean jobs",
        "open sheet",
        "status"
    ]
    
    print("="*60)
    print("NLP PROCESSOR TEST")
    print("="*60)
    
    for cmd in test_commands:
        intent = processor.detect_intent(cmd)
        
        # Also test role extraction for add/remove
        if intent in [Intent.ADD_ROLE, Intent.REMOVE_ROLE]:
            roles = processor.extract_roles(cmd)
            print(f"{cmd:45} → {intent.value} ({roles})")
        else:
            print(f"{cmd:45} → {intent.value}")
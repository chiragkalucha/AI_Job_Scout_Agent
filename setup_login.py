# setup_logins.py - One-time login setup for all portals

import os
from utils.login_helper import LoginHelper

print("="*70)
print("ONE-TIME LOGIN SETUP")
print("="*70)
print("\nThis script will help you login to job portals.")
print("You only need to do this ONCE.")
print("Future runs will use saved sessions.\n")

# Create browser profiles directory
os.makedirs('./browser_profiles', exist_ok=True)

portals = [
    {
        'name': 'LinkedIn',
        'url': 'https://www.linkedin.com/login',
        'priority': 'HIGH'
    },
    {
        'name': 'Naukri',
        'url': 'https://www.naukri.com/nlogin/login',
        'priority': 'HIGH'
    },
    {
        'name': 'Glassdoor',
        'url': 'https://www.glassdoor.co.in/profile/login_input.htm',
        'priority': 'MEDIUM'
    }
]

print("We'll setup login for these portals:\n")
for p in portals:
    print(f"  • {p['name']} ({p['priority']} priority)")

print("\n" + "="*70)

for portal in portals:
    proceed = input(f"\nSetup {portal['name']}? (y/n): ")
    
    if proceed.lower() == 'y':
        LoginHelper.request_login(portal['name'], portal['url'])
    else:
        print(f"⏭️  Skipped {portal['name']}")

print("\n" + "="*70)
print("✅ SETUP COMPLETE!")
print("="*70)
print("\nYou can now run scrapers without manual login.")
print("Run: python main.py")
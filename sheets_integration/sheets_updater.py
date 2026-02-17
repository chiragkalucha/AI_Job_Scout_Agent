# sheets_integration/sheets_updater.py - FIXED VERSION

import os
import sys
from datetime import datetime
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv('config/.env')

class GoogleSheetsUpdater:
    """Update Google Sheets with job data"""
    
    def __init__(self):
        """Initialize Google Sheets API"""
        
        self.spreadsheet_id = os.getenv('GOOGLE_SHEET_ID')
        
        if not self.spreadsheet_id:
            raise ValueError("GOOGLE_SHEET_ID not found in .env file")
        
        # Set up credentials
        creds_path = 'config/google_credentials.json'
        
        if not os.path.exists(creds_path):
            raise FileNotFoundError(f"Google credentials not found at: {creds_path}")
        
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        
        try:
            creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
            self.service = build('sheets', 'v4', credentials=creds)
            self.sheet = self.service.spreadsheets()
            
            print("✅ Google Sheets API connected")
            
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Google Sheets: {str(e)}")
    
    def add_jobs_batch(self, jobs_list):
        """Add multiple jobs at once"""
        
        print(f"\n{'='*70}")
        print(f"UPDATING GOOGLE SHEETS")
        print(f"{'='*70}")
        print(f"📊 Adding {len(jobs_list)} jobs to sheet...")
        
        if not jobs_list:
            print("⚠️  No jobs to add")
            return False
        
        # ✅ FIXED: Prepare all rows FIRST
        rows = []
        
        for job in jobs_list:
            row = [
                False,  # Checkbox (column A)
                job.get('date_found', datetime.now().strftime('%d-%b-%Y')),  # Use job's date
                job.get('time_found', datetime.now().strftime('%I:%M %p')),  # Use job's time
                job.get('company', 'Unknown'),
                job.get('title', 'Unknown'),
                job.get('salary', 'Not mentioned'),
                job.get('location', 'Unknown'),
                job.get('portal', 'Unknown'),
                job.get('url', ''),
                
                # AI Analysis fields
                str(job.get('ats_score', 'Pending')),
                str(job.get('selection_chances', 'Pending')),
                str(job.get('skills_match_percentage', 'Pending')),
                
                # Missing skills - handle list
                ', '.join(job.get('missing_skills', [])) if isinstance(job.get('missing_skills'), list) else str(job.get('missing_skills', 'Pending')),
                
                str(job.get('resume_changes', 'Pending')),
                str(job.get('project_emphasis', 'Pending')),
                
                'New',  # Status
                '',     # Notes
                self.calculate_priority(job)
            ]
            
            rows.append(row)
        
        # ✅ FIXED: Now body is defined
        body = {'values': rows}
        
        try:
            # Batch append
            result = self.sheet.values().append(
                spreadsheetId=self.spreadsheet_id,
                range='Sheet1!A:R',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            
            updates = result.get('updates', {})
            rows_added = updates.get('updatedRows', 0)
            
            print(f"✅ Successfully added {rows_added} jobs to Google Sheets")
            
            # Apply formatting
            self.format_sheet()
            
            return True
            
        except HttpError as e:
            print(f"❌ Error updating sheet: {str(e)}")
            return False
    
    def calculate_priority(self, job):
        """Calculate job priority"""
        
        priority_score = 0
        
        # Factor 1: Company
        high_priority_companies = ['Amazon', 'Google', 'Microsoft', 'Meta', 'Apple', 'Flipkart', 'Netflix']
        company = job.get('company', '')
        
        if any(comp.lower() in company.lower() for comp in high_priority_companies):
            priority_score += 3
        
        # Factor 2: Salary
        salary = job.get('salary', 'Not mentioned')
        if salary != 'Not mentioned':
            priority_score += 2
            
            import re
            numbers = re.findall(r'\d+', salary)
            if numbers:
                min_sal = int(numbers[0])
                if min_sal >= 30:
                    priority_score += 2
                elif min_sal >= 25:
                    priority_score += 1
        
        # Factor 3: ATS score
        ats_score = job.get('ats_score', 0)
        if isinstance(ats_score, (int, float)):
            if ats_score >= 90:
                priority_score += 3
            elif ats_score >= 80:
                priority_score += 2
            elif ats_score >= 70:
                priority_score += 1
        
        # Factor 4: Selection chances
        chances = job.get('selection_chances', '')
        if chances == 'High':
            priority_score += 2
        elif chances == 'Medium':
            priority_score += 1
        
        # Determine priority level
        if priority_score >= 7:
            return '🔴 HIGH'
        elif priority_score >= 4:
            return '🟡 MEDIUM'
        else:
            return '🟢 LOW'
    
    def format_sheet(self):
        """Apply formatting to the sheet"""
        
        try:
            # Get sheet ID
            sheet_metadata = self.sheet.get(spreadsheetId=self.spreadsheet_id).execute()
            sheet_id = sheet_metadata['sheets'][0]['properties']['sheetId']
            
            requests = [
                # Freeze header row
                {
                    'updateSheetProperties': {
                        'properties': {
                            'sheetId': sheet_id,
                            'gridProperties': {
                                'frozenRowCount': 1
                            }
                        },
                        'fields': 'gridProperties.frozenRowCount'
                    }
                },
                
                # Bold header row with blue background
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_id,
                            'startRowIndex': 0,
                            'endRowIndex': 1
                        },
                        'cell': {
                            'userEnteredFormat': {
                                'backgroundColor': {
                                    'red': 0.2,
                                    'green': 0.4,
                                    'blue': 0.8
                                },
                                'textFormat': {
                                    'foregroundColor': {
                                        'red': 1.0,
                                        'green': 1.0,
                                        'blue': 1.0
                                    },
                                    'bold': True
                                }
                            }
                        },
                        'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                    }
                },
                
                # Add checkbox validation to column A (starting from row 2)
                {
                    'repeatCell': {
                        'range': {
                            'sheetId': sheet_id,
                            'startColumnIndex': 0,
                            'endColumnIndex': 1,
                            'startRowIndex': 1
                        },
                        'cell': {
                            'dataValidation': {
                                'condition': {
                                    'type': 'BOOLEAN'
                                }
                            }
                        },
                        'fields': 'dataValidation'
                    }
                },
                
                # Auto-resize all columns
                {
                    'autoResizeDimensions': {
                        'dimensions': {
                            'sheetId': sheet_id,
                            'dimension': 'COLUMNS',
                            'startIndex': 0,
                            'endIndex': 18
                        }
                    }
                }
            ]
            
            body = {'requests': requests}
            
            self.sheet.batchUpdate(
                spreadsheetId=self.spreadsheet_id,
                body=body
            ).execute()
            
            print("✅ Sheet formatting applied")
            
        except Exception as e:
            print(f"⚠️  Formatting error (non-critical): {str(e)[:60]}")
    
    def get_sheet_stats(self):
        """Get statistics about the sheet"""
        
        try:
            result = self.sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Sheet1!A:R'
            ).execute()
            
            values = result.get('values', [])
            
            if not values or len(values) <= 1:
                return {
                    'total_jobs': 0,
                    'pending_analysis': 0,
                    'high_priority': 0,
                    'applied': 0
                }
            
            total = len(values) - 1
            
            pending = sum(1 for row in values[1:] if len(row) > 9 and row[9] == 'Pending')
            high_priority = sum(1 for row in values[1:] if len(row) > 17 and 'HIGH' in str(row[17]))
            applied = sum(1 for row in values[1:] if len(row) > 15 and row[15] == 'Applied')
            
            return {
                'total_jobs': total,
                'pending_analysis': pending,
                'high_priority': high_priority,
                'applied': applied
            }
            
        except Exception as e:
            print(f"❌ Error getting stats: {str(e)}")
            return {}
    def get_existing_job_urls(self):
        """Get all job URLs already in sheet"""
        
        try:
            result = self.sheet.values().get(
                spreadsheetId=self.spreadsheet_id,
                range='Sheet1!I:I'  # Column I = Job URL
            ).execute()
            
            values = result.get('values', [])
            
            # Extract URLs (skip header)
            existing_urls = set()
            for row in values[1:]:
                if row and len(row) > 0:
                    url = row[0].strip()
                    if url and url != 'Job URL':  # Skip header
                        existing_urls.add(url)
            
            print(f"📊 Found {len(existing_urls)} existing jobs in sheet")
            return existing_urls
            
        except Exception as e:
            print(f"⚠️  Error getting existing URLs: {e}")
            return set()

    def filter_new_jobs(self, jobs_list):
            """Remove jobs already in sheet"""
            
            existing_urls = self.get_existing_job_urls()
            
            if not existing_urls:
                print("ℹ️  Sheet is empty, all jobs are new")
                return jobs_list
            
            # Filter out existing jobs
            new_jobs = []
            skipped = 0
            
            for job in jobs_list:
                job_url = job.get('url', '').strip()
                
                if job_url and job_url not in existing_urls:
                    new_jobs.append(job)
                else:
                    skipped += 1
            
            print(f"✅ Filtered: {len(new_jobs)} new jobs (skipped {skipped} duplicates)")
            
            return new_jobs

    def delete_checked_jobs(self):
            """Delete jobs marked as applied (checkbox = TRUE)"""
            
            print("\n🗑️  Checking for completed jobs...")
            
            try:
                # Get all data including checkboxes
                result = self.sheet.values().get(
                    spreadsheetId=self.spreadsheet_id,
                    range='Sheet1!A:R'
                ).execute()
                
                values = result.get('values', [])
                
                if not values or len(values) <= 1:
                    print("   No jobs to clean up")
                    return
                
                # Find checked rows (from bottom to top to preserve indices)
                rows_to_delete = []
                
                for idx, row in enumerate(values[1:], start=2):  # Start from row 2
                    if len(row) > 0 and str(row[0]).upper() in ['TRUE', 'YES', '1']:
                        rows_to_delete.append(idx)
                
                if not rows_to_delete:
                    print("   No checked jobs to delete")
                    return
                
                print(f"   Found {len(rows_to_delete)} checked jobs")
                
                # Get sheet ID
                sheet_metadata = self.sheet.get(spreadsheetId=self.spreadsheet_id).execute()
                sheet_id = sheet_metadata['sheets'][0]['properties']['sheetId']
                
                # Delete rows in reverse order (bottom to top)
                requests = []
                for row_num in sorted(rows_to_delete, reverse=True):
                    requests.append({
                        'deleteDimension': {
                            'range': {
                                'sheetId': sheet_id,
                                'dimension': 'ROWS',
                                'startIndex': row_num - 1,
                                'endIndex': row_num
                            }
                        }
                    })
                
                # Execute batch delete
                body = {'requests': requests}
                self.sheet.batchUpdate(
                    spreadsheetId=self.spreadsheet_id,
                    body=body
                ).execute()
                
                print(f"   ✅ Deleted {len(rows_to_delete)} checked jobs")
                
            except Exception as e:
                print(f"   ⚠️  Cleanup error: {e}")


# Test
if __name__ == "__main__":
    print("="*70)
    print("GOOGLE SHEETS UPDATER TEST")
    print("="*70)
    
    try:
        updater = GoogleSheetsUpdater()
        
        # Test with sample jobs
        sample_jobs = [
            {
                'date_found': '2026-02-14',
                'time_found': '17:30:00',
                'company': 'Amazon',
                'title': 'Data Analyst',
                'salary': '25-30 LPA',
                'location': 'Bangalore',
                'portal': 'Amazon Careers',
                'url': 'https://amazon.jobs/example',
                'ats_score': 85,
                'selection_chances': 'High',
                'skills_match_percentage': 80,
                'missing_skills': ['Docker', 'Kubernetes'],
                'resume_changes': 'Add Docker experience',
                'project_emphasis': 'Highlight ML project'
            },
            {
                'date_found': '2026-02-14',
                'time_found': '17:35:00',
                'company': 'Flipkart',
                'title': 'Business Analyst',
                'salary': 'Est. 20 LPA',
                'location': 'Bangalore',
                'portal': 'Flipkart Careers',
                'url': 'https://flipkart.com/careers',
                'ats_score': 78,
                'selection_chances': 'Medium',
                'skills_match_percentage': 75,
                'missing_skills': ['Tableau'],
                'resume_changes': 'Emphasize business analysis skills',
                'project_emphasis': 'Highlight funnel analysis'
            }
        ]
        
        print("\n📝 Adding sample jobs...")
        success = updater.add_jobs_batch(sample_jobs)
        
        if success:
            print("\n✅ Test successful!")
            print(f"\n🔗 Check your Google Sheet:")
            print(f"   https://docs.google.com/spreadsheets/d/{updater.spreadsheet_id}")
            
            # Get stats
            print("\n📊 Sheet Statistics:")
            stats = updater.get_sheet_stats()
            for key, value in stats.items():
                print(f"   {key}: {value}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
# sheets_integration/sheet_cleaner.py

import os
import sys
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv('config/.env')

class SheetCleaner:
    """Clean up checked jobs from sheet"""
    
    def __init__(self):
        self.spreadsheet_id = os.getenv('GOOGLE_SHEET_ID')
        
        creds_path = 'config/google_credentials.json'
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        
        creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
        self.service = build('sheets', 'v4', credentials=creds)
        self.sheet = self.service.spreadsheets()
    
    def delete_checked_jobs(self):
        """Delete rows where checkbox (column A) is checked"""
        
        print("\n🗑️  Checking for jobs to delete...")
        
        # Get all data
        result = self.sheet.values().get(
            spreadsheetId=self.spreadsheet_id,
            range='Sheet1!A:R'
        ).execute()
        
        values = result.get('values', [])
        
        if not values or len(values) <= 1:
            print("   No jobs found")
            return
        
        # Find rows with checkbox = TRUE
        rows_to_delete = []
        
        for idx, row in enumerate(values[1:], start=2):  # Start from row 2
            if len(row) > 0 and str(row[0]).upper() == 'TRUE':
                rows_to_delete.append(idx)
        
        if not rows_to_delete:
            print("   No checked jobs to delete")
            return
        
        print(f"   Found {len(rows_to_delete)} checked jobs")
        
        # Delete rows (in reverse order to maintain indices)
        rows_to_delete.reverse()
        
        for row_num in rows_to_delete:
            self.delete_row(row_num)
        
        print(f"   ✅ Deleted {len(rows_to_delete)} jobs")
    
    def delete_row(self, row_number):
        """Delete a specific row"""
        
        # Get sheet ID
        sheet_metadata = self.sheet.get(spreadsheetId=self.spreadsheet_id).execute()
        sheet_id = sheet_metadata['sheets'][0]['properties']['sheetId']
        
        request = {
            'deleteDimension': {
                'range': {
                    'sheetId': sheet_id,
                    'dimension': 'ROWS',
                    'startIndex': row_number - 1,  # 0-indexed
                    'endIndex': row_number
                }
            }
        }
        
        body = {'requests': [request]}
        
        self.sheet.batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body=body
        ).execute()


# Run as scheduled task
if __name__ == "__main__":
    print("="*70)
    print("CLEANING CHECKED JOBS")
    print("="*70)
    
    cleaner = SheetCleaner()
    cleaner.delete_checked_jobs()
    
    print("\n✅ Cleanup complete!")
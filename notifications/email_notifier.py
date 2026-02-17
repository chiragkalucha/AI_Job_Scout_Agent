# notifications/email_notifier.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv

load_dotenv('config/.env')

class EmailNotifier:
    """Send email notifications for new jobs"""
    
    def __init__(self):
        """Initialize email configuration"""
        
        self.sender_email = os.getenv('YOUR_EMAIL')
        self.sender_password = os.getenv('EMAIL_APP_PASSWORD')
        self.recipient_email = os.getenv('YOUR_EMAIL')  # Send to yourself
        
        if not self.sender_email or not self.sender_password:
            raise ValueError("Email credentials not found in .env")
        
        print("✅ Email notifier initialized")
    
    def send_job_alert(self, jobs_list):
        """Send email with new jobs found"""
        
        if not jobs_list:
            print("⚠️  No jobs to notify about")
            return False
        
        print(f"\n📧 Sending email notification for {len(jobs_list)} jobs...")
        
        # Create email
        subject = f"🚨 {len(jobs_list)} New Jobs Found - AI Job Scout"
        
        # HTML email body
        html = self.create_email_html(jobs_list)
        
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = self.sender_email
        message['To'] = self.recipient_email
        
        html_part = MIMEText(html, 'html')
        message.attach(html_part)
        
        try:
            # Connect to Gmail SMTP
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(
                    self.sender_email,
                    self.recipient_email,
                    message.as_string()
                )
            
            print("✅ Email sent successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Email failed: {str(e)[:80]}")
            return False
    
    def create_email_html(self, jobs):
        """Create HTML email template"""
        
        # Count high priority jobs
        high_priority = sum(1 for j in jobs if j.get('ats_score', 0) >= 80 or 'Amazon' in j.get('company', ''))
        
        html = f"""
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f4f4f4;
                    margin: 0;
                    padding: 20px;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background-color: white;
                    border-radius: 10px;
                    padding: 30px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{
                    background-color: #FF9900;
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    text-align: center;
                }}
                .summary {{
                    background-color: #f9f9f9;
                    padding: 15px;
                    margin: 20px 0;
                    border-left: 4px solid #FF9900;
                }}
                .job-card {{
                    border: 1px solid #ddd;
                    padding: 15px;
                    margin: 15px 0;
                    border-radius: 5px;
                    background-color: #fafafa;
                }}
                .job-title {{
                    color: #232F3E;
                    font-size: 18px;
                    font-weight: bold;
                    margin-bottom: 5px;
                }}
                .job-company {{
                    color: #666;
                    font-size: 14px;
                    margin-bottom: 10px;
                }}
                .job-details {{
                    font-size: 13px;
                    color: #333;
                }}
                .high-priority {{
                    background-color: #fff3cd;
                    border-left-color: #ff0000;
                }}
                .apply-button {{
                    display: inline-block;
                    background-color: #FF9900;
                    color: white;
                    padding: 10px 20px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 10px;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    color: #999;
                    font-size: 12px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚀 AI Job Scout Alert</h1>
                    <p>{datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
                </div>
                
                <div class="summary">
                    <h2>📊 Summary</h2>
                    <p><strong>{len(jobs)}</strong> new jobs found</p>
                    <p><strong>{high_priority}</strong> high-priority opportunities</p>
                </div>
                
                <h2>🎯 Top Opportunities</h2>
        """
        
        # Add job cards (top 10)
        for idx, job in enumerate(jobs[:10], 1):
            is_high_priority = job.get('ats_score', 0) >= 80 or any(comp in job.get('company', '') for comp in ['Amazon', 'Google', 'Microsoft'])
            
            card_class = 'job-card high-priority' if is_high_priority else 'job-card'
            
            html += f"""
                <div class="{card_class}">
                    <div class="job-title">
                        {idx}. {job.get('title', 'Unknown')}
                        {' 🔥' if is_high_priority else ''}
                    </div>
                    <div class="job-company">
                        {job.get('company', 'Unknown')} | {job.get('portal', 'Unknown')}
                    </div>
                    <div class="job-details">
                        💰 {job.get('salary', 'Not mentioned')}<br>
                        📍 {job.get('location', 'Unknown')}<br>
            """
            
            if job.get('ats_score'):
                html += f"🎯 ATS Score: {job.get('ats_score')}/100 | Selection: {job.get('selection_chances', 'Unknown')}<br>"
            
            html += f"""
                    </div>
                    <a href="{job.get('url', '#')}" class="apply-button" target="_blank">
                        Apply Now →
                    </a>
                </div>
            """
        
        if len(jobs) > 10:
            html += f"""
                <div class="summary">
                    <p>... and {len(jobs) - 10} more jobs!</p>
                    <p>Check your Google Sheet for complete list</p>
                </div>
            """
        
        html += """
                <div class="footer">
                    <p>🤖 Automated by AI Job Scout</p>
                    <p>This is an automated email. Do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def send_daily_summary(self, stats):
        """Send daily summary email"""
        
        subject = f"📊 Daily Job Scout Summary - {stats.get('total_jobs', 0)} Jobs Tracked"
        
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; }}
                .header {{ background-color: #232F3E; color: white; padding: 20px; border-radius: 5px; text-align: center; }}
                .stat-box {{ display: inline-block; margin: 10px; padding: 20px; background: #f9f9f9; border-radius: 5px; text-align: center; }}
                .stat-number {{ font-size: 32px; font-weight: bold; color: #FF9900; }}
                .stat-label {{ font-size: 14px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>📊 Daily Job Scout Summary</h1>
                    <p>{datetime.now().strftime('%B %d, %Y')}</p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <div class="stat-box">
                        <div class="stat-number">{stats.get('total_jobs', 0)}</div>
                        <div class="stat-label">Total Jobs</div>
                    </div>
                    
                    <div class="stat-box">
                        <div class="stat-number">{stats.get('pending_analysis', 0)}</div>
                        <div class="stat-label">Pending Analysis</div>
                    </div>
                    
                    <div class="stat-box">
                        <div class="stat-number">{stats.get('high_priority', 0)}</div>
                        <div class="stat-label">High Priority</div>
                    </div>
                    
                    <div class="stat-box">
                        <div class="stat-number">{stats.get('applied', 0)}</div>
                        <div class="stat-label">Applied</div>
                    </div>
                </div>
                
                <p style="text-align: center; color: #666;">
                    Keep hunting! Your next opportunity is just around the corner. 🎯
                </p>
            </div>
        </body>
        </html>
        """
        
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = self.sender_email
        message['To'] = self.recipient_email
        
        message.attach(MIMEText(html, 'html'))
        
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, self.recipient_email, message.as_string())
            
            print("✅ Daily summary sent!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send summary: {str(e)[:80]}")
            return False


# Test
if __name__ == "__main__":
    print("="*70)
    print("EMAIL NOTIFIER TEST")
    print("="*70)
    
    try:
        notifier = EmailNotifier()
        
        # Test with sample jobs
        sample_jobs = [
            {
                'title': 'Data Analyst',
                'company': 'Amazon',
                'salary': '25-30 LPA',
                'location': 'Bangalore',
                'portal': 'LinkedIn',
                'url': 'https://example.com/job1',
                'ats_score': 85,
                'selection_chances': 'High'
            },
            {
                'title': 'Business Analyst',
                'company': 'Google',
                'salary': '28-35 LPA',
                'location': 'Hyderabad',
                'portal': 'Naukri',
                'url': 'https://example.com/job2',
                'ats_score': 78,
                'selection_chances': 'Medium'
            }
        ]
        
        print("\n📧 Sending test email...")
        success = notifier.send_job_alert(sample_jobs)
        
        if success:
            print("\n✅ Check your email inbox!")
        
    except ValueError as e:
        print(f"\n⚠️  {str(e)}")
        print("\n💡 To enable email notifications:")
        print("   1. Add YOUR_EMAIL to .env")
        print("   2. Generate Gmail App Password")
        print("   3. Add EMAIL_APP_PASSWORD to .env")
        print("\n   For now, you can skip email notifications.")
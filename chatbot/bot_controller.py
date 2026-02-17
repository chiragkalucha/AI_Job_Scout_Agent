# chatbot/bot_controller.py - UPDATED Bot Controller

import os
import sys
from PyQt5.QtCore import QObject, pyqtSignal

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(PROJECT_ROOT)

from chatbot.nlp_processor import NLPProcessor, Intent
from chatbot.hunt_manager import HuntManager
from chatbot.config_manager import ConfigManager


class BotController(QObject):
    """Main bot controller - UPDATED"""
    
    # Signals
    status_changed = pyqtSignal(str)
    hunt_started = pyqtSignal()
    hunt_completed = pyqtSignal(int)
    hunt_failed = pyqtSignal(str)
    progress_update = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        self.nlp = NLPProcessor()
        self.hunt_manager = HuntManager()
        self.config = ConfigManager()
        
        # Connect hunt manager signals
        self.hunt_manager.hunt_started.connect(self.hunt_started)
        self.hunt_manager.hunt_completed.connect(self.on_hunt_completed)
        self.hunt_manager.hunt_failed.connect(self.on_hunt_failed)
        self.hunt_manager.progress_update.connect(self.progress_update)
        
        print("Bot controller initialized")
    
    def process_command(self, text):
        """Process user command"""
        
        intent = self.nlp.detect_intent(text)
        
        print(f"Command: '{text}' → Intent: {intent.value}")
        
        # Route to handler
        handlers = {
            Intent.START_HUNT: self.handle_start_hunt,
            Intent.STOP_HUNT: self.handle_stop_hunt,
            Intent.CHANGE_SALARY: self.handle_change_salary,
            Intent.CHANGE_ROLES: self.handle_change_roles,
            Intent.ADD_ROLE: self.handle_add_role,
            Intent.REMOVE_ROLE: self.handle_remove_role,
            Intent.CLEAN_JOBS: self.handle_clean_jobs,
            Intent.OPEN_SHEET: self.handle_open_sheet,
            Intent.SHOW_STATUS: self.handle_show_status,
            Intent.HELP: self.handle_help,
        }
        
        handler = handlers.get(intent, self.handle_unknown)
        return handler(text)
    
    def handle_start_hunt(self, text):
        """Start continuous hunting"""
        
        if self.hunt_manager.should_continue:
            return ("✅ **Continuous hunting is already active!**\n\n"
                    "Running every 30 minutes.\n"
                    "Say 'stop hunt' to disable.")
        
        # Start continuous hunt
        success = self.hunt_manager.start_continuous_hunt()
        
        if success:
            self.status_changed.emit("🟢 Hunting (Continuous)")
            
            return ("🔄 **CONTINUOUS HUNTING ACTIVATED!**\n\n"
                    "✅ Running NOW\n"
                    "✅ Will repeat every 30 minutes\n"
                    "✅ Continues until you say 'stop hunt'\n\n"
                    "Starting first hunt now...")
        else:
            return "❌ Failed to start hunt"
    
    def handle_stop_hunt(self, text):
        """Stop hunting"""
        
        if not self.hunt_manager.should_continue and not self.hunt_manager.is_running:
            return "ℹ️ **No hunt is currently running.**\n\nSay 'start hunt' to begin."
        
        success = self.hunt_manager.stop_hunt()
        
        if success:
            self.status_changed.emit("🔴 Idle")
            
            return ("⏹️ **HUNTING FULLY STOPPED!**\n\n"
                    "❌ Current hunt cancelled\n"
                    "❌ Continuous mode disabled\n"
                    "❌ No more automatic hunts\n\n"
                    "Say 'start hunt' to resume.")
        else:
            return "❌ Failed to stop hunt"
    
    def handle_change_salary(self, text):
        """Change minimum salary"""
        
        salary = self.nlp.extract_number(text)
        
        if salary:
            success = self.config.set_salary(salary)
            
            if success:
                return f"✅ **Minimum salary updated!**\n\nNew value: {salary} LPA"
            else:
                return "❌ Failed to update salary"
        else:
            current = self.config.get_salary()
            return (f"📝 Current salary: {current} LPA\n\n"
                    f"Please specify new salary.\n"
                    f"Example: 'change salary to 25'")
    
    def handle_change_roles(self, text):
        """Change job roles"""
        
        roles = self.nlp.extract_roles(text)
        
        if roles:
            success = self.config.set_roles(roles)
            
            if success:
                roles_str = ', '.join(roles)
                return f"✅ **Job roles updated!**\n\nNew roles:\n{roles_str}"
            else:
                return "❌ Failed to update roles"
        else:
            current = self.config.get_roles()
            current_str = ', '.join(current)
            return (f"📝 Current roles:\n{current_str}\n\n"
                    f"Please specify new roles.\n"
                    f"Example: 'change roles to Data Analyst, ML Engineer'")
    
    def handle_add_role(self, text):
        """Add new role"""
        
        roles = self.nlp.extract_roles(text)
        
        if roles:
            added = []
            for role in roles:
                if self.config.add_role(role):
                    added.append(role)
            
            if added:
                added_str = ', '.join(added)
                all_roles = ', '.join(self.config.get_roles())
                return (f"✅ **Role(s) added!**\n\n"
                        f"Added: {added_str}\n\n"
                        f"All roles:\n{all_roles}")
            else:
                return "ℹ️ Role(s) already exist"
        else:
            return ("📝 Please specify role to add.\n\n"
                    "Example: 'add Data Scientist'")
    
    def handle_remove_role(self, text):
        """Remove role"""
        
        roles = self.nlp.extract_roles(text)
        
        if roles:
            removed = []
            for role in roles:
                if self.config.remove_role(role):
                    removed.append(role)
            
            if removed:
                removed_str = ', '.join(removed)
                all_roles = ', '.join(self.config.get_roles())
                return (f"✅ **Role(s) removed!**\n\n"
                        f"Removed: {removed_str}\n\n"
                        f"Remaining roles:\n{all_roles}")
            else:
                return "ℹ️ Role(s) not found"
        else:
            current = ', '.join(self.config.get_roles())
            return (f"📝 Current roles:\n{current}\n\n"
                    "Specify role to remove.\n"
                    "Example: 'remove Business Analyst'")
    
    def handle_clean_jobs(self,text):
        """Clean checked jobs"""
        
        try:
            from sheets_integration.sheets_updater import GoogleSheetsUpdater
            from dotenv import load_dotenv
            
            load_dotenv(os.path.join(PROJECT_ROOT, 'config', '.env'))
            
            updater = GoogleSheetsUpdater()
            updater.delete_checked_jobs()
            
            return "✅ **Checked jobs removed!**\n\nSheet has been cleaned."
        
        except Exception as e:
            return f"❌ **Cleanup failed**\n\nError: {str(e)[:100]}"
        
    def handle_open_sheet(self,text):
        """Open Google Sheet"""
        
        try:
            import webbrowser
            
            sheet_id = self.config.get_value('GOOGLE_SHEET_ID')
            
            if sheet_id:
                url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
                webbrowser.open(url)
                return "📊 **Opening Google Sheet...**\n\nSheet opened in browser!"
            else:
                return "❌ **Sheet not configured**\n\nAdd GOOGLE_SHEET_ID to config/.env"
        
        except Exception as e:
            return f"❌ **Error**\n\n{str(e)}"
        
    def handle_show_status(self,text):
        """Show status"""
        
        min_sal = self.config.get_salary()
        roles = ', '.join(self.config.get_roles())
        
        status = "📊 **CURRENT STATUS**\n\n"
        
        # Mode
        if self.hunt_manager.is_running and self.hunt_manager.should_continue:
            status += "🟢 Mode: **CONTINUOUS HUNTING**\n"
            status += "   (Running + every 30 min)\n\n"
        elif self.hunt_manager.is_running:
            status += "🟡 Mode: **HUNT IN PROGRESS**\n\n"
        elif self.hunt_manager.should_continue:
            status += "🔵 Mode: **WAITING FOR NEXT HUNT**\n"
            status += "   (Next in 30 min)\n\n"
        else:
            status += "🔴 Mode: **IDLE**\n\n"
        
        status += f"⚙️ **SETTINGS:**\n"
        status += f"• Min Salary: {min_sal} LPA\n"
        status += f"• Job Roles:\n  {roles}\n"
        
        return status
        
    def handle_help(self,text):
        """Show help"""
        
        return """📚 **AVAILABLE COMMANDS**

🚀 **HUNTING:**
- "start hunt" → Continuous (every 30 min)
- "stop hunt" → Stop completely

⚙️ **SETTINGS:**
- "change salary to X" → Update salary
- "change roles to X, Y" → Replace roles
- "add ROLE" → Add new role
- "remove ROLE" → Remove role

📊 **DATA:**
- "clean jobs" → Remove checked rows
- "open sheet" → View Google Sheet
- "status" → Show settings

💡 **TIP:** Type naturally!
        """
    
    def handle_unknown(self,text):
        """Unknown command"""
        
        return """❓ **I didn't understand that.**

Try:
- "start hunt" - Begin hunting
- "stop hunt" - Stop hunting
- "status" - View settings
- "help" - See all commands
        """
    
    def on_hunt_completed(self, jobs_count):
        """Forward hunt completed signal"""
        self.hunt_completed.emit(jobs_count)
    
    def on_hunt_failed(self, error):
        """Forward hunt failed signal"""
        self.hunt_failed.emit(error)
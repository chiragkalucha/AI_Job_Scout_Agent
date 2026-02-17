# chatbot/system_tray.py - System tray integration

import sys
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class SystemTrayIcon(QSystemTrayIcon):
    """System tray icon"""
    
    def __init__(self, chat_window, bot_controller, parent=None):
        
        # Create icon
        icon = QApplication.style().standardIcon(QApplication.style().SP_MessageBoxInformation)
        
        super().__init__(icon, parent)
        
        self.chat_window = chat_window
        self.bot_controller = bot_controller
        
        # Create menu
        self.create_menu()
        
        # Set tooltip
        self.setToolTip("AI Job Scout - Click to open chat")
        
        # Connect signals
        self.activated.connect(self.on_activated)
        self.bot_controller.hunt_completed.connect(self.on_hunt_completed)
        self.bot_controller.status_changed.connect(self.update_tooltip)
        
        # Show icon
        self.show()
    
    def create_menu(self):
        """Create context menu"""
        
        menu = QMenu()
        
        # Header
        header = QAction("🤖 AI Job Scout", menu)
        header.setEnabled(False)
        menu.addAction(header)
        
        menu.addSeparator()
        
        # Open chat
        open_action = QAction("💬 Open Chat", menu)
        open_action.triggered.connect(self.show_chat)
        menu.addAction(open_action)
        
        menu.addSeparator()
        
        # Quick actions
        start_action = QAction("▶️ Start Hunt", menu)
        start_action.triggered.connect(lambda: self.quick_command("start hunt"))
        menu.addAction(start_action)
        
        stop_action = QAction("⏹️ Stop Hunt", menu)
        stop_action.triggered.connect(lambda: self.quick_command("stop hunt"))
        menu.addAction(stop_action)
        
        clean_action = QAction("🗑️ Clean Jobs", menu)
        clean_action.triggered.connect(lambda: self.quick_command("clean jobs"))
        menu.addAction(clean_action)
        
        menu.addSeparator()
        
        # Exit
        exit_action = QAction("❌ Exit", menu)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)
        
        self.setContextMenu(menu)
    
    def on_activated(self, reason):
        """Handle tray icon activation"""
        
        if reason == QSystemTrayIcon.Trigger:
            # Left click - open chat
            self.show_chat()
    
    def show_chat(self):
        """Show chat window"""
        
        self.chat_window.show()
        self.chat_window.raise_()
        self.chat_window.activateWindow()
    
    def quick_command(self, command):
        """Execute quick command"""
        
        response = self.bot_controller.process_command(command)
        
        if response:
            # Show notification
            self.showMessage(
                "AI Job Scout",
                response.replace('**', '').replace('*', '')[:100],
                QSystemTrayIcon.Information,
                3000
            )
    
    def on_hunt_completed(self, jobs_count):
        """Show notification when hunt completes"""
        
        self.showMessage(
            "🎉 Hunt Completed!",
            f"Found {jobs_count} new jobs!\n\nClick to view details.",
            QSystemTrayIcon.Information,
            5000
        )
    
    def update_tooltip(self, status):
        """Update tooltip"""
        
        self.setToolTip(f"AI Job Scout - {status}")
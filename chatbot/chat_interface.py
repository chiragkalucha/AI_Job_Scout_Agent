# chatbot/chat_interface.py - Professional Chat Interface

import sys
import os
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ChatBubble(QWidget):
    """Individual chat bubble"""
    
    def __init__(self, message, is_bot=True):
        super().__init__()
        
        layout = QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Message label
        label = QLabel(message)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        label.setFont(QFont("Segoe UI", 10))
        label.setMaximumWidth(400)
        
        if is_bot:
            # Bot message (left, blue)
            label.setStyleSheet("""
                QLabel {
                    background-color: #E3F2FD;
                    border-radius: 15px;
                    padding: 12px 16px;
                    color: #1565C0;
                }
            """)
            layout.addWidget(label)
            layout.addStretch()
        else:
            # User message (right, green)
            label.setStyleSheet("""
                QLabel {
                    background-color: #C8E6C9;
                    border-radius: 15px;
                    padding: 12px 16px;
                    color: #2E7D32;
                }
            """)
            layout.addStretch()
            layout.addWidget(label)
        
        self.setLayout(layout)


class QuickActionButton(QPushButton):
    """Styled quick action button"""
    
    def __init__(self, text, command):
        super().__init__(text)
        self.command = command
        
        self.setStyleSheet("""
            QPushButton {
                background: #FFFFFF;
                border: 2px solid #2196F3;
                border-radius: 8px;
                padding: 10px 16px;
                font-size: 11px;
                font-weight: bold;
                color: #2196F3;
            }
            QPushButton:hover {
                background: #E3F2FD;
            }
            QPushButton:pressed {
                background: #BBDEFB;
            }
        """)
        
        self.setMinimumHeight(40)


class ChatInterface(QMainWindow):
    """Main chat interface"""
    
    # Signals
    command_signal = pyqtSignal(str)
    
    def __init__(self, bot_controller):
        super().__init__()
        
        self.bot_controller = bot_controller
        
        self.setWindowTitle("AI Job Scout - Chat Assistant")
        self.setGeometry(300, 100, 550, 750)
        
        
        
        # Window style
        self.setStyleSheet("""
            QMainWindow {
                background-color: #F5F5F5;
            }
        """)
        
        # Central widget
        central = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Chat area
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setStyleSheet("border: none; background: #F5F5F5;")
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.chat_widget = QWidget()
        self.chat_layout = QVBoxLayout()
        self.chat_layout.setSpacing(8)
        self.chat_layout.setContentsMargins(10, 10, 10, 10)
        self.chat_layout.addStretch()
        self.chat_widget.setLayout(self.chat_layout)
        
        self.chat_scroll.setWidget(self.chat_widget)
        layout.addWidget(self.chat_scroll)
        
        # Quick actions
        actions = self.create_quick_actions()
        layout.addWidget(actions)
        
        # Input area
        input_area = self.create_input_area()
        layout.addWidget(input_area)
        
        central.setLayout(layout)
        self.setCentralWidget(central)
        
        # Connect bot signals
        self.bot_controller.hunt_completed.connect(self.on_hunt_completed)
        self.bot_controller.hunt_failed.connect(self.on_hunt_failed)
        self.bot_controller.status_changed.connect(self.on_status_changed)
        self.bot_controller.progress_update.connect(self.on_progress_update) 
        
        # Welcome message
        self.add_bot_message(
            "👋 **Hello! I'm your AI Job Scout Assistant.**\n\n"
            "I can help you:\n"
            "• 🚀 Start/stop continuous job hunting\n"
            "• ⚙️ Change salary and role preferences\n"
            "• 📊 Manage your job listings\n"
            "• 🗑️ Clean checked jobs\n\n"
            "Just type naturally or use the buttons below!"
        )
    def on_progress_update(self, message):
        """Show progress update"""
        
        # Update status label
        clean_msg = message.replace('🚀', '').replace('📝', '').replace('⏳', '').strip()
        self.status_label.setText(f"🟢 {clean_msg[:50]}")
    def create_header(self):
        """Create header bar"""
        
        header = QWidget()
        header.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                            stop:0 #2196F3, stop:1 #1976D2);
                padding: 0px;
            }
        """)
        header.setFixedHeight(90)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Icon
        icon_label = QLabel("🤖")
        icon_label.setFont(QFont("Segoe UI", 28))
        layout.addWidget(icon_label)
        
        # Title and status
        text_layout = QVBoxLayout()
        text_layout.setSpacing(4)
        
        title = QLabel("AI Job Scout Assistant")
        title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        title.setStyleSheet("color: white;")
        text_layout.addWidget(title)
        
        self.status_label = QLabel("🔴 Idle - Ready to hunt")
        self.status_label.setFont(QFont("Segoe UI", 11))
        self.status_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        text_layout.addWidget(self.status_label)
        
        layout.addLayout(text_layout)
        layout.addStretch()
        
        header.setLayout(layout)
        return header
    
    def create_quick_actions(self):
        """Create quick action buttons"""
        
        widget = QWidget()
        widget.setStyleSheet("background: white; border-top: 1px solid #E0E0E0;")
        
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 12, 15, 12)
        layout.setSpacing(8)
        
        # Title
        title = QLabel("⚡ Quick Actions:")
        title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        title.setStyleSheet("color: #757575;")
        layout.addWidget(title)
        
        # Buttons grid
        grid = QGridLayout()
        grid.setSpacing(8)
        
        buttons = [
            ("▶️ Start Hunt", "start hunt"),
            ("⏹️ Stop Hunt", "stop hunt"),
            ("📊 Open Sheet", "open sheet"),
            ("🗑️ Clean Jobs", "clean jobs"),
            ("💰 Change Salary", "change salary"),
            ("📋 Show Status", "status")
        ]
        
        for idx, (text, command) in enumerate(buttons):
            btn = QuickActionButton(text, command)
            btn.clicked.connect(lambda checked, cmd=command: self.send_quick_command(cmd))
            row = idx // 2
            col = idx % 2
            grid.addWidget(btn, row, col)
        
        layout.addLayout(grid)
        
        widget.setLayout(layout)
        return widget
    
    def create_input_area(self):
        """Create input area"""
        
        widget = QWidget()
        widget.setStyleSheet("background: white; border-top: 2px solid #E0E0E0;")
        widget.setFixedHeight(80)
        
        layout = QHBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Input field
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.setFont(QFont("Segoe UI", 12))
        self.input_field.setStyleSheet("""
            QLineEdit {
                border: 2px solid #E0E0E0;
                border-radius: 25px;
                padding: 12px 20px;
                background: #FAFAFA;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
                background: white;
            }
        """)
        self.input_field.returnPressed.connect(self.on_send)
        layout.addWidget(self.input_field)
        
        # Send button
        send_btn = QPushButton("Send")
        send_btn.setFixedSize(90, 50)
        send_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        send_btn.setStyleSheet("""
            QPushButton {
                background: #2196F3;
                color: white;
                border: none;
                border-radius: 25px;
            }
            QPushButton:hover {
                background: #1976D2;
            }
            QPushButton:pressed {
                background: #1565C0;
            }
        """)
        send_btn.clicked.connect(self.on_send)
        layout.addWidget(send_btn)
        
        widget.setLayout(layout)
        return widget
    
    def add_bot_message(self, text):
        """Add bot message"""
        
        bubble = ChatBubble(text, is_bot=True)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        self.scroll_to_bottom()
    
    def add_user_message(self, text):
        """Add user message"""
        
        bubble = ChatBubble(text, is_bot=False)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble)
        self.scroll_to_bottom()
    
    def scroll_to_bottom(self):
        """Scroll chat to bottom"""
        QTimer.singleShot(100, lambda: self.chat_scroll.verticalScrollBar().setValue(
            self.chat_scroll.verticalScrollBar().maximum()
        ))
    
    def on_send(self):
        """Handle send button"""
        
        message = self.input_field.text().strip()
        
        if not message:
            return
        
        self.add_user_message(message)
        self.input_field.clear()
        
        # Process command
        response = self.bot_controller.process_command(message)
        
        if response:
            QTimer.singleShot(500, lambda: self.add_bot_message(response))
    
    def send_quick_command(self, command):
        """Send quick action command"""
        
        self.add_user_message(command)
        
        response = self.bot_controller.process_command(command)
        
        if response:
            QTimer.singleShot(500, lambda: self.add_bot_message(response))
    
    def on_hunt_completed(self, jobs_count):
        """Hunt completed notification"""
        
        message = f"🎉 **Hunt completed!**\n\nFound {jobs_count} new jobs!"
        
        if jobs_count > 0:
            message += "\n\nCheck your Google Sheet to view them."
        
        self.add_bot_message(message)
    
    def on_hunt_failed(self, error):
        """Hunt failed notification"""
        
        self.add_bot_message(f"❌ **Hunt failed**\n\nError: {error}")
    
    def on_status_changed(self, status):
        """Update status label"""
        
        self.status_label.setText(status)
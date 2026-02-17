# chatbot/main_app.py - Main application entry point

import sys
import os

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(PROJECT_ROOT)  # ← THIS IS THE KEY FIX

# Add to path
sys.path.insert(0, PROJECT_ROOT)

print(f"Working directory set to: {PROJECT_ROOT}")


from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt

from chatbot.bot_controller import BotController
from chatbot.chat_interface import ChatInterface
from chatbot.system_tray import QSystemTrayIcon
from chatbot.system_tray import SystemTrayIcon



def main():
    """Main entry point"""
    
    print("="*70)
    print("AI JOB SCOUT - STARTING")
    print("="*70)
    print()
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("AI Job Scout")
    app.setQuitOnLastWindowClosed(False)
    
    # Check system tray availability
    if not QSystemTrayIcon.isSystemTrayAvailable():
        QMessageBox.critical(
            None,
            "System Tray Not Available",
            "System tray is required for this application.\n\n"
            "Please enable system tray and try again."
        )
        return 1
    
    print("✅ System tray available")
    
    # Create bot controller
    bot_controller = BotController()
    print("✅ Bot controller initialized")
    
    # Create chat interface
    chat_window = ChatInterface(bot_controller)
    print("✅ Chat interface created")
    
    # Create system tray
    tray_icon = SystemTrayIcon(chat_window, bot_controller)
    print("✅ System tray icon created")
    
    # Show startup notification
    tray_icon.showMessage(
        "🤖 AI Job Scout Started",
        "Click the icon to open chat!\n\nReady to hunt for jobs.",
        QSystemTrayIcon.Information,
        4000
    )
    
    # Show chat window initially
    chat_window.show()
    
    print()
    print("="*70)
    print("APPLICATION RUNNING")
    print("="*70)
    print()
    print("💡 Click the system tray icon to open chat")
    print("💡 Right-click for quick actions")
    print("💡 Close window to minimize to tray")
    print()
    
    # Run application
    return app.exec_()


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nStopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
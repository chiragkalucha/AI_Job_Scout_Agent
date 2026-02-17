# launch_chatbot.py - Proper Launcher (No Terminal Freeze)

import subprocess
import sys
import os
import time

print("="*70)
print("🤖 AI JOB SCOUT - CHATBOT LAUNCHER")
print("="*70)
print()

# Get pythonw path (runs without console window)
if hasattr(sys, 'base_prefix'):
    pythonw = os.path.join(sys.base_prefix, 'pythonw.exe')
else:
    pythonw = os.path.join(sys.prefix, 'pythonw.exe')

# Fallback to regular python if pythonw not found
if not os.path.exists(pythonw):
    pythonw = sys.executable
    print("⚠️  pythonw.exe not found, using python.exe")
else:
    print(f"✅ Using: {pythonw}")

# Path to chatbot script
chatbot_script = os.path.join(os.path.dirname(__file__), 'chatbot', 'system_tray_agent.py')

print(f"📁 Chatbot script: {chatbot_script}")
print()

# Check if chatbot file exists
if not os.path.exists(chatbot_script):
    print(f"❌ Error: Chatbot script not found!")
    print(f"   Expected: {chatbot_script}")
    input("\nPress Enter to exit...")
    sys.exit(1)

print("🚀 Launching chatbot as separate process...")
print()

try:
    # Launch chatbot as DETACHED process
    if os.name == 'nt':  # Windows
        # Use CREATE_NEW_CONSOLE and DETACHED_PROCESS
        DETACHED_PROCESS = 0x00000008
        CREATE_NO_WINDOW = 0x08000000
        
        process = subprocess.Popen(
            [pythonw, chatbot_script],
            creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL
        )
        
        print("✅ Chatbot launched successfully!")
        print()
        print("="*70)
        print("CHATBOT IS NOW RUNNING IN BACKGROUND")
        print("="*70)
        print()
        print("📍 WHERE TO FIND IT:")
        print("   1. Look at bottom-right corner of screen")
        print("   2. Find the system tray (near the clock)")
        print("   3. Click the UP ARROW (^) to show hidden icons")
        print("   4. You should see the chatbot icon there")
        print()
        print("🖱️  HOW TO USE:")
        print("   • Right-click icon → See menu")
        print("   • Double-click icon → Start hunting")
        print("   • Select 'Test Notification' to verify it works")
        print()
        print("⏹️  TO STOP CHATBOT:")
        print("   • Right-click icon → Exit")
        print("   OR")
        print("   • Open Task Manager → End 'pythonw.exe'")
        print()
        print("="*70)
        print()
        
        # Wait to see if it crashes immediately
        time.sleep(2)
        
        # Check if still running
        if process.poll() is None:
            print("✅ Chatbot is running (PID: {})".format(process.pid))
            print()
            print("This window will close in 3 seconds...")
            time.sleep(3)
        else:
            print("❌ Chatbot crashed immediately!")
            print("   Check if PyQt5 is installed: pip install PyQt5")
            input("\nPress Enter to exit...")
            sys.exit(1)
        
    else:  # Linux/Mac
        process = subprocess.Popen(
            [pythonw, chatbot_script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )
        
        print("✅ Chatbot launched!")
        time.sleep(2)
    
except Exception as e:
    print(f"❌ Error launching chatbot: {e}")
    print()
    print("💡 Troubleshooting:")
    print("   1. Make sure PyQt5 is installed: pip install PyQt5")
    print("   2. Try running directly: python chatbot/system_tray_agent.py")
    print("   3. Check for error messages above")
    input("\nPress Enter to exit...")
    sys.exit(1)
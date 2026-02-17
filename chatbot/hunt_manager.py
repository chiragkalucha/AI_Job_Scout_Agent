# chatbot/hunt_manager.py - Manages continuous job hunting

import os
import io
import sys
import subprocess
import threading
import time
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class HuntManager(QObject):
    """Manages continuous job hunting execution"""
    
    hunt_started = pyqtSignal()
    hunt_completed = pyqtSignal(int)
    hunt_failed = pyqtSignal(str)
    progress_update = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        self.is_running = False
        self.should_continue = False
        self.hunt_thread = None
        self.current_process = None
        
        print("Hunt Manager initialized")
    
    def start_continuous_hunt(self):
        """Start continuous hunting (runs every 30 min)"""
        
        if self.is_running:
            print("Hunt already running")
            return False
        
        self.should_continue = True
        
        # Start hunt thread
        self.hunt_thread = threading.Thread(target=self._hunt_loop, daemon=True)
        self.hunt_thread.start()
        
        print("Continuous hunt started")
        return True
    
    def stop_hunt(self):
        """Stop continuous hunting"""
        
        print("Stopping hunt...")
        
        # Stop the loop
        self.should_continue = False
        
        # Kill current process if running
        if self.current_process:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=5)
            except:
                try:
                    self.current_process.kill()
                except:
                    pass
            
            self.current_process = None
        
        self.is_running = False
        
        print("Hunt stopped")
        return True
    
    def _hunt_loop(self):
        """Main hunt loop - runs continuously"""
        
        print("Hunt loop started")
        
        while self.should_continue:
            # Run one hunt
            self._run_single_hunt()
            
            # If should continue, wait 30 minutes
            if self.should_continue:
                print("Waiting 30 minutes until next hunt...")
                self.progress_update.emit("⏳ Waiting 30 min for next hunt...")
                
                # Wait in 1-second intervals (so we can stop quickly)
                for i in range(1800):  # 1800 seconds = 30 minutes
                    if not self.should_continue:
                        print("Hunt stopped during wait period")
                        break
                    time.sleep(1)
        
        print("Hunt loop ended")
    
    # chatbot/hunt_manager.py
# Find _run_single_hunt method and update:

    def _run_single_hunt(self):
        """Run single hunt - SHORTCUT SAFE"""
        
        self.is_running = True
        self.hunt_started.emit()
        
        print(f"Starting hunt at {datetime.now().strftime('%H:%M:%S')}")
        self.progress_update.emit(f"Starting hunt...")
        
        try:
            # ✅ FIX: Use ABSOLUTE paths (works from any working directory)
            script_path = os.path.join(PROJECT_ROOT, 'main_subprocess.py')
            
            if not os.path.exists(script_path):
                script_path = os.path.join(PROJECT_ROOT, 'main.py')
            
            if not os.path.exists(script_path):
                self.hunt_failed.emit(f"Script not found: {script_path}")
                return
            
            print(f"PROJECT_ROOT: {PROJECT_ROOT}")
            print(f"Script: {script_path}")
            self.progress_update.emit(f"Running from: {PROJECT_ROOT}")
            
            # ✅ FIX: Set environment
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'
            env['PYTHONPATH'] = PROJECT_ROOT
            
            self.current_process = subprocess.Popen(
                [sys.executable, '-X', 'utf8', script_path],
                cwd=PROJECT_ROOT,          # ✅ EXPLICIT absolute cwd
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                errors='replace',
                bufsize=1,
                env=env
            )
            
            # Read output
            output_lines = []
            
            for line in iter(self.current_process.stdout.readline, ''):
                if not self.should_continue:
                    self.current_process.terminate()
                    break
                if line:
                    line = line.rstrip()
                    output_lines.append(line)
                    import re
                    clean = re.sub(r'[^\x00-\x7F]+', '', line)
                    if any(k in clean for k in ['STEP', 'Step', 'Found', 'jobs', 'ERROR', 'Starting', 'Complete']):
                        self.progress_update.emit(clean[:100])
                        print(f"  {clean}")
            
            self.current_process.wait(timeout=1800)
            full_output = '\n'.join(output_lines)
            
            if self.current_process.returncode != 0:
                error_lines = [l for l in output_lines[-10:] if l.strip()]
                error_msg = ' | '.join(error_lines[-3:]) if error_lines else f"Exit code {self.current_process.returncode}"
                self.hunt_failed.emit(error_msg[:200])
            else:
                import re
                jobs_found = 0
                for pattern in [r'(\d+)\s+NEW\s+jobs', r'(\d+)\s+jobs\s+added', r'COMPLETE.*?(\d+)']:
                    matches = re.findall(pattern, full_output, re.IGNORECASE)
                    if matches:
                        jobs_found = int(matches[-1])
                        break
                self.hunt_completed.emit(jobs_found)
                print(f"Hunt completed: {jobs_found} jobs")
        
        except subprocess.TimeoutExpired:
            if self.current_process:
                self.current_process.kill()
            self.hunt_failed.emit("Hunt timeout (30 min)")
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            self.hunt_failed.emit(str(e)[:150])
        
        finally:
            self.current_process = None
            self.is_running = False
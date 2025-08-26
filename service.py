#!/usr/bin/env python3
"""
PDF-to-Text Service Manager
Simple service management for Docker containers and servers without systemd
"""

import os
import sys
import signal
import subprocess
import time
import argparse
from pathlib import Path

class ServiceManager:
    def __init__(self):
        self.pid_file = Path("logs/app.pid")
        self.log_file = Path("logs/app.log")
        self.app_script = "main.py"
        
        # Ensure logs directory exists
        self.log_file.parent.mkdir(exist_ok=True)
    
    def start(self):
        """Start the service"""
        if self.is_running():
            print("❌ Service is already running!")
            return False
        
        print("🚀 Starting PDF-to-Text API...")
        
        # Start the process
        with open(self.log_file, 'w') as log:
            process = subprocess.Popen(
                [sys.executable, self.app_script],
                stdout=log,
                stderr=subprocess.STDOUT,
                cwd=os.getcwd()
            )
        
        # Save PID
        with open(self.pid_file, 'w') as f:
            f.write(str(process.pid))
        
        # Wait a moment to check if it started successfully
        time.sleep(2)
        if self.is_running():
            print(f"✅ Service started successfully!")
            print(f"📋 Process ID: {process.pid}")
            print(f"📁 Log file: {self.log_file}")
            print(f"🌐 API: http://localhost:8000")
            print(f"📖 Docs: http://localhost:8000/docs")
            return True
        else:
            print("❌ Failed to start service")
            return False
    
    def stop(self):
        """Stop the service"""
        if not self.pid_file.exists():
            print("⚠️  No PID file found")
            return self._kill_by_name()
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            print(f"🛑 Stopping service (PID: {pid})...")
            
            # Try graceful shutdown first
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(2)
                
                # Check if still running
                try:
                    os.kill(pid, 0)  # Check if process exists
                    print("⚠️  Process still running, forcing shutdown...")
                    os.kill(pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass  # Process already stopped
                    
            except ProcessLookupError:
                print("⚠️  Process not found")
            
            # Clean up PID file
            self.pid_file.unlink()
            print("✅ Service stopped successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Error stopping service: {e}")
            return self._kill_by_name()
    
    def _kill_by_name(self):
        """Kill process by name as fallback"""
        try:
            subprocess.run(["pkill", "-f", "python main.py"], check=False)
            print("✅ Killed processes by name")
            return True
        except:
            print("⚠️  Could not kill processes by name")
            return False
    
    def status(self):
        """Check service status"""
        print("📊 PDF-to-Text API Status")
        print("=" * 30)
        
        if self.is_running():
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            print("✅ Status: RUNNING")
            print(f"📋 Process ID: {pid}")
            
            # Get process info if possible
            try:
                result = subprocess.run(
                    ["ps", "-o", "pid,vsz,rss,etime,comm", "-p", str(pid)],
                    capture_output=True, text=True, check=False
                )
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if len(lines) > 1:
                        print(f"💾 Process info: {lines[1]}")
            except:
                pass
        else:
            print("❌ Status: STOPPED")
        
        # Log file info
        if self.log_file.exists():
            size = self.log_file.stat().st_size
            print(f"📁 Log file: {self.log_file} ({size} bytes)")
        else:
            print("📁 Log file: Not found")
        
        print(f"🌐 API endpoint: http://localhost:8000")
        print(f"📖 API docs: http://localhost:8000/docs")
    
    def is_running(self):
        """Check if service is running"""
        if not self.pid_file.exists():
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, ValueError):
            # Clean up stale PID file
            if self.pid_file.exists():
                self.pid_file.unlink()
            return False
    
    def logs(self, follow=False):
        """Show logs"""
        if not self.log_file.exists():
            print("❌ Log file not found")
            return
        
        if follow:
            print(f"📄 Following logs from {self.log_file} (Ctrl+C to stop)...")
            try:
                subprocess.run(["tail", "-f", str(self.log_file)])
            except KeyboardInterrupt:
                print("\n👋 Stopped following logs")
        else:
            print(f"📄 Last 50 lines from {self.log_file}:")
            try:
                subprocess.run(["tail", "-50", str(self.log_file)])
            except:
                # Fallback to Python implementation
                with open(self.log_file, 'r') as f:
                    lines = f.readlines()
                    for line in lines[-50:]:
                        print(line.rstrip())

def main():
    parser = argparse.ArgumentParser(description='PDF-to-Text Service Manager')
    parser.add_argument('action', choices=['start', 'stop', 'restart', 'status', 'logs'],
                       help='Action to perform')
    parser.add_argument('-f', '--follow', action='store_true',
                       help='Follow logs (only with logs action)')
    
    args = parser.parse_args()
    service = ServiceManager()
    
    if args.action == 'start':
        service.start()
    elif args.action == 'stop':
        service.stop()
    elif args.action == 'restart':
        service.stop()
        time.sleep(1)
        service.start()
    elif args.action == 'status':
        service.status()
    elif args.action == 'logs':
        service.logs(follow=args.follow)

if __name__ == '__main__':
    main()

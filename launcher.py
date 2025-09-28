import sys
import os
import subprocess
import threading
import time
from pynput import keyboard
import psutil
import win32gui
import win32con

class DirectSearchLauncher:
    """Optimized launcher that keeps main app pre-loaded for instant activation"""
    
    def __init__(self):
        self.listener = None
        self.main_process = None
        self.is_main_app_ready = False
        self.activation_requested = False
        
    def start_listening(self):
        """Start listening for the hotkey and pre-load main app"""
        try:
            print("🚀 Direct Search Launcher Started")
            print("📋 Press Ctrl+Shift+Space to activate")
            print("⚡ Pre-loading main application for instant activation...")
            
            # Pre-load main app in background
            self.preload_main_app()
            
            def on_activate():
                print("🎯 Hotkey activated - showing overlay instantly")
                self.activate_main_app()
            
            # Global hotkey listener
            self.listener = keyboard.GlobalHotKeys({
                '<ctrl>+<shift>+<space>': on_activate
            })
            
            self.listener.start()
            print("✅ Hotkey listener active: Ctrl+Shift+Space")
            print("💡 Main app is pre-loaded and ready for instant activation")
            
            # Keep the launcher running
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                self.stop_listening()
                
        except Exception as e:
            print(f"❌ Launcher error: {e}")
    
    def preload_main_app(self):
        """Pre-load main app in background for instant activation"""
        try:
            print("🔄 Pre-loading main application...")
            
            # Determine the path to the main executable
            app_path = self.get_main_app_path()
            if not app_path:
                print("❌ Could not find main application")
                return
            
            # Start main app in hidden pre-load mode
            if app_path.endswith('.exe'):
                self.main_process = subprocess.Popen(
                    [app_path, "--preload"], 
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            else:
                self.main_process = subprocess.Popen(
                    [sys.executable, app_path, "--preload"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
            
            # Wait a bit for app to initialize
            time.sleep(3)
            self.is_main_app_ready = True
            print("✅ Main application pre-loaded and ready")
            
        except Exception as e:
            print(f"❌ Failed to pre-load main app: {e}")
    
    def activate_main_app(self):
        """Activate the pre-loaded main app instantly"""
        if not self.is_main_app_ready or not self.main_process:
            print("⚠️ Main app not ready, launching fresh instance...")
            self.launch_fresh_instance()
            return
        
        try:
            # Send signal to show overlay (you'll need to implement this in main.py)
            # For now, we'll just bring the window to foreground if it exists
            self.bring_main_app_to_foreground()
            
        except Exception as e:
            print(f"❌ Failed to activate main app: {e}")
            self.launch_fresh_instance()
    
    def bring_main_app_to_foreground(self):
        """Bring main app window to foreground"""
        try:
            # Look for window with "Direct Search" in title
            def callback(hwnd, extra):
                if win32gui.IsWindowVisible(hwnd) and "Direct Search" in win32gui.GetWindowText(hwnd):
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    win32gui.SetForegroundWindow(hwnd)
                    return False
                return True
            
            win32gui.EnumWindows(callback, None)
        except Exception as e:
            print(f"⚠️ Could not bring window to foreground: {e}")
    
    def launch_fresh_instance(self):
        """Launch a fresh instance of main app"""
        try:
            app_path = self.get_main_app_path()
            if app_path:
                if app_path.endswith('.exe'):
                    subprocess.Popen([app_path, "--single-use"])
                else:
                    subprocess.Popen([sys.executable, app_path, "--single-use"])
                print("✅ Launched fresh instance")
        except Exception as e:
            print(f"❌ Failed to launch fresh instance: {e}")
    
    def get_main_app_path(self):
        """Get path to main application"""
        if getattr(sys, 'frozen', False):
            # Running as executable
            if os.path.exists("DirectSearch.exe"):
                return "DirectSearch.exe"
            else:
                base_dir = os.path.dirname(sys.executable)
                app_path = os.path.join(base_dir, "DirectSearch.exe")
                if os.path.exists(app_path):
                    return app_path
        else:
            # Running as script
            return "main.py"
        return None
    
    def stop_listening(self):
        """Stop the launcher and clean up"""
        if self.listener:
            self.listener.stop()
        if self.main_process:
            try:
                self.main_process.terminate()
            except:
                pass
        print("👋 Launcher stopped")

def main():
    # Check if another launcher is already running
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            if proc.info['pid'] != current_pid and 'DirectSearchLauncher' in proc.info['name']:
                print("⚠️ Another launcher is already running. Exiting.")
                return
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    launcher = DirectSearchLauncher()
    launcher.start_listening()

if __name__ == "__main__":
    main()
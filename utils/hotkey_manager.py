import threading
import time
from PySide6.QtCore import QObject, Signal, QTimer

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("[WARNING] pynput not available, using fallback method")

class GlobalHotkeyListener(QObject):
    """Global hotkey listener using pynput for system-wide shortcuts"""
    hotkey_pressed = Signal()

    def __init__(self):
        super().__init__()
        self.active = False
        self.listener = None

    def start_listening(self):
        """Start global hotkey listening"""
        if not PYNPUT_AVAILABLE:
            print("[ERROR] pynput not available for global hotkeys")
            return False
            
        if self.active:
            return True
            
        try:
            self.active = True
            listener_thread = threading.Thread(target=self._run_listener, daemon=True)
            listener_thread.start()
            print("[INFO] ✅ Global hotkeys started: Ctrl+Shift+Space and Ctrl+Alt+S")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to start global hotkeys: {e}")
            return False

    def _run_listener(self):
        """Run the global hotkey listener"""
        try:
            with keyboard.GlobalHotKeys({
                '<ctrl>+<shift>+<space>': self._on_hotkey,
                '<ctrl>+<alt>+s': self._on_hotkey
            }) as self.listener:
                while self.active:
                    time.sleep(0.1)
        except Exception as e:
            print(f"[ERROR] Hotkey listener error: {e}")

    def _on_hotkey(self):
        """Handle hotkey activation"""
        if self.active:
            print("[DEBUG] 🎯 Global hotkey activated!")
            self.hotkey_pressed.emit()

    def stop_listening(self):
        """Stop hotkey listening"""
        self.active = False
        if self.listener:
            try:
                self.listener.stop()
            except:
                pass

class FallbackHotkeyListener(QObject):
    """Fallback hotkey listener for when pynput is not available"""
    hotkey_pressed = Signal()

    def __init__(self):
        super().__init__()
        print("[INFO] ⚠️ Using fallback hotkey method - limited functionality")
        print("[INFO] Press F12 to activate capture instead")

    def start_listening(self):
        """Start fallback method"""
        return True
    
    def stop_listening(self):
        """Stop fallback listening"""
        pass

class HotkeyManager(QObject):
    """Manages hotkey functionality with fallback support"""
    
    hotkey_pressed = Signal()  # Define the signal at class level
    
    def __init__(self):
        super().__init__()
        if PYNPUT_AVAILABLE:
            self.listener = GlobalHotkeyListener()
        else:
            self.listener = FallbackHotkeyListener()
        
        # Connect the listener's signal to our signal
        self.listener.hotkey_pressed.connect(self.hotkey_pressed)
    
    def start_listening(self):
        """Start hotkey listening"""
        return self.listener.start_listening()
    
    def stop_listening(self):
        """Stop hotkey listening"""
        self.listener.stop_listening()
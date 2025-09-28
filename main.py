import sys
import os
import atexit
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLockFile, QDir

from core.direct_search_engine import DirectSearchEngine
from utils.hotkey_manager import HotkeyManager
from overlay import OverlayWindow

class DirectSearchApplication:
    """Main application controller for direct search functionality"""
    
    def __init__(self, app: QApplication):
        self.app = app
        print("[DEBUG] Initializing Direct Search Application...")
        
        # Core components
        self.search_engine = DirectSearchEngine()
        self.overlay = OverlayWindow()
        self.hotkey_manager = HotkeyManager()
        
        # Connect signals
        self.overlay.region_selected.connect(self.on_region_selected)
        self.hotkey_manager.hotkey_pressed.connect(self.handle_show_overlay)
        
        # Start hotkey listener
        self.hotkey_manager.start_listening()
        
        print("[DEBUG] Direct Search Application initialized!")

    def handle_show_overlay(self):
        """Show the capture overlay directly"""
        print("[DEBUG] 🎯 Showing overlay (direct hotkey)...")
        try:
            self.overlay.show_overlay()
            print("[DEBUG] Overlay activated via hotkey")
        except Exception as e:
            print(f"[ERROR] Failed to show overlay: {e}")

    def on_region_selected(self, rect):
        """Handle region selection with direct search"""
        print(f"[DEBUG] Region selected: {rect}")
        self.search_engine.process_selection(rect)

    def cleanup(self):
        """Cleanup resources"""
        self.search_engine.cleanup()
        self.hotkey_manager.stop_listening()

if __name__ == "__main__":
    print("🚀 Starting Direct Search Application")
    
    # Single instance lock
    lock_file = QLockFile(os.path.join(QDir.tempPath(), "direct-search-app.lock"))
    if not lock_file.tryLock(100):
        print("[ERROR] Another instance is already running.")
        sys.exit(0)
    
    # Create application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("Direct Search")

    # Create main controller
    main_controller = DirectSearchApplication(app)

    print("✨ Direct Search Application is ready!")
    print("📖 How to use:")
    print("   🎯 Press Ctrl+Shift+Space OR Ctrl+Alt+S to capture")
    print("   🔍 Text automatically searches on Google!")
    print("   🚀 Images automatically perform DIRECT upload to Google Lens!")
    print("   📋 Text is auto-copied to clipboard")
    print("   ❌ Press Ctrl+C in terminal to quit")
    
    # Ensure cleanup on exit
    atexit.register(main_controller.cleanup)

    # Start the application
    sys.exit(app.exec())
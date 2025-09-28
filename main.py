import sys
import os
import atexit
import time
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QIcon, QAction, QPixmap, QPainter
from PySide6.QtCore import QLockFile, QDir, Qt, QPoint, QTimer

class DirectSearchApplication:
    """Optimized main application with pre-load mode for instant activation"""
    
    def __init__(self, app: QApplication, single_use_mode=False, preload_mode=False):
        self.app = app
        self.single_use_mode = single_use_mode
        self.preload_mode = preload_mode
        self.overlay = None
        self.search_engine = None
        
        print(f"[DEBUG] Starting Direct Search Application... Mode: {'Preload' if preload_mode else 'Single-use' if single_use_mode else 'Legacy'}")
        
        if preload_mode:
            # Pre-load mode: initialize in background, wait for activation
            self.setup_preload_mode()
        elif single_use_mode:
            # Single-use mode: show overlay immediately
            self.setup_direct_mode()
        else:
            # Legacy mode with system tray
            self.setup_system_tray()
            self.setup_components()
    
    def setup_preload_mode(self):
        """Setup for pre-load mode - minimal initialization"""
        try:
            # Only import heavy modules when needed
            print("💤 Pre-load mode: Waiting for activation...")
            
            # Set up system tray to indicate ready state
            self.setup_minimal_tray()
            
            # Initialize core components but don't load heavy resources yet
            self.initialize_light_components()
            
        except Exception as e:
            print(f"[ERROR] Failed to setup preload mode: {e}")
    
    def setup_minimal_tray(self):
        """Setup minimal system tray for pre-load mode"""
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(self.create_default_icon())
        
        tray_menu = QMenu()
        activate_action = QAction("🚀 Activate Overlay", self.app)
        activate_action.triggered.connect(self.activate_from_tray)
        tray_menu.addAction(activate_action)
        
        exit_action = QAction("❌ Exit", self.app)
        exit_action.triggered.connect(self.cleanup_and_exit)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("Direct Search (Ready - Press Ctrl+Shift+Space)")
        self.tray_icon.show()
    
    def initialize_light_components(self):
        """Initialize only light components in pre-load mode"""
        # Import and create overlay (light component)
        from overlay import OverlayWindow
        self.overlay = OverlayWindow()
        self.overlay.region_selected.connect(self.on_region_selected)
        self.overlay.overlay_closed.connect(self.on_overlay_closed)
    
    def activate_from_tray(self):
        """Activate overlay from tray menu"""
        self.show_overlay_instantly()
    
    def show_overlay_instantly(self):
        """Show overlay instantly (for pre-load mode)"""
        try:
            if not self.overlay:
                from overlay import OverlayWindow
                self.overlay = OverlayWindow()
                self.overlay.region_selected.connect(self.on_region_selected)
                self.overlay.overlay_closed.connect(self.on_overlay_closed)
            
            print("🎯 Showing overlay instantly...")
            self.overlay.show_overlay()
            
        except Exception as e:
            print(f"[ERROR] Failed to show overlay: {e}")
    
    def setup_direct_mode(self):
        """Optimized setup for single-use mode"""
        try:
            # Lazy import heavy modules
            from overlay import OverlayWindow
            
            print("⚡ Fast startup: Initializing overlay only...")
            
            # Create overlay immediately (light component)
            self.overlay = OverlayWindow()
            self.overlay.region_selected.connect(self.on_region_selected)
            self.overlay.overlay_closed.connect(self.on_overlay_closed)
            
            # Show overlay instantly
            print("🎯 Showing overlay...")
            self.overlay.show_overlay()
            
            # Load search engine in background after overlay is shown
            QTimer.singleShot(100, self.initialize_search_engine)
            
        except Exception as e:
            print(f"[ERROR] Failed to setup direct mode: {e}")
            self.cleanup_and_exit()
    
    def initialize_search_engine(self):
        """Initialize search engine in background"""
        try:
            from core.direct_search_engine import DirectSearchEngine
            self.search_engine = DirectSearchEngine()
            print("✅ Search engine initialized in background")
        except Exception as e:
            print(f"[WARNING] Search engine initialization delayed: {e}")

    def on_region_selected(self, rect):
        """Handle region selection with optimized loading"""
        print(f"[DEBUG] Region selected: {rect}")
        
        # Ensure search engine is initialized
        if not self.search_engine:
            from core.direct_search_engine import DirectSearchEngine
            self.search_engine = DirectSearchEngine()
        
        if hasattr(self, 'search_engine'):
            self.search_engine.process_selection(rect)
            
            # In single-use mode, wait a bit then exit
            if self.single_use_mode:
                print("⏳ Search completed, app will close shortly...")
                QTimer.singleShot(2000, self.cleanup_and_exit)

    def on_overlay_closed(self):
        """Handle overlay closed without selection"""
        if self.single_use_mode:
            print("👋 Overlay closed without selection")
            self.cleanup_and_exit()
        elif self.preload_mode:
            print("💤 Returning to pre-load mode...")
            # Stay running in pre-load mode

    def create_default_icon(self):
        """Create default icon (for legacy mode)"""
        pixmap = QPixmap(64, 64)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(Qt.blue)
        painter.setPen(Qt.darkBlue)
        painter.drawEllipse(8, 8, 48, 48)
        painter.setBrush(Qt.white)
        painter.drawEllipse(16, 16, 32, 32)
        painter.setBrush(Qt.blue)
        painter.drawRect(40, 40, 20, 8)
        painter.end()
        return QIcon(pixmap)

    def setup_system_tray(self):
        """Setup system tray (legacy mode only)"""
        self.tray_icon = QSystemTrayIcon()
        
        icon_path = self.get_icon_path()
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            self.tray_icon.setIcon(self.create_default_icon())
        
        tray_menu = QMenu()
        show_action = QAction("📷 Capture Screen", self.app)
        show_action.triggered.connect(self.handle_show_overlay)
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        exit_action = QAction("❌ Exit", self.app)
        exit_action.triggered.connect(self.cleanup_and_exit)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.setToolTip("Direct Search\nPress Ctrl+Shift+Space to capture")
        self.tray_icon.show()

    def setup_components(self):
        """Setup core components (for legacy mode)"""
        try:
            from core.direct_search_engine import DirectSearchEngine
            from overlay import OverlayWindow
            from utils.hotkey_manager import HotkeyManager

            self.search_engine = DirectSearchEngine()
            self.overlay = OverlayWindow()
            self.hotkey_manager = HotkeyManager()

            # Connect signals
            self.overlay.region_selected.connect(self.on_region_selected)
            self.hotkey_manager.hotkey_pressed.connect(self.handle_show_overlay)

            # Start hotkey listener
            self.hotkey_manager.start_listening()
        except:
            pass

    def get_icon_path(self):
        """Get icon path"""
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'assets', 'tray_icon.ico'),
            os.path.join(os.path.dirname(__file__), 'assets', 'icon.ico'),
            os.path.join(os.path.dirname(__file__), 'tray_icon.ico'),
            os.path.join(os.path.dirname(__file__), 'icon.ico'),
        ]
        
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
            possible_paths.extend([
                os.path.join(base_path, 'assets', 'tray_icon.ico'),
                os.path.join(base_path, 'assets', 'icon.ico'),
                os.path.join(base_path, 'tray_icon.ico'),
                os.path.join(base_path, 'icon.ico'),
            ])
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return ""

    def handle_show_overlay(self):
        """Show overlay (legacy mode only)"""
        try:
            if hasattr(self, 'overlay'):
                self.overlay.show_overlay()
        except Exception as e:
            print(f"[ERROR] Failed to show overlay: {e}")

    def cleanup_and_exit(self):
        """Cleanup and exit application"""
        self.cleanup()
        self.app.quit()

    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'search_engine'):
            self.search_engine.cleanup()

def main():
    print("🚀 Direct Search Application - Optimized")
    
    # Check running mode
    single_use = "--single-use" in sys.argv
    preload_mode = "--preload" in sys.argv
    
    if preload_mode:
        print("[INFO] Running in pre-load mode (always ready)")
        # No lock file for pre-load mode
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        main_controller = DirectSearchApplication(app, preload_mode=True)
        atexit.register(main_controller.cleanup)
        sys.exit(app.exec())
    elif single_use:
        print("[INFO] Running in optimized single-use mode")
        # No lock file for single-use mode
        app = QApplication(sys.argv)
        main_controller = DirectSearchApplication(app, single_use_mode=True)
        atexit.register(main_controller.cleanup)
        sys.exit(app.exec())
    else:
        # Legacy mode with system tray
        print("[INFO] Running in legacy system tray mode")
        lock_file = QLockFile(os.path.join(QDir.tempPath(), "direct-search-app.lock"))
        if not lock_file.tryLock(100):
            print("[ERROR] Another instance is already running.")
            sys.exit(0)
        
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)
        main_controller = DirectSearchApplication(app, single_use_mode=False)
        atexit.register(main_controller.cleanup)
        sys.exit(app.exec())

if __name__ == "__main__":
    main()
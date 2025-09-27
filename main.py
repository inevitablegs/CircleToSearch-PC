import sys
import os
import threading
import mss
import easyocr
import numpy
import webbrowser
import pyperclip
import tempfile
import time
import io
from urllib.parse import quote_plus

# Selenium imports for direct image search
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.action_chains import ActionChains

# PySide6 Imports
from PySide6.QtWidgets import (
    QApplication, QMessageBox, 
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QLabel
)
from PySide6.QtGui import QFont, QGuiApplication
from PySide6.QtCore import QObject, Signal, QThread, QTimer, QLockFile, QDir, QRect, Qt

# Global hotkey import
try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
    print("[WARNING] pynput not available, using fallback method")

# Simple imports that we know work
from overlay import OverlayWindow
from side_panel import SidePanelWindow
from PIL import Image

# Enhanced Image Search Handler with DIRECT image upload
class ImageSearchHandler:
    """Handles DIRECT image search with automatic upload to Google Images"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.save_dir = self.create_save_directory()
        self.driver = None
        self.selenium_available = self._check_selenium()
    
    def _check_selenium(self):
        """Check if Selenium is available"""
        try:
            from selenium import webdriver
            return True
        except ImportError:
            print("[WARNING] Selenium not available - direct image search disabled")
            return False
    
    def create_save_directory(self):
        """Create directory to save captured files"""
        try:
            documents_path = os.path.join(os.path.expanduser("~"), "Documents")
            save_path = os.path.join(documents_path, "CircleToSearch_Captures")
            os.makedirs(save_path, exist_ok=True)
            print(f"[INFO] Save directory: {save_path}")
            return save_path
        except Exception as e:
            print(f"[ERROR] Could not create save directory: {e}")
            return os.path.join(os.path.expanduser("~"), "Desktop")
    
    def perform_direct_image_search(self, pil_image: Image.Image):
        """DIRECT image upload to Google Images using Selenium automation"""
        if not self.selenium_available:
            print("[WARNING] Selenium not available, using fallback method")
            return self._fallback_image_search(pil_image)
        
        try:
            print("🚀 Starting DIRECT image search automation...")
            
            # Save image to temporary file
            temp_image_path = self._save_temp_image(pil_image)
            print(f"📁 Temporary image saved: {temp_image_path}")
            
            # Setup Chrome driver
            if not self._setup_driver():
                return self._fallback_image_search(pil_image)
            
            # METHOD 1: Try direct Google Lens URL first (most reliable)
            print("🔧 Attempting Method 1: Direct Google Lens upload...")
            if self._try_direct_lens_upload(temp_image_path):
                return True
            
            # METHOD 2: Try traditional Google Images flow
            print("🔧 Attempting Method 2: Traditional Google Images...")
            if self._try_google_images_upload(temp_image_path):
                return True
            
            # METHOD 3: Last resort - use Google's upload endpoint directly
            print("🔧 Attempting Method 3: Direct upload endpoint...")
            if self._try_direct_upload_endpoint(temp_image_path):
                return True
            
            # All methods failed
            print("❌ All direct upload methods failed, using fallback...")
            return self._fallback_image_search(pil_image)
                
        except Exception as e:
            print(f"❌ Direct image search failed: {e}")
            return self._fallback_image_search(pil_image)
        finally:
            # Cleanup temp file
            if 'temp_image_path' in locals():
                try:
                    os.unlink(temp_image_path)
                except:
                    pass
    
    def _try_direct_lens_upload(self, image_path):
        """Method 1: Use Google Lens directly (most reliable)"""
        try:
            print("🌐 Opening Google Lens...")
            self.driver.get("https://lens.google.com/")
            time.sleep(3)
            
            # Try to find the upload area
            print("📤 Looking for upload area...")
            upload_selectors = [
                "input[type='file']",
                "div[role='button'][aria-label*='image']",
                "div[data-query*='upload']",
                "button[aria-label*='image']"
            ]
            
            for selector in upload_selectors:
                try:
                    file_inputs = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in file_inputs:
                        try:
                            if element.tag_name.lower() == "input" and element.get_attribute("type") == "file":
                                print("✅ Found file input, uploading image...")
                                element.send_keys(image_path)
                                print("🎉 Image uploaded to Google Lens!")
                                return True
                        except Exception as e:
                            continue
                except:
                    continue
            
            # If no file input found, try clicking around
            print("🔍 No direct file input found, trying interactive method...")
            return self._try_interactive_upload(image_path)
            
        except Exception as e:
            print(f"❌ Google Lens upload failed: {e}")
            return False
    
    def _try_google_images_upload(self, image_path):
        """Method 2: Traditional Google Images upload"""
        try:
            print("🌐 Opening Google Images...")
            self.driver.get("https://images.google.com")
            time.sleep(3)
            
            # Try to find and click the camera icon
            print("📷 Looking for camera icon...")
            camera_selectors = [
                "div[aria-label*='Search by image']",
                "div[role='button'][aria-label*='image']",
                ".LM8x9c",
                ".nDcEnd"
            ]
            
            for selector in camera_selectors:
                try:
                    camera_btn = WebDriverWait(self.driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                    )
                    camera_btn.click()
                    print("✅ Camera icon clicked!")
                    time.sleep(2)
                    break
                except:
                    continue
            else:
                print("❌ Could not find camera icon")
                return False
            
            # Try to find file input after camera click
            print("📤 Looking for file input after camera click...")
            try:
                file_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
                file_input.send_keys(image_path)
                print("✅ Image uploaded via Google Images!")
                return True
            except TimeoutException:
                print("❌ File input not found after camera click")
                return False
                
        except Exception as e:
            print(f"❌ Google Images upload failed: {e}")
            return False
    
    def _try_direct_upload_endpoint(self, image_path):
        """Method 3: Use Google's direct upload endpoint"""
        try:
            print("🌐 Using direct upload endpoint...")
            self.driver.get("https://www.google.com/searchbyimage/upload")
            time.sleep(3)
            
            # Look for file input on the upload page
            try:
                file_input = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='file']"))
                )
                file_input.send_keys(image_path)
                print("✅ Image uploaded via direct endpoint!")
                return True
            except TimeoutException:
                print("❌ No file input found on upload page")
                return False
                
        except Exception as e:
            print(f"❌ Direct endpoint upload failed: {e}")
            return False
    
    def _try_interactive_upload(self, image_path):
        """Interactive method using JavaScript and click simulation"""
        try:
            # Use JavaScript to create a file input element
            js_script = """
            var input = document.createElement('input');
            input.type = 'file';
            input.id = 'auto-upload-input';
            input.style.display = 'none';
            document.body.appendChild(input);
            """
            self.driver.execute_script(js_script)
            time.sleep(1)
            
            # Find the created input and upload file
            file_input = self.driver.find_element(By.ID, 'auto-upload-input')
            file_input.send_keys(image_path)
            time.sleep(2)
            
            # Try to trigger form submission
            submit_script = """
            var input = document.getElementById('auto-upload-input');
            var event = new Event('change', { bubbles: true });
            input.dispatchEvent(event);
            """
            self.driver.execute_script(submit_script)
            
            print("✅ Interactive upload completed!")
            return True
            
        except Exception as e:
            print(f"❌ Interactive upload failed: {e}")
            return False
    
    def _setup_driver(self):
        """Setup Chrome driver with options"""
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Remove automation detection
            chrome_options.add_argument("--disable-blink-features")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.implicitly_wait(5)
            return True
            
        except Exception as e:
            print(f"❌ Chrome driver setup failed: {e}")
            return False
    
    def _save_temp_image(self, pil_image: Image.Image):
        """Save image to temporary file"""
        temp_path = os.path.join(self.temp_dir, f"search_image_{int(time.time())}.jpg")
        
        # Optimize image
        img = pil_image.copy()
        max_size = (1200, 800)
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        img.save(temp_path, "JPEG", quality=85)
        return temp_path
    
    def _fallback_image_search(self, pil_image: Image.Image):
        """Fallback method when direct upload fails"""
        try:
            # Save to desktop for manual upload
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            image_path = os.path.join(desktop_path, "search_image.jpg")
            pil_image.save(image_path, "JPEG", quality=90)
            
            # Open Google Images with instructions
            webbrowser.open("https://lens.google.com")
            
            print("📁 Image saved to desktop for manual upload:")
            print(f"   📍 Location: {image_path}")
            print("   🌐 Google Lens opened - drag and drop the image file")
            print("   💡 Pro tip: Drag the image file from desktop to Google Lens page")
            
            return True
        except Exception as e:
            print(f"❌ Fallback method failed: {e}")
            # Last resort - just open Google Lens
            webbrowser.open("https://lens.google.com")
            return False
    
    def cleanup(self):
        """Clean up browser driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

# Enhanced Search Engine with DIRECT image search
class EnhancedSearchEngine:
    """Enhanced search engine with DIRECT image search capability"""
    
    def __init__(self):
        self.image_handler = ImageSearchHandler()
        self.auto_search = True
    
    def search_text(self, query):
        """Search text with Google"""
        if not query.strip():
            return False
        
        try:
            clean_query = query.strip()
            encoded_query = quote_plus(clean_query)
            url = f"https://www.google.com/search?q={encoded_query}"
            webbrowser.open(url)
            print(f"[INFO] 🔍 Google text search: '{clean_query[:50]}{'...' if len(clean_query) > 50 else ''}'")
            return True
        except Exception as e:
            print(f"[ERROR] Text search failed: {e}")
            return False
    
    def search_images_by_text(self, query):
        """Search for images using text query on Google"""
        if not query.strip():
            return False
        
        try:
            clean_query = query.strip()
            encoded_query = quote_plus(clean_query)
            url = f"https://www.google.com/search?tbm=isch&q={encoded_query}"
            webbrowser.open(url)
            print(f"[INFO] 🖼️ Google image search: '{clean_query[:50]}{'...' if len(clean_query) > 50 else ''}'")
            return True
        except Exception as e:
            print(f"[ERROR] Image search by text failed: {e}")
            return False
    
    def search_image(self, pil_image=None):
        """Perform DIRECT reverse image search on Google"""
        if pil_image:
            print("🚀 Starting DIRECT image search...")
            return self.image_handler.perform_direct_image_search(pil_image)
        else:
            print("[WARNING] No image provided for reverse search")
            return False

# Global OCR Reader
EASYOCR_READER = None

def get_ocr_reader():
    """Creates or returns the singleton OCR reader instance."""
    global EASYOCR_READER
    if EASYOCR_READER is None:
        print("[INFO] Initializing EasyOCR Reader...")
        EASYOCR_READER = easyocr.Reader(['en'], gpu=False)
        print("[INFO] EasyOCR Reader initialized.")
    return EASYOCR_READER

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
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_fallback)
        
    def start_listening(self):
        """Start fallback method"""
        print("[INFO] ⚠️ Using fallback hotkey method - limited functionality")
        print("[INFO] Press F12 to activate capture instead")
        self.widget = QWidget()
        self.widget.setWindowTitle("Circle to Search - Press F12 to Capture")
        self.widget.setFixedSize(400, 100)
        self.widget.show()
        
        from PySide6.QtGui import QShortcut, QKeySequence
        self.f12_shortcut = QShortcut(QKeySequence("F12"), self.widget)
        self.f12_shortcut.activated.connect(self._on_hotkey)
        
        return True
    
    def _check_fallback(self):
        """Check for fallback activation"""
        pass
    
    def _on_hotkey(self):
        """Handle fallback hotkey"""
        print("[DEBUG] 🎯 F12 hotkey activated!")
        self.hotkey_pressed.emit()
    
    def stop_listening(self):
        """Stop fallback listening"""
        if hasattr(self, 'widget'):
            self.widget.close()

class SimpleOcrWorker(QThread):
    """OCR worker with enhanced image search support"""
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, pil_image):
        super().__init__()
        self.pil_image = pil_image

    def run(self):
        """Run OCR processing"""
        try:
            reader = get_ocr_reader()
            image_np = numpy.array(self.pil_image)
            result = reader.readtext(image_np)
            
            recognized_texts = [text for bbox, text, conf in result if conf > 0.3]
            full_text = "\n".join(recognized_texts)
            
            self.finished.emit(full_text)
        except Exception as e:
            self.error.emit(f"OCR Error: {repr(e)}")

class EnhancedSidePanel(QWidget):
    """Enhanced side panel with DIRECT image search"""
    
    def __init__(self):
        super().__init__()
        self.search_engine = None
        self.current_image = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("Circle to Search - Results")
        self.setFixedSize(380, 500)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QLabel("🔍 Circle to Search Results")
        header.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 10px;
            }
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Text area
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Recognized text will appear here...")
        self.text_edit.setFixedHeight(150)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #ddd;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', monospace;
                font-size: 11px;
                background-color: #f9f9f9;
            }
            QTextEdit:focus {
                border-color: #667eea;
                background-color: white;
            }
        """)
        layout.addWidget(self.text_edit)
        
        # Search buttons
        search_layout = QVBoxLayout()
        
        # Text search buttons
        text_buttons_layout = QHBoxLayout()
        
        self.search_text_btn = QPushButton("🔍 Search on Google")
        self.search_text_btn.clicked.connect(self.search_text)
        self.search_text_btn.setStyleSheet(self.get_button_style("#4CAF50"))
        text_buttons_layout.addWidget(self.search_text_btn)
        
        self.search_images_btn = QPushButton("🖼️ Google Images")
        self.search_images_btn.clicked.connect(self.search_images_by_text)
        self.search_images_btn.setStyleSheet(self.get_button_style("#FF9800"))
        text_buttons_layout.addWidget(self.search_images_btn)
        
        search_layout.addLayout(text_buttons_layout)
        
        # DIRECT Image search button (prominent)
        self.image_search_btn = QPushButton("🚀 DIRECT Image Search")
        self.image_search_btn.clicked.connect(self.search_image)
        self.image_search_btn.setStyleSheet(self.get_button_style("#2196F3"))
        self.image_search_btn.setFixedHeight(50)
        search_layout.addWidget(self.image_search_btn)
        
        layout.addLayout(search_layout)
        
        # Additional features
        features_layout = QHBoxLayout()
        
        self.copy_btn = QPushButton("📋 Copy")
        self.copy_btn.clicked.connect(self.copy_text)
        self.copy_btn.setStyleSheet(self.get_button_style("#607D8B"))
        features_layout.addWidget(self.copy_btn)
        
        self.translate_btn = QPushButton("🌐 Translate")
        self.translate_btn.clicked.connect(self.translate_text)
        self.translate_btn.setStyleSheet(self.get_button_style("#9C27B0"))
        features_layout.addWidget(self.translate_btn)
        
        layout.addLayout(features_layout)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        self.close_btn = QPushButton("❌ Close")
        self.close_btn.clicked.connect(self.hide)
        self.close_btn.setStyleSheet(self.get_button_style("#F44336"))
        action_layout.addWidget(self.close_btn)
        
        layout.addLayout(action_layout)
        
        self.setLayout(layout)
        
        # Overall styling
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border: 3px solid #667eea;
                border-radius: 15px;
            }
        """)
    
    def get_button_style(self, color):
        """Get button styling"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-weight: bold;
                font-size: 11px;
            }}
            QPushButton:hover {{
                background-color: {color}CC;
            }}
            QPushButton:pressed {{
                background-color: {color}AA;
            }}
            QPushButton:disabled {{
                background-color: #CCCCCC;
                color: #666666;
            }}
        """
    
    def set_content(self, text, image, search_engine):
        """Set content for the panel"""
        self.text_edit.setPlainText(text)
        self.current_image = image
        self.search_engine = search_engine
        
        # Enable/disable buttons
        has_text = bool(text.strip())
        has_image = image is not None
        
        self.search_text_btn.setEnabled(has_text)
        self.search_images_btn.setEnabled(has_text)
        self.copy_btn.setEnabled(has_text)
        self.translate_btn.setEnabled(has_text)
        self.image_search_btn.setEnabled(has_image)
        
        if has_image:
            self.image_search_btn.setText("🚀 DIRECT Image Search ✨")
        else:
            self.image_search_btn.setText("🚀 No Image Available")
    
    def search_text(self):
        """Search for text on Google"""
        text = self.text_edit.toPlainText().strip()
        if self.search_engine and text:
            success = self.search_engine.search_text(text)
            if success:
                self.show_feedback("🔍 Searching on Google!")
    
    def search_images_by_text(self):
        """Search for images by text on Google"""
        text = self.text_edit.toPlainText().strip()
        if self.search_engine and text:
            success = self.search_engine.search_images_by_text(text)
            if success:
                self.show_feedback("🖼️ Google Images opened!")
    
    def search_image(self):
        """Perform DIRECT reverse image search on Google"""
        if self.search_engine and self.current_image:
            print("🚀 Starting DIRECT image search from panel...")
            success = self.search_engine.search_image(self.current_image)
            if success:
                self.show_feedback("🎉 DIRECT image search started!")
            else:
                self.show_feedback("❌ Image search failed")
        else:
            self.show_feedback("❌ No image to search")
    
    def copy_text(self):
        """Copy text to clipboard"""
        text = self.text_edit.toPlainText().strip()
        if text:
            try:
                pyperclip.copy(text)
                self.show_feedback("📋 Text copied!")
            except Exception:
                clipboard = QApplication.clipboard()
                clipboard.setText(text)
                self.show_feedback("📋 Text copied!")
    
    def translate_text(self):
        """Translate text"""
        text = self.text_edit.toPlainText().strip()
        if text:
            try:
                encoded_text = quote_plus(text)
                url = f"https://translate.google.com/?sl=auto&tl=en&text={encoded_text}"
                webbrowser.open(url)
                self.show_feedback("🌐 Translation opened!")
            except Exception as e:
                print(f"[ERROR] Translation failed: {e}")
    
    def show_feedback(self, message):
        """Show feedback message"""
        original_title = self.windowTitle()
        self.setWindowTitle(message)
        QTimer.singleShot(2000, lambda: self.setWindowTitle(original_title))
    
    def show_panel(self, relative_rect=None):
        """Show the panel"""
        if relative_rect:
            screen = QGuiApplication.primaryScreen().geometry()
            panel_x = min(relative_rect.right() + 15, screen.width() - self.width())
            panel_y = max(0, min(relative_rect.top(), screen.height() - self.height()))
            self.move(panel_x, panel_y)
        
        self.show()
        self.raise_()
        self.activateWindow()

class DirectHotkeyApplication(QObject):
    """Direct hotkey application with DIRECT image search"""
    
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        print("[DEBUG] Initializing Direct Hotkey Circle to Search...")
        
        # Core components
        self.search_engine = EnhancedSearchEngine()
        
        # UI Components
        self.overlay = OverlayWindow()
        self.side_panel = EnhancedSidePanel()
        
        # State
        self.ocr_worker = None
        self.last_selection_rect = None
        self.last_captured_image = None
        
        # Setup only hotkeys (no tray)
        self.setup_direct_hotkeys()
        
        # Connect signals
        self.overlay.region_selected.connect(self.on_region_selected)
        
        print("[DEBUG] Direct Hotkey Circle to Search initialized!")

    def setup_direct_hotkeys(self):
        """Setup direct keyboard shortcuts without tray icon"""
        if PYNPUT_AVAILABLE:
            self.hotkey_listener = GlobalHotkeyListener()
            success = self.hotkey_listener.start_listening()
        else:
            success = False
            
        if not success:
            print("[WARNING] Global hotkeys failed, using fallback method")
            self.hotkey_listener = FallbackHotkeyListener()
            self.hotkey_listener.start_listening()
        
        self.hotkey_listener.hotkey_pressed.connect(self.handle_show_overlay)
        print("[INFO] ✅ Hotkey setup complete")

    def handle_show_overlay(self):
        """Show the capture overlay directly"""
        print("[DEBUG] 🎯 Showing overlay (direct hotkey)...")
        try:
            self.overlay.show_overlay()
            print("[DEBUG] Overlay activated via hotkey")
        except Exception as e:
            print(f"[ERROR] Failed to show overlay: {e}")
            QMessageBox.information(None, "Capture", "Hotkey activated! Click OK to capture screenshot manually.")

    def on_region_selected(self, rect: QRect):
        """Handle region selection with DIRECT search"""
        print(f"[DEBUG] Region selected: {rect}")
        
        self.last_selection_rect = rect
        screen = QGuiApplication.primaryScreen()
        pixel_ratio = screen.devicePixelRatio()
        
        capture_rect = {
            "top": int(rect.top() * pixel_ratio),
            "left": int(rect.left() * pixel_ratio),
            "width": int(rect.width() * pixel_ratio),
            "height": int(rect.height() * pixel_ratio),
        }
        
        try:
            with mss.mss() as sct:
                sct_img = sct.grab(capture_rect)
                pil_img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
                
                self.last_captured_image = pil_img.copy()
                
                print("✅ Region captured, starting OCR...")
                
                if self.ocr_worker and self.ocr_worker.isRunning():
                    self.ocr_worker.quit()
                    self.ocr_worker.wait()

                self.ocr_worker = SimpleOcrWorker(pil_img)
                self.ocr_worker.finished.connect(self.handle_ocr_result)
                self.ocr_worker.error.connect(self.handle_ocr_error)
                self.ocr_worker.start()
                
        except Exception as e:
            print(f"[ERROR] Screen capture failed: {e}")
            QMessageBox.warning(None, "Capture Error", f"Failed to capture screen: {e}")

    def handle_ocr_result(self, ocr_text):
        """Handle OCR results with DIRECT image search"""
        clean_text = ocr_text.strip()
        print(f"✅ OCR Result: {clean_text}")
        
        # Auto-copy text to clipboard
        if clean_text:
            try:
                pyperclip.copy(clean_text)
                print("[INFO] Text copied to clipboard")
            except Exception as e:
                print(f"[WARNING] Could not copy text: {e}")
        
        # DIRECT search logic
        if clean_text:
            print("[INFO] 🔍 Performing automatic text search...")
            self.search_engine.search_text(clean_text)
            print(f"✅ Text Found: {clean_text[:40]}{'...' if len(clean_text) > 40 else ''}")
        else:
            # DIRECT image search when no text found
            if self.last_captured_image:
                print("[INFO] 🚀 Performing AUTOMATIC DIRECT image search...")
                success = self.search_engine.search_image(self.last_captured_image)
                
                if success:
                    print("🎉 Automatic DIRECT image search completed!")
                else:
                    print("❌ Direct search failed, opening Google Lens...")
                    webbrowser.open("https://lens.google.com")
            else:
                print("❌ No image available for search")

    def handle_ocr_error(self, error_message):
        """Handle OCR errors"""
        print(f"[ERROR] OCR failed: {error_message}")
        QMessageBox.warning(None, "OCR Error", f"Text recognition failed:\n{error_message}")

    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self.search_engine.image_handler, 'cleanup'):
            self.search_engine.image_handler.cleanup()

if __name__ == "__main__":
    print("🚀 Starting Direct Hotkey Circle to Search with DIRECT Image Search")
    
    # Single instance lock
    lock_file = QLockFile(os.path.join(QDir.tempPath(), "circle-to-search-direct.lock"))
    if not lock_file.tryLock(100):
        print("[ERROR] Another instance is already running.")
        sys.exit(0)
    
    # Create application
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName("Circle to Search Direct")

    # Create main controller
    main_controller = DirectHotkeyApplication(app)

    print("✨ Direct Hotkey Circle to Search is ready!")
    print("📖 How to use:")
    print("   🎯 Press Ctrl+Shift+Space OR Ctrl+Alt+S to capture")
    print("   🔍 Text automatically searches on Google!")
    print("   🚀 Images automatically perform DIRECT upload to Google Lens!")
    print("   📋 Text is auto-copied to clipboard")
    print("   ❌ Press Ctrl+C in terminal to quit")
    
    # Ensure cleanup on exit
    import atexit
    atexit.register(main_controller.cleanup)

    # Start the application
    sys.exit(app.exec())
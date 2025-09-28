import os
import tempfile
import time
import webbrowser
from PIL import Image
import threading
import sys

# Selenium imports for direct image search
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

class DirectImageSearchHandler:
    """Handles DIRECT image search with automatic upload to Google Images"""
    
    def __init__(self):
        self.temp_dir = self._get_safe_temp_dir()
        self.driver = None
        self.selenium_available = self._check_selenium()
        self.current_temp_files = []  # Track temp files to clean up on app exit
    
    def _check_selenium(self):
        """Check if Selenium is available"""
        try:
            from selenium import webdriver
            return True
        except ImportError:
            print("[WARNING] Selenium not available - direct image search disabled")
            return False
    
    def perform_direct_image_search(self, pil_image: Image.Image):
        """DIRECT image upload to Google Images using Selenium automation - BROWSER STAYS OPEN"""
        if not self.selenium_available:
            print("[WARNING] Selenium not available, using fallback method")
            return self._fallback_image_search(pil_image)
        
        try:
            print("🚀 Starting DIRECT image search automation...")
            
            # Save image to a persistent temporary file
            temp_image_path = self._save_persistent_temp_image(pil_image)
            print(f"📁 Persistent temporary image saved: {temp_image_path}")
            
            # Verify file exists and is accessible
            if not os.path.exists(temp_image_path):
                print("❌ Temp file was not created properly")
                return self._fallback_image_search(pil_image)
                
            print(f"✅ File verification: {os.path.getsize(temp_image_path)} bytes")
            
            # Setup Chrome driver
            if not self._setup_driver():
                return self._fallback_image_search(pil_image)
            
            # METHOD 1: Try direct Google Lens URL first (most reliable)
            print("🔧 Attempting Method 1: Direct Google Lens upload...")
            if self._try_direct_lens_upload(temp_image_path):
                print("✅ Google Lens search completed - browser will stay open for user to view results")
                return True
            
            # METHOD 2: Try traditional Google Images flow
            print("🔧 Attempting Method 2: Traditional Google Images...")
            if self._try_google_images_upload(temp_image_path):
                print("✅ Google Images search completed - browser will stay open for user to view results")
                return True
            
            # METHOD 3: Last resort - use Google's upload endpoint directly
            print("🔧 Attempting Method 3: Direct upload endpoint...")
            if self._try_direct_upload_endpoint(temp_image_path):
                print("✅ Direct upload search completed - browser will stay open for user to view results")
                return True
            
            # All methods failed
            print("❌ All direct upload methods failed, using fallback...")
            return self._fallback_image_search(pil_image)
                
        except Exception as e:
            print(f"❌ Direct image search failed: {e}")
            import traceback
            traceback.print_exc()
            return self._fallback_image_search(pil_image)
    
    def _save_persistent_temp_image(self, pil_image: Image.Image):
        """Save image to a persistent temp file that won't be deleted automatically"""
        # Create a safe filename with timestamp
        timestamp = int(time.time())
        safe_filename = f"direct_search_image_{timestamp}.jpg"
        
        # Use user's Documents folder or Desktop for better accessibility
        user_folder = os.path.expanduser("~")
        possible_folders = [
            os.path.join(user_folder, "Documents"),
            os.path.join(user_folder, "Desktop"),
            self.temp_dir
        ]
        
        # Try to find a writable folder
        for folder in possible_folders:
            try:
                if not os.path.exists(folder):
                    continue
                    
                temp_path = os.path.join(folder, safe_filename)
                
                # Optimize and save image
                img = pil_image.copy()
                max_size = (1200, 800)
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                img.save(temp_path, "JPEG", quality=85)
                print(f"💾 Saved image to: {temp_path}")
                
                # Add to cleanup list
                self.current_temp_files.append(temp_path)
                return temp_path
                
            except Exception as e:
                print(f"⚠️ Could not save to {folder}: {e}")
                continue
        
        # Fallback to traditional temp file
        return self._save_fallback_temp_image(pil_image)
    
    def _save_fallback_temp_image(self, pil_image: Image.Image):
        """Fallback method for saving temp image"""
        temp_path = os.path.join(self.temp_dir, f"search_image_{int(time.time())}.jpg")
        
        # Optimize image
        img = pil_image.copy()
        max_size = (1200, 800)
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        img.save(temp_path, "JPEG", quality=85)
        self.current_temp_files.append(temp_path)
        return temp_path
    
    def _try_direct_lens_upload(self, image_path):
        """Method 1: Use Google Lens directly (most reliable)"""
        try:
            print("🌐 Opening Google Lens...")
            self.driver.get("https://lens.google.com/")
            time.sleep(3)
            
            # Double-check file exists before uploading
            if not os.path.exists(image_path):
                print("❌ Image file disappeared before upload!")
                return False
                
            print(f"📁 File ready for upload: {image_path} ({os.path.getsize(image_path)} bytes)")
            
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
                                
                                # Use absolute path to be safe
                                absolute_path = os.path.abspath(image_path)
                                print(f"📤 Uploading: {absolute_path}")
                                
                                element.send_keys(absolute_path)
                                
                                # Wait a moment for upload to complete
                                time.sleep(2)
                                print("🎉 Image uploaded to Google Lens!")
                                print("📖 Browser will stay open - close it manually when done")
                                return True
                        except Exception as e:
                            print(f"⚠️ Failed with element {selector}: {e}")
                            continue
                except Exception as e:
                    print(f"⚠️ Selector {selector} failed: {e}")
                    continue
            
            # If no file input found, try clicking around
            print("🔍 No direct file input found, trying interactive method...")
            return self._try_interactive_upload(image_path)
            
        except Exception as e:
            print(f"❌ Google Lens upload failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _try_google_images_upload(self, image_path):
        """Method 2: Traditional Google Images upload"""
        try:
            print("🌐 Opening Google Images...")
            self.driver.get("https://images.google.com")
            time.sleep(2)
            
            # Verify file still exists
            if not os.path.exists(image_path):
                print("❌ Image file disappeared before upload!")
                return False
            
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
                    camera_btn = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if camera_btn.is_displayed() and camera_btn.is_enabled():
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
                file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                
                # Use absolute path
                absolute_path = os.path.abspath(image_path)
                print(f"📤 Uploading: {absolute_path}")
                
                file_input.send_keys(absolute_path)
                
                # Wait for upload
                time.sleep(2)
                print("✅ Image uploaded via Google Images!")
                print("📖 Browser will stay open - close it manually when done")
                return True
            except Exception as e:
                print(f"❌ File input not found after camera click: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Google Images upload failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _try_direct_upload_endpoint(self, image_path):
        """Method 3: Use Google's direct upload endpoint"""
        try:
            print("🌐 Using direct upload endpoint...")
            self.driver.get("https://www.google.com/searchbyimage/upload")
            time.sleep(2)
            
            # Verify file exists
            if not os.path.exists(image_path):
                print("❌ Image file disappeared before upload!")
                return False
            
            # Look for file input on the upload page
            try:
                file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
                
                absolute_path = os.path.abspath(image_path)
                print(f"📤 Uploading: {absolute_path}")
                
                file_input.send_keys(absolute_path)
                
                time.sleep(2)
                print("✅ Image uploaded via direct endpoint!")
                print("📖 Browser will stay open - close it manually when done")
                return True
            except Exception as e:
                print(f"❌ No file input found on upload page: {e}")
                return False
                
        except Exception as e:
            print(f"❌ Direct endpoint upload failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _try_interactive_upload(self, image_path):
        """Interactive method using JavaScript and click simulation"""
        try:
            # Verify file exists
            if not os.path.exists(image_path):
                print("❌ Image file disappeared before upload!")
                return False
            
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
            
            absolute_path = os.path.abspath(image_path)
            print(f"📤 Uploading via JS: {absolute_path}")
            
            file_input.send_keys(absolute_path)
            time.sleep(2)
            
            # Try to trigger form submission
            submit_script = """
            var input = document.getElementById('auto-upload-input');
            var event = new Event('change', { bubbles: true });
            input.dispatchEvent(event);
            """
            self.driver.execute_script(submit_script)
            
            print("✅ Interactive upload completed!")
            print("📖 Browser will stay open - close it manually when done")
            return True
            
        except Exception as e:
            print(f"❌ Interactive upload failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _setup_driver(self):
        """Setup Chrome driver with optimized options"""
        try:
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Set page load strategy to 'eager' to load quickly
            chrome_options.page_load_strategy = 'eager'
            
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=chrome_options
            )
            
            # Remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            # Set implicit wait to 0 (no waiting)
            self.driver.implicitly_wait(0)
            
            return True
            
        except Exception as e:
            print(f"❌ Chrome driver setup failed: {e}")
            return False
        
    def _get_safe_temp_dir(self):
        """Get a safe temp directory that works in .exe"""
        if getattr(sys, 'frozen', False):
            # Running as .exe - use user's temp directory that's accessible
            return os.path.join(os.path.expanduser("~"), "AppData", "Local", "Temp", "DirectSearch")
        else:
            # Running as script
            return tempfile.gettempdir()
    
    def _fallback_image_search(self, pil_image: Image.Image):
        """Fallback method when direct upload fails"""
        try:
            # Save to user's Documents folder for better accessibility
            user_folder = os.path.expanduser("~")
            save_folder = os.path.join(user_folder, "Documents")
            if not os.path.exists(save_folder):
                save_folder = user_folder
                
            image_path = os.path.join(save_folder, "direct_search_image.jpg")
            pil_image.save(image_path, "JPEG", quality=90)
            
            # Open Google Lens with instructions
            webbrowser.open("https://lens.google.com")
            
            print("📁 Image saved for manual upload:")
            print(f"   📍 Location: {image_path}")
            print("   🌐 Google Lens opened - drag and drop the image file")
            print("   📖 Close the browser manually when done searching")
            
            return True
        except Exception as e:
            print(f"❌ Fallback method failed: {e}")
            # Last resort - just open Google Lens
            webbrowser.open("https://lens.google.com")
            return False
    
    def cleanup(self):
        """Clean up browser driver and temp files - ONLY called when app exits"""
        # Clean up browser
        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
                print("[INFO] Browser driver cleaned up")
            except:
                pass
        
        # Clean up temp files (optional - comment out if you want files to persist)
        for temp_file in self.current_temp_files:
            try:
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
                    print(f"[INFO] Cleaned up temp file: {temp_file}")
            except:
                print(f"[WARNING] Could not delete temp file: {temp_file}")
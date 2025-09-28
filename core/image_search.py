import os
import tempfile
import time
import webbrowser
from PIL import Image
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service as ChromeService

class DirectImageSearchHandler:
    """Handles direct image search with automatic upload to Google Images"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
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
    
    def perform_direct_image_search(self, pil_image: Image.Image):
        """Direct image upload to Google Images using Selenium automation"""
        if not self.selenium_available:
            print("[WARNING] Selenium not available, using fallback method")
            return self._fallback_image_search(pil_image)
        
        try:
            print("🚀 Starting direct image search automation...")
            
            # Save image to temporary file
            temp_image_path = self._save_temp_image(pil_image)
            print(f"📁 Temporary image saved: {temp_image_path}")
            
            # Setup Chrome driver
            if not self._setup_driver():
                return self._fallback_image_search(pil_image)
            
            # Try different upload methods
            methods = [
                self._try_direct_lens_upload,
                self._try_google_images_upload,
                self._try_direct_upload_endpoint
            ]
            
            for method in methods:
                print(f"🔧 Attempting {method.__name__}...")
                if method(temp_image_path):
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
        """Method 1: Use Google Lens directly"""
        try:
            print("🌐 Opening Google Lens...")
            self.driver.get("https://lens.google.com/")
            time.sleep(3)
            
            # Try to find the upload area
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
                        except Exception:
                            continue
                except:
                    continue
            
            return False
            
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
            
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=chrome_options
            )
            
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
            
            return True
        except Exception as e:
            print(f"❌ Fallback method failed: {e}")
            webbrowser.open("https://lens.google.com")
            return False
    
    def cleanup(self):
        """Clean up browser driver"""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
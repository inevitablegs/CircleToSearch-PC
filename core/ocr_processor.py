import easyocr
import numpy
from PIL import Image

class OCRProcessor:
    """Handles OCR text extraction from images"""
    
    def __init__(self):
        self.reader = None
        
    def _initialize_reader(self):
        """Initialize EasyOCR reader if not already done"""
        if self.reader is None:
            print("[INFO] Initializing EasyOCR Reader...")
            self.reader = easyocr.Reader(['en'], gpu=False)
            print("[INFO] EasyOCR Reader initialized.")
    
    def extract_text(self, pil_image: Image.Image):
        """Extract text from PIL Image using OCR"""
        self._initialize_reader()
        
        try:
            image_np = numpy.array(pil_image)
            result = self.reader.readtext(image_np)
            
            recognized_texts = [text for bbox, text, conf in result if conf > 0.3]
            full_text = "\n".join(recognized_texts)
            
            print(f"[INFO] OCR extracted {len(recognized_texts)} text elements")
            return full_text
            
        except Exception as e:
            print(f"[ERROR] OCR processing failed: {e}")
            return ""
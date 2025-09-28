# PyDirect

[![CI/CD Status](https://img.shields.io/badge/CI/CD-Passing-brightgreen)](https://github.com/your-org/PyDirect/actions)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/pydirect)](https://pypi.org/project/pydirect/)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue)](https://www.python.org/downloads/)

## Table of Contents
- [About PyDirect](#about-pydirect)
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Using pip](#using-pip)
  - [From Source](#from-source)
  - [Building an Executable](#building-an-executable)
- [Usage](#usage)
  - [Basic Screen Capture](#basic-screen-capture)
  - [Performing OCR on Screen](#performing-ocr-on-screen)
  - [Automating Mouse Clicks](#automating-mouse-clicks)
  - [Web Automation Example](#web-automation-example)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

---

## About PyDirect

PyDirect is a robust, Python-based desktop automation and screen interaction framework designed for precision and efficiency. Leveraging a powerful combination of advanced libraries, it empowers users to programmatically interact with their screen, perform sophisticated Optical Character Recognition (OCR), and automate complex workflows across both desktop applications and web browsers.

Whether you're building automated testing suites, creating custom tools for data extraction from graphical interfaces, or developing accessibility solutions, PyDirect provides the tools to directly engage with your digital environment. Its intuitive design, coupled with a comprehensive feature set including screen overlays and real-time interaction capabilities, makes it an invaluable asset for developers seeking direct control over their system's visual and interactive elements.

## Features

PyDirect offers a comprehensive suite of functionalities to streamline automation and interaction:

*   **Advanced Screen Capture**: Capture full screens or specific regions with high precision using `mss`.
*   **Optical Character Recognition (OCR)**: Extract text from any part of the screen using `easyocr` and `torch` for intelligent text recognition.
*   **Desktop Automation**: Programmatically control mouse movements, clicks, and keyboard inputs (`pynput`) for seamless interaction with desktop applications.
*   **Web Browser Automation**: Integrate with web browsers via `selenium` and `webdriver-manager` to automate web tasks, form filling, and data scraping.
*   **Interactive Overlays**: Utilize `PySide6` to create interactive screen overlays for visual feedback, selection areas, or enhanced user interaction.
*   **Clipboard Management**: Easily copy and paste text using `pyperclip`.
*   **Image Processing**: Built-in support for image manipulation and analysis with `numpy` and `Pillow`.
*   **Cross-Platform Compatibility**: Designed to work across major operating systems.

## Installation

### Prerequisites

Ensure you have Python 3.8 or higher installed on your system.

### Using pip

The easiest way to install PyDirect and its dependencies is via pip:

```bash
# It's recommended to use a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

pip install pydirect
```

If you prefer to install from the `requirements.txt` file (e.g., for development):

```bash
# Clone the repository first if you haven't already
git clone https://github.com/inevitablegs/CircleToSearch-PC
cd PyDirect

# Install dependencies from requirements.txt
pip install -r requirements.txt
```

### From Source

For development or to get the latest unreleased features, you can install PyDirect directly from its source code:

```bash
git clone https://github.com/inevitablegs/CircleToSearch-PC
cd PyDirect
pip install -e .
```

### Building an Executable

PyDirect includes a script (`build_exe.py`) to create standalone executables, typically using tools like PyInstaller. This allows you to run PyDirect without a Python environment.

```bash
# Ensure you have PyInstaller or a similar tool installed:
pip install pyinstaller

# Then, run the build script from the project root:
python build_exe.py
```
The executable will typically be found in a `dist/` folder after the build process completes. Refer to the `build_exe.py` script for specific output locations and options.

## Usage

PyDirect is designed to be highly modular. Below are some common usage examples demonstrating its core capabilities.

### Basic Screen Capture

Capture a screenshot of the entire screen or a specific region.

```python
import mss
import mss.tools
from PIL import Image

def capture_screen_region(x, y, width, height, output_filename="screenshot.png"):
    """
    Captures a specific region of the screen and saves it as an image.
    """
    with mss.mss() as sct:
        monitor = {"top": y, "left": x, "width": width, "height": height}
        sct_img = sct.grab(monitor)
        # Convert to PIL Image for easier manipulation
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
        img.save(output_filename)
        print(f"Captured region ({x},{y},{width},{height}) to {output_filename}")
        return img

if __name__ == "__main__":
    # Example: Capture a 500x300 pixel region starting at (100, 100)
    capture_screen_region(100, 100, 500, 300, "my_region.png")

    # The main.py module might offer higher-level abstractions:
    # from pydirect.main import ScreenManager
    # screen = ScreenManager()
    # screen.capture_area(100, 100, 500, 300, "my_region_via_pydirect.png")
```

### Performing OCR on Screen

Identify and extract text from a captured screen region.

```python
import easyocr
from PIL import Image
import numpy as np
import mss

# Initialize OCR reader (only once)
# This might take a moment the first time as models are loaded
reader = easyocr.Reader(['en']) # Specify languages, e.g., ['en', 'fr']

def ocr_screen_region(x, y, width, height):
    """
    Captures a screen region, performs OCR, and returns detected text.
    """
    with mss.mss() as sct:
        monitor = {"top": y, "left": x, "width": width, "height": height}
        sct_img = sct.grab(monitor)
        img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")

        # Convert PIL Image to a NumPy array (required by EasyOCR)
        img_np = np.array(img)

        # Perform OCR
        result = reader.readtext(img_np)

        detected_text = []
        for (bbox, text, prob) in result:
            detected_text.append(text)
            print(f"Detected: '{text}' (Confidence: {prob:.2f}) at {bbox}")
        return " ".join(detected_text)

if __name__ == "__main__":
    print("Performing OCR on a screen region...")
    # Adjust coordinates and size to a region on your screen likely to contain text
    extracted_text = ocr_screen_region(10, 10, 800, 200)
    print(f"\nTotal extracted text: \n'{extracted_text}'")

    # PyDirect might offer an integrated OCR function:
    # from pydirect.main import OCREngine
    # ocr = OCREngine()
    # text = ocr.read_screen_area(10, 10, 800, 200)
```

### Automating Mouse Clicks

Programmatically control mouse movements and clicks.

```python
from pynput.mouse import Controller, Button
import time

mouse = Controller()

def click_at(x, y, button=Button.left, count=1, delay=0.1):
    """
    Moves the mouse to (x, y) and performs a click.
    """
    print(f"Moving mouse to ({x}, {y}) and clicking {count} time(s) with {button} button.")
    mouse.position = (x, y)
    time.sleep(delay) # Give cursor time to move
    for _ in range(count):
        mouse.click(button)
        if count > 1:
            time.sleep(delay) # Delay between multiple clicks

if __name__ == "__main__":
    print("Mouse automation example. Move your mouse away now.")
    time.sleep(3) # Give user time to move mouse away

    # Example: Click at a specific screen coordinate (e.g., 500, 300)
    click_at(500, 300)

    # Example: Double-click with the right button
    # click_at(600, 400, button=Button.right, count=2)

    print("Mouse automation complete.")

    # PyDirect's main.py might have a more integrated control system:
    # from pydirect.main import InputController
    # inputs = InputController()
    # inputs.mouse_click(500, 300)
```

### Web Automation Example

Using PyDirect with `selenium` to automate web browser interactions.

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

def automate_web_search(query):
    """
    Opens a browser, navigates to Google, searches for a query, and closes.
    """
    print(f"Starting web automation for query: '{query}'")
    service = ChromeService(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)
    
    try:
        driver.get("https://www.google.com")
        print("Navigated to Google.")
        time.sleep(2) # Allow page to load

        search_box = driver.find_element("name", "q")
        search_box.send_keys(query)
        search_box.submit()
        print(f"Searched for '{query}'.")
        time.sleep(5) # View search results

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Closing browser.")
        driver.quit()

if __name__ == "__main__":
    automate_web_search("PyDirect project")

    # PyDirect might encapsulate these actions:
    # from pydirect.main import WebAutomator
    # web = WebAutomator()
    # web.google_search("PyDirect automation framework")
```

For more examples and advanced usage, refer to the `main.py` and `overlay.py` files in the source code, which demonstrate the high-level application logic and GUI interactions.

## Configuration

PyDirect manages its core dependencies through the `requirements.txt` file. For advanced users or developers, this file specifies the exact versions of libraries required.

```txt
# requirements.txt
numpy>=1.24.0
Pillow>=10.0.0
easyocr>=1.7.0
mss>=9.0.1
pyperclip>=1.8.2
torchvision>=0.15.0
torch>=2.0.0
pynput>=1.7.6
webdriver-manager>=4.0.0
PySide6>=6.5.0
selenium>=4.10.0
# Add other dependencies here as needed
```

To modify dependencies or for development:
1.  Edit `requirements.txt` as needed.
2.  Run `pip install -r requirements.txt` to apply changes.

Runtime configurations (e.g., OCR language models, default screenshot paths) are typically handled within the `main.py` or other module files, or can be exposed via command-line arguments or environment variables. Consult the source code for specific configuration options.

## Contributing

We welcome contributions to PyDirect! If you're interested in improving the project, please follow these steps:

1.  **Fork the repository** on GitHub.
2.  **Clone your forked repository** to your local machine.
3.  **Create a new branch** for your feature or bugfix:
    ```bash
    git checkout -b feature/your-feature-name
    ```
4.  **Make your changes**, ensuring that your code adheres to the project's coding standards.
5.  **Write and run tests** to ensure your changes work as expected and don't introduce regressions.
6.  **Commit your changes** with a clear and descriptive commit message.
7.  **Push your branch** to your forked repository.
8.  **Open a Pull Request** against the `main` branch of the original PyDirect repository.

Please refer to [CONTRIBUTING.md](CONTRIBUTING.md) for more detailed guidelines.

## License

PyDirect is released under the [MIT License](LICENSE).

---
*Generated by an expert technical writer.*
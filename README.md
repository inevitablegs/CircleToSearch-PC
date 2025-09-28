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
# Contributing to Direct Search

🎉 First off, thank you for taking the time to contribute!\
Direct Search is an open project that aims to make text and image
searching faster and simpler. We welcome contributions of all kinds --
bug fixes, new features, documentation improvements, and more.

------------------------------------------------------------------------

## 🛠 How to Contribute

### 1. Fork & Clone

-   Fork the repository to your GitHub account.\

-   Clone your fork locally:

    ``` bash
    git clone https://github.com/<your-username>/DirectSearch.git
    cd DirectSearch
    ```

### 2. Set Up the Environment

-   Install dependencies:

    ``` bash
    pip install -r requirements.txt
    ```

-   Run the app:

    ``` bash
    python main.py
    ```

### 3. Branch Workflow

-   Always create a new branch for your changes:

    ``` bash
    git checkout -b feature/your-feature-name
    ```

-   Use meaningful branch names:

    -   `feature/...` → New features\
    -   `fix/...` → Bug fixes\
    -   `docs/...` → Documentation changes

### 4. Code Guidelines

-   Follow **PEP8** style guide.\
-   Keep functions and classes small and focused.\
-   Add docstrings/comments where helpful.\
-   Place reusable code in `core/` or `utils/`.\
-   Don't hardcode paths -- use relative or config options.

### 5. Testing

-   Manually test new features:
    -   Hotkey trigger works (`Ctrl+Shift+Space`)\
    -   Text OCR runs correctly\
    -   Image search opens in browser\
    -   Tray icon actions (capture, exit) work\
-   If possible, add automated tests (future improvement).

### 6. Commit Messages

-   Use clear, descriptive commit messages:
    -   `fix: resolve hotkey listener crash`
    -   `feat: add Google Images fallback method`
    -   `docs: update installation guide`

### 7. Submitting a PR

1.  Push your branch:

    ``` bash
    git push origin feature/your-feature-name
    ```

2.  Open a Pull Request (PR) to the `main` branch.\

3.  Clearly describe your changes, why they are needed, and any testing
    done.

------------------------------------------------------------------------

## 🧩 Types of Contributions

-   **Bug fixes** → Fix crashes, errors, unexpected behavior.\
-   **Features** → Add new functionality like more OCR languages,
    additional search providers.\
-   **Documentation** → Improve guides, installation steps, or code
    comments.\
-   **Code cleanup** → Refactor, optimize, or improve readability.

------------------------------------------------------------------------

## 📜 Code of Conduct

Please be respectful, collaborative, and constructive.\
We're all here to learn and build something useful together.

------------------------------------------------------------------------

## 💡 Need Ideas?

Check the `imptovr.txt` file or GitHub Issues for pending improvements.\
Some ideas: - Add dark mode for overlay UI.\
- Support multiple OCR languages.\
- Add a settings panel for custom hotkeys.\
- Improve error handling for Selenium search.

------------------------------------------------------------------------

🙌 Thank you for contributing to **Direct Search**!

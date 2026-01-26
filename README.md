# QA TestCase Buddy (Local LLM Test Case Generator)

## Overview
A local CLI tool that uses Ollama (specifically `qwen3:4b`) to generate detailed QA test cases from user requirements and saves them to Excel.

## Prerequisites
1.  **Ollama** installed and running (`ollama serve`).
2.  **Model**: `qwen3:4b` pulled (`ollama pull qwen3:4b`).
3.  **Python 3.x**
4.  **Dependencies**: `pandas`, `openpyxl`, `requests`.

## How to Run

### Interactive Mode (CLI)
```powershell
python run_generator.py
```
Paste your requirements, then type `DONE`.

### One-Liner Mode (CLI)
```powershell
python run_generator.py "Your requirements here..."
```

## 🌐 Web Interface

Prefer a graphical interface? We have a modern web UI.

### How to Run
1.  Start the backend server:
    ```powershell
    python app.py
    ```
2.  Open your browser and navigate to:
    [http://localhost:5000](http://localhost:5000)

### Features
-   **Visual Table**: View generated cases instantly.
-   **Excel Download**: One-click export.
-   **Execution Time**: View how long the generation took.
-   **Premium Design**: Dark mode with glassmorphism aesthetics.

## Troubleshooting
-   **Empty Output / JSON Errors**: The model (`qwen3:4b`) can be sensitive. We have disabled strict JSON mode to help it output text. If it fails, try re-running with a simpler prompt.
-   **Excel Error**: Close `test_cases.xlsx` if it is open before running the script.

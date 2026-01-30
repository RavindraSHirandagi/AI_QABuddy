# System Architecture: Test Case Generation Flow

This document visualizes the end-to-end data flow for generating test cases using **QA TestCase Buddy**.

## Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant UI as Frontend (index.html)
    participant App as Flask Server (app.py)
    participant Parser as Tool: FileParser
    participant Generator as Tool: Generator
    participant AI as AI Server (Ollama)

    %% Step 1: User Initiation
    User->>UI: 1. Selects Model & Input (Text/File)
    User->>UI: 2. Clicks "Generate Test Cases"

    %% Step 2: Request Preparation
    activate UI
    UI->>UI: Validate Inputs
    UI->>App: POST /generate (FormData)
    activate App

    %% Step 3: Backend Processing
    Note right of App: Handle Multipart Request
    
    alt File Uploaded
        App->>Parser: extract_text_from_file(filepath)
        Parser-->>App: Raw Text Content
        App->>App: Construct Prompt + File Context
    else Manual Text
        App->>App: Use User Prompt directly
    end

    %% Step 4: AI Generation
    App->>Generator: generate_cases_from_server(prompt, model)
    activate Generator
    
    Note over Generator, AI: Enforces JSON Schema (TID, Type, Priority...)
    Generator->>AI: POST /v1/chat/completions
    activate AI
    AI-->>Generator: Raw JSON Response
    deactivate AI
    
    Generator->>Generator: Clean & Parse JSON (with repair_json)
    Generator-->>App: List[TestCase Objects]
    deactivate Generator

    %% Step 5: Response & Rendering
    App-->>UI: JSON Response {test_cases, time, model}
    deactivate App
    
    UI->>UI: Render Results Table
    deactivate UI

    %% Step 6: Export Flow
    opt User Clicks Download
        User->>UI: Click "Download Excel"
        UI->>App: POST /download (test_cases[])
        activate App
        App->>App: Pandas DataFrame -> Excel Bytes
        App-->>UI: File Attachment (.xlsx)
        deactivate App
        UI->>User: Save File
    end
```

## Key Modules

1.  **Frontend (`index.html`)**: Handles state (input mode, model selection) and renders the response.
2.  **Backend (`app.py`)**: Orchestrator that routes requests and manages temporary files.
3.  **File Parser (`file_parser.py`)**: Extracts text from PDF, DOCX, and TXT files.
4.  **Generator Tool (`generate_test_cases.py`)**: Manages the LLM prompt engineering and JSON validation.
5.  **AI Server (Ollama)**: Local inference server (Port 11434).

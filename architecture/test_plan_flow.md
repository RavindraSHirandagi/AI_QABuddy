# System Architecture: Test Plan Generation Flow

This document visualizes the end-to-end data flow for generating a Master Test Plan using **QA TestPlan Buddy**.

## Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant UI as Frontend (index.html)
    participant App as Flask Server (app.py)
    participant Parser as Tool: FileParser
    participant PlanGen as Tool: PlanGenerator
    participant AI as AI Server (Ollama)

    %% Step 1: User Initiation
    User->>UI: 1. Switches to "TestPlan Buddy" Tab
    User->>UI: 2. Enters Scope or Uploads Spec (PDF/DOCX)
    User->>UI: 3. Clicks "Generate Test Plan"

    %% Step 2: Request Preparation
    activate UI
    UI->>UI: Validate Inputs (Separate logic from TestCases)
    UI->>App: POST /generate_plan (FormData)
    activate App

    %% Step 3: Backend Processing
    Note right of App: Handle Multipart Request
    
    alt File Uploaded
        App->>Parser: extract_text_from_file(filepath)
        Parser-->>App: Raw Spec Content
        App->>App: Construct Prompt + Spec Context
    else Manual Text
        App->>App: Use User Scope Description
    end

    %% Step 4: AI Generation (High Latency)
    App->>PlanGen: generate_plan_from_server(prompt, model)
    activate PlanGen
    
    Note over PlanGen, AI: Enforces "Master Plan" 10-Section Format
    PlanGen->>AI: POST /v1/chat/completions
    activate AI
    Note right of AI: Processing (Timeout: 2000s)
    AI-->>PlanGen: Raw JSON Response (10 Sections)
    deactivate AI
    
    PlanGen->>PlanGen: Clean Markdown Blocks & Parse/Repair JSON
    PlanGen-->>App: Test Plan Object (Dict)
    deactivate PlanGen

    %% Step 5: Response & Rendering
    App-->>UI: JSON Response {test_plan, time, model}
    deactivate App
    
    activate UI
    UI->>UI: renderPlan() -> DOM Injection
    Note right of UI: Dynamically creating Sections (Intro -> Approvals)
    UI-->>User: Displays Formatted Test Plan
    deactivate UI

    %% Step 6: Export Flow
    opt User Clicks Download
        User->>UI: Selects Format (DOCX/PDF) & Clicks Download
        alt DOCX
            UI->>App: POST /download_plan
            App->>App: Generate DOCX
            App-->>UI: File Attachment (.docx)
        else PDF
            UI->>App: POST /download_plan_pdf
            App->>App: Generate PDF (ReportLab)
            App-->>UI: File Attachment (.pdf)
        end
        UI->>User: Save File (LLM_TestPlan_<model>.<ext>)
    end
```

## Key Differences from Test Case Flow

1.  **Endpoint**: Uses `/generate_plan` instead of `/generate`.
2.  **Tooling**: Uses `generate_test_plan.py` which has specific logic for longer timeouts (33 mins) and robust JSON repair.
3.  **Strict Structure**: The prompt enforces a strict **10-Section Standard** (Introduction, Scope, Strategy, Environment, Pass/Fail, Deliverables, Schedule, Roles, Risks, Approvals).
4.  **Rendering**: The UI renders a structured document view.
5.  **Dual Export**: Supports both DOCX and PDF export.

# Progress Log

## Initialization
- Created project structure (tools, architecture, .tmp)
- Created memory files (task_plan, findings, progress, verified Ollama connection)
- Built 3-layer architecture (SOPs, Navigation, Tools)
- Encountered empty response issue with `qwen3:4b` in JSON mode
- Fixed: Disabled `format: "json"` in API call to allow text output from VL model
- Validated end-to-end flow with sample input

## Phase 2: Enhancements (LM Studio & UX)
- **Migration to LM Studio**: Replaced Ollama with LM Studio (local OpenAI-compatible server) for better windows compatibility and model management.
- **Robustness**: Implemented auto-discovery of models and auto-start logic using `lms` CLI tool.
- **UI Enhancements**:
  - Added Model Selection Dropdown (dynamic fetching).
  - Replaced manual Server URL input with specific **Status Box** for real-time connection feedback.
  - Implemented Dark Mode compatibility for dropdowns.
- **Feature: PRD Upload**:
  - Added support for PDF, DOCX, and TXT file uploads.
  - Implemented Toggle Switch between "Feature Info" (Text) and "Attach PRD" (File).
  - Integrated `pypdf` and `python-docx` for backend text extraction.
- **Enhancements & Fixes**:
  - **Generation Logic**: Mandated minimum 5 test cases per category (Functional, Security, etc.) via strict prompt engineering.
  - **UI Tables**: Added columns for TID, Type, and Priority.
  - **Excel Export**: Updated to include new columns and use dynamic filenames (`LLM_TestCase_<model_name>.xlsx`).
  - **Bug Fix**: Fixed invisible Rocket emoji in header by isolating gradient text styles.

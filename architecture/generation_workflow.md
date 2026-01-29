# Test Case Generation SOP

## Goal
Generate structured test cases from a user prompt using a local LLM and save them to an Excel file.

## Inputs
- `user_requirements` (str): Free-text description OR parsed text from uploaded file.
- `input_file` (Optional): PDF, DOCX, or TXT file containing requirements (PRD).
- `model_name` (str): Selected from LM Studio via UI.

## Workflow
1.  **Input Processing**:
    -   **Text Mode**: Use user typed input directly.
    -   **File Mode**: 
        -   Upload file to `.tmp/`.
        -   Parse content using `python-docx` or `pypdf`.
        -   Append extracted text to the prompt.
2.  **LLM Generation (LM Studio)**:
    -   **API**: Post to `http://localhost:1234/v1/chat/completions`.
    -   **Prompt Engineering**:
        -   Enforce **at least 5 cases** per category (Functional, Non-Functional, Negative, Positive, Security).
        -   Mandate JSON structure with fields: `TID`, `TestCaseName`, `Steps`, `Expected_Result`, `Priority`, `TestType`.
    -   **Validation**: Clean and parse JSON response.
3.  **Data Transformation**:
    -   Convert JSON list to Pandas DataFrame.
    -   Normalize columns to preferred order: `TID`, `TestType`, `Priority`, `TestCaseName`, `Steps`, `Expected_Result`.
4.  **Export**:
    -   Save DataFrame to `LLM_TestCase_<CleanedModelName>.xlsx`.
    -   Return execution time and model name in response.

## Error Handling
-   **LM Studio Connection**:
    -   Frontend checks `/v1/models`.
    -   If failed, backend attempts `lms server start` (if configured).
-   **File Parse Error**: Return 400 with specific parsing failure message.
-   **Excel Save Error**: Permission issues (file open?) -> Prompt user to close file.

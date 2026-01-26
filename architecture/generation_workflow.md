# Test Case Generation SOP

## Goal
Generate structured test cases from a user prompt using a local LLM and save them to an Excel file.

## Inputs
- `user_requirements` (str): Free-text description of the feature or logic to test.
- `model_name` (str): Defaults to "qwen3:4b".

## Workflow
1.  **Input Normalization**: Clean the user input string.
2.  **LLM Generation**:
    -   Construct a system prompt demanding JSON output.
    -   Call Ollama API `/api/generate`.
    -   **Validation**: Ensure JSON parsing succeeds. If it fails, retry or error out.
3.  **Data Transformation**:
    -   Convert JSON list of objects to a Pandas DataFrame.
    -   Columns: `Test Name`, `Steps`, `Expected Result`.
4.  **Export**:
    -   Save DataFrame to `test_cases.xlsx`.
    -   Verify file existence.

## Error Handling
-   **Ollama Connection Error**: Exit gracefully with a clear message.
-   **JSON Parse Error**:
    -   Retry once with a "fix json" prompt?
    -   OR fallback to regex extraction.
-   **Excel Save Error**: Permission issues (file open?) -> Prompt user to close file.

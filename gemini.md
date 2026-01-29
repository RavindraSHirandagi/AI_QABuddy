# Project Constitution (gemini.md)

## Data Schemas
### Input
- `user_requirements`: String (Raw text pasted by user or parsed from file).
- `input_file`: Optional PDF/DOCX/TXT file.

### Intermediate (LLM Response)
- Format: JSON
- Structure:
    ```json
    {
      "test_cases": [
        {
          "TID": "TC_001",
          "TestCaseName": "String",
          "Steps": "String",
          "Expected_Result": "String",
          "Priority": "High/Medium/Low",
          "TestType": "Functional/Security/etc"
        }
      ]
    }
    ```

### Output (Payload)
- File: `LLM_TestCase_<ModelName>.xlsx`
- Columns: `TID`, `TestType`, `Priority`, `TestCaseName`, `Steps`, `Expected Result`

## Behavioral Rules
- **Model**: Use local models via **LM Studio** (OpenAI-compatible API).
- **Test Coverage**: MANDATORY 5 test cases per category (Functional, Non-Functional, Negative, Positive, Security).
- **Reliability**: Always validate JSON structure before parsing.
- **Self-Healing**: If JSON is malformed, attempt to repair or regex extract.

## Architectural Invariants
- 3-Layer Architecture:
    1. Architecture (SOPs)
    2. Navigation (Logic)
    3. Tools (Atomic Scripts)
- Code only starts after Payload shape confirmation.
- `gemini.md` is law.

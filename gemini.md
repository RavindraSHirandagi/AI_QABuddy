# Project Constitution (gemini.md)

## Data Schemas
### Input
- `user_requirements`: String (Raw text pasted by the user via CLI).

### Intermediate (LLM Response)
- Format: JSON
- Structure:
    ```json
    {
      "test_cases": [
        {
          "test_name": "String (Concise title)",
          "steps": "String (Numbered list or clear text)",
          "expected_result": "String (Clear outcome)"
        }
      ]
    }
    ```

### Output (Payload)
- File: `test_cases.xlsx` (Excel)
- Columns: `Test Name`, `Steps`, `Expected Result`

## Behavioral Rules
- **Model**: Use `qwen2.5` (or latest available 'qwen' variant) via Ollama.
- **Reliability**: Always validate JSON structure before parsing.
- **User Interaction**: detailed prompts are not required; the system should infer standard test coverage (positive, negative, edge cases) if not specified.
- **Self-Healing**: If JSON is malformed, attempt to repair or re-prompt the model.

## Architectural Invariants
- 3-Layer Architecture:
    1. Architecture (SOPs)
    2. Navigation (Logic)
    3. Tools (Atomic Scripts)
- Code only starts after Payload shape confirmation.
- `gemini.md` is law.

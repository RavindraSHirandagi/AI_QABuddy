# Project Constitution (gemini.md)

## Data Schemas
### Input
- `user_requirements`: String (Raw text pasted by user or parsed from file).
- `input_file`: Optional PDF/DOCX/TXT file.

### Intermediate (LLM Output)
1. **Test Cases (JSON)**:
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
2. **Test Plan (JSON)**:
    ```json
    {
      "plan_title": "String",
      "sections": [
        { "heading": "1.0 Introduction", "content": "..." },
        { "heading": "2.0 Scope", "content": "..." }
        // ... (Strict 10 sections)
      ]
    }
    ```

### Output (Payload)
- **Test Cases**: `LLM_TestCase_<ModelName>.xlsx`
- **Test Plan**: 
    - `LLM_TestPlan_<ModelName>.docx`
    - `LLM_TestPlan_<ModelName>.pdf`

## Behavioral Rules
- **Model Provider**: **Ollama** (Default: `http://localhost:11434`).
- **Test Coverage**: MANDATORY 5 test cases per category (Functional, Non-Functional, Negative, Positive, Security).
- **Test Plan**: MANDATORY 10-section standard format.
- **Reliability**: Always validate JSON structure before parsing.
- **Self-Healing**: Use `repair_json` to fix malformed or truncated LLM responses.
- **Timeouts**: Allow up to **2000 seconds** (~33 mins) for generation.

## Architectural Invariants
- 3-Layer Architecture:
    1. Architecture (SOPs)
    2. Navigation (Logic)
    3. Tools (Atomic Scripts)
- `gemini.md` is law.
- Code only starts after Payload shape confirmation.

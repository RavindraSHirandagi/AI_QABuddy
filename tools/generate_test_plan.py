import requests
import json
import sys
import re

# --- HELPER: Auto-Repair Malformed JSON (Copied from generate_test_cases.py) ---
def repair_json(json_str):
    if not isinstance(json_str, str):
        return json_str

    print("DEBUG: Original JSON length:", len(json_str))
    
    # Pre-cleaning: simple whitespace strip
    json_str = json_str.strip()
    
    # 1. Strip Markdown Code Blocks (Common issue with strict mode)
    if json_str.startswith("```json"):
        json_str = json_str[7:]
    elif json_str.startswith("```"):
        json_str = json_str[3:]
    if json_str.endswith("```"):
        json_str = json_str[:-3]
    json_str = json_str.strip()

    # 3. Fix common missing comma issues (e.g. } { -> }, {)
    json_str = re.sub(r'\}\s*\{', '}, {', json_str)
    
    # 4. Stack-based Balance & String Closure
    stack = []
    in_string = False
    escape = False
    
    for char in json_str:
        if in_string:
            if char == '\\' and not escape:
                escape = True
            elif char == '"' and not escape:
                in_string = False
            else:
                escape = False
        else:
            if char == '"':
                in_string = True
            elif char == '{':
                stack.append('}')
            elif char == '[':
                stack.append(']')
            elif char == '}' or char == ']':
                if stack and stack[-1] == char:
                    stack.pop()

    # 5. Clean trailing comma if present at EOF (before closing)
    json_str = json_str.rstrip()
    if json_str and json_str[-1] == ',':
        json_str = json_str[:-1]

    # 6. Close String if Open
    if in_string:
        json_str += '"'
        print("DEBUG: Closed unclosed string.")

    # 7. Close Braces/Brackets from Stack (LIFO)
    while stack:
        closer = stack.pop()
        json_str += closer
        print(f"DEBUG: Appended missing '{closer}'")
        
    return json_str

def generate_plan_from_server(prompt, model, base_url="http://localhost:11434"):
    """
    Generates a Test Plan from an AI Server (e.g. Ollama) given a prompt.
    Returns a dictionary representing the plan.
    """
    base_url = base_url.rstrip('/')
    
    # Connection logic
    url = f"{base_url}/v1/chat/completions"
    
    if not model:
        return {"error": "No model specified. Please select a model."}

    # System instruction
    system_message = "You are a QA Manager. Create a comprehensive Test Plan. Output ONLY valid JSON."
    
    user_message = f"""
    Act as a QA Lead. Create a **Comprehensive Test Plan** for: "{prompt}".

    ### RULES:
    1.  **Format**: Return ONLY valid JSON.
    2.  **Standards**: You MUST include the following 10 sections in order:

    ### SECTIONS:
    1.  **Introduction & Overview**: Purpose, project background, and goals.
    2.  **Scope**: Clearly define In-Scope vs Out-of-Scope features.
    3.  **Test Strategy & Types**: Functional, Security, Performance, tools, levels.
    4.  **Test Environment & Data**: Hardware, software, network, data sets.
    5.  **Pass/Fail Criteria**: Success conditions (e.g., 0 critical bugs) and Suspension criteria.
    6.  **Deliverables**: Reports, logs, documentation to be provided.
    7.  **Schedule & Milestones**: Key testing dates/phases.
    8.  **Roles & Responsibilities**: Team structure (QA Lead, Tester, Dev, etc.).
    9.  **Risks & Mitigation**: Potential obstacles and backup plans.
    10. **Approvals**: Sign-off placeholders.

    ### JSON Structure:
    {{
      "plan_title": "Test Plan for [Feature]",
      "sections": [
        {{ "heading": "1.0 Introduction & Overview", "content": "..." }},
        {{ "heading": "2.0 Scope", "content": "..." }},
        // ... continue for all 10 sections
      ]
    }}
    """
    
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        "temperature": 0.7,
        "stream": False,
        "max_tokens": 10000 # Explicitly allowing more tokens
    }
    
    try:
        print(f"Generating Test Plan with {model} via AI Server...")
        response = requests.post(url, json=payload, timeout=2000)
        response.raise_for_status()
        
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            raw_response = data["choices"][0]["message"]["content"]
        else:
            msg = "Error: AI Server returned no choices."
            print(msg)
            return {"error": msg}
        
        # --- Save Raw Output ---
        import os
        import time
        tmp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.tmp')
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
        
        timestamp = int(time.time())
        dump_file = os.path.join(tmp_dir, f"plan_response_{timestamp}.txt")
        with open(dump_file, "w", encoding="utf-8") as f:
            f.write(raw_response)
        # ---------------------
        
        # Cleanup JSON logic
        
        # 1. Try to find content within markdown code blocks first
        markdown_match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_response, re.DOTALL)
        to_parse = raw_response
        if markdown_match:
            to_parse = markdown_match.group(1).strip()
            
        # 2. Robust extraction: Find the first '{' and the last '}' 
        # to isolate valid JSON from any conversational preamble/postamble.
        json_match = re.search(r"(\{.*\})", to_parse, re.DOTALL)
        if json_match:
             clean_response = json_match.group(1)
        else:
             # Fallback if no braces found (unlikely but possible)
             clean_response = to_parse
            
        try:
             # Try parsing with raw_decode to handle "Extra Data" (suffix text) automatically
             try:
                 parsed, _ = json.JSONDecoder().raw_decode(clean_response)
             except json.JSONDecodeError:
                 # If raw_decode fails (likely due to truncation), fall back to standard load/strict
                 parsed = json.loads(clean_response)
            
             if "usage" in data:
                 parsed["usage"] = data["usage"]
             return parsed
        except json.JSONDecodeError as je:
            print(f"DEBUG: JSON Parse Error: {je}")
            print("DEBUG: Attempting Auto-Repair...")
            
            try:
                repaired = repair_json(clean_response)
                # Fix common markdown glitch again
                repaired = repaired.replace("```", "")
                
                # Handling Control Characters (newlines inside strings are fine in python json if escaped, but LLMs mess this up)
                # If we have unescaped newlines inside strings, strict=False might not help.
                # repair_json doesn't fix unescaped control chars (0x00-0x1f).
                # But typically the specific error "Invalid control character" implies newlines in strings.
                
                parsed = json.loads(repaired, strict=False) # strict=False allows control chars
                return parsed
            except Exception as e2:
                msg = f"Repair failed: {e2}"
                print(msg)
                print(f"Raw Output form LLM: {raw_response[:500]}") 
                return {"error": msg + f" Raw: {raw_response[:100]}..."}
        
    except requests.exceptions.RequestException as e:
        msg = f"Error generating plan: {e}"
        print(msg)
        return {"error": msg}
    except Exception as e:
        msg = f"An unexpected error occurred: {e}"
        print(msg)
        return {"error": msg}

if __name__ == "__main__":
    # Test script 
    sys.path.append('.') 
    from handshake import check_ai_server
    
    print("Checking for models...")
    models = check_ai_server()
    if not models:
        print("No models found. Ensure AI Server (Ollama) is running.")
        sys.exit(1)
        
    model = models[0] 
    print(f"Testing with model: {model}")
    
    prompt = "A simple Login Page"
    plan = generate_plan_from_server(prompt, model)
    
    if plan:
        print(json.dumps(plan, indent=2))

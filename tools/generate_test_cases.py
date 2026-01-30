
import requests
import json
import sys
import re


# --- HELPER: Auto-Repair Malformed JSON ---
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

    # 2. Fix missing braces around array items (Prompt-specific artifact)
    # Scenario: [ "TID": ... "TID": ... ]
    # Check if we have an array that starts immediately with a key "TID" instead of {
    if re.search(r'\[\s*"TID"', json_str):
        print("DEBUG: Detected missing start braces in array.")
        # Fix the first one
        json_str = re.sub(r'\[\s*"TID"', '[ { "TID"', json_str)
        # Fix subsequent ones: replace ", "TID"" with "}, { "TID""
        json_str = re.sub(r',\s*"TID"', '}, { "TID"', json_str)
        
    # 3. Fix common missing comma issues (e.g. } { -> }, {)
    # This regex looks for '}' followed by '{' with generic whitespace
    json_str = re.sub(r'\}\s*\{', '}, {', json_str)
    
    # 4. Stack-based Balance & String Closure
    stack = []
    in_string = False
    escape = False
    
    # Track the parsing state to handle trailing commas efficiently later
    # Only iterate to build the stack
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
                # Else: Mismatched or extra closing char, we ignore for stack purposes
                # but it remains in string. 

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

def generate_cases_from_server(prompt, model, base_url="http://localhost:11434"):
    """
    Generates test cases from an OpenAI-compatible server (e.g. Ollama) given a prompt.
    Returns a list of dictionaries.
    """
    # Clean base url
    base_url = base_url.rstrip('/')

    # Standard OpenAI Chat Endpoint
    url = f"{base_url}/v1/chat/completions"
    
    if not model:
        msg = "Error: No model specified."
        print(msg)
        return {"error": msg}

    # System instruction + User prompt
    system_message = "You are a Senior QA Engineer. Output ONLY valid JSON."
    
    # Dynamic Quantity Logic
    count_match = re.search(r"\b(\d+)\s*(?:test\s*)?(?:cases|scenarios)\b", prompt, re.IGNORECASE)
    
    if count_match:
        count = int(count_match.group(1))
        quantity_rule = f"2.  **Quantity**: Generate a TOTAL of **{count}** test cases, distributed across the categories."
    else:
        quantity_rule = "2.  **Quantity**: Generate **AT LEAST 5** test cases for **EACH** category. (Total minimum 25 test cases)."

    user_message = f"""
    Act as a Senior QA Engineer. Generate detailed test cases for the following requirement: "{prompt}"

    ### RULES:
    1.  **Test Types**: You MUST generate test cases for ALL of the following categories:
        *   **Functional**
        *   **Non-Functional**
        *   **Negative**
        *   **Positive**
        *   **Security**
    {quantity_rule}
    3.  **Format**: Return ONLY valid JSON.
    4.  **Structure Constraint**: The output MUST be a JSON object containing a list named "test_cases". Each item in the list MUST be an object wrapped in curly braces {{}}.
    
    ### JSON Structure Example:
    {{
      "test_cases": [
        {{
          "TID": "TC_001",
          "TestCaseName": "Verify login",
          "Steps": "1. Open App...",
          "Expected_Result": "Success",
          "Priority": "High",
          "TestType": "Functional"
        }},
        {{
          "TID": "TC_002",
          "TestCaseName": "Verify logout",
          "Steps": "1. Click logout...",
          "Expected_Result": "Logged out",
          "Priority": "Medium",
          "TestType": "Functional"
        }}
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
        "max_tokens": 10000, 
        "stream": False
    }
    
    try:
        print(f"Generating test cases with {model} via AI Server ({base_url})...")
        print(f"DEBUG Payload: {json.dumps(payload)}") 
        
        # Requests
        response = requests.post(url, json=payload, timeout=2000)
        response.raise_for_status()
        
        data = response.json()
        
        # OpenAI format
        if "choices" in data and len(data["choices"]) > 0:
            choice = data["choices"][0]
            raw_response = choice["message"]["content"]
            finish_reason = choice.get("finish_reason", "unknown")
            print(f"DEBUG: finish_reason: {finish_reason}")
            
            # Log Token Usage
            if "usage" in data:
                print(f"DEBUG: Usage: {data['usage']}")
                
            if not raw_response:
                msg = f"Error: Model returned empty response. Finish Reason: {finish_reason}."
                print(msg)
                print(f"DEBUG: Full Choice: {json.dumps(choice)}")
                return {"error": msg}

            # --- Save Raw Output ---
            import os
            import time
            tmp_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.tmp')
            if not os.path.exists(tmp_dir):
                os.makedirs(tmp_dir)
            
            timestamp = int(time.time())
            dump_file = os.path.join(tmp_dir, f"raw_response_{timestamp}.txt")
            with open(dump_file, "w", encoding="utf-8") as f:
                f.write(raw_response)
            # ---------------------
            
        else:
            msg = "Error: Unexpected response format from AI Server."
            print(msg)
            print(f"Full response: {data}")
            return {"error": msg}
        
        # Attempt to clean up JSON
        markdown_match = re.search(r"```(?:json)?\s*(.*?)\s*```", raw_response, re.DOTALL)
        to_parse = raw_response
        if markdown_match:
            to_parse = markdown_match.group(1).strip()
        
        # Find JSON boundaries
        json_start_idx = -1
        json_end_idx = -1
        
        first_brace = to_parse.find('{')
        first_bracket = to_parse.find('[')
        
        if first_brace != -1 and first_bracket != -1:
            json_start_idx = min(first_brace, first_bracket)
        elif first_brace != -1:
            json_start_idx = first_brace
        elif first_bracket != -1:
            json_start_idx = first_bracket
            
        if json_start_idx != -1:
            last_brace = to_parse.rfind('}')
            last_bracket = to_parse.rfind(']')
            json_end_idx = max(last_brace, last_bracket)
            
            if json_end_idx > json_start_idx:
                to_parse = to_parse[json_start_idx : json_end_idx+1]
        
        # Try parsing with raw_decode to handle "Extra Data" (suffix text) automatically
        try:
             parsed, _ = json.JSONDecoder().raw_decode(to_parse)
        except json.JSONDecodeError:
             # If raw_decode fails (likely due to truncation), fall back to standard repair
             parsed = json.loads(to_parse)
             
        if isinstance(parsed, dict) and "test_cases" in parsed:
             result = parsed["test_cases"]
        else:
             result = parsed
             
        # Normalize result to be a dictionary containing both data and metadata if not already
        # However, app.py expects a list or a dict. 
        # If it's a list (test cases), we need to wrap it or app.py needs to handle it.
        # Looking at app.py, it expects {"test_cases": cases}.
        # So we should probably capture usage in a separate variable and let app.py handle it, 
        # OR return a tuble/dict with metadata.
        # Let's check app.py... app.py calls this function.
        # To avoid breaking changes, let's look at how we CAN pass this back.
        # The best way without breaking the signature "list of dicts" is to attach it to the first item? No, that's messy.
        
        # Actually, let's check app.py again. 
        # cases = generate_cases_from_server(...)
        # return jsonify({"test_cases": cases...})
        
        # If we change return type to dict { "cases": [], "usage": {} }, we break app.py.
        # But wait, `parsed` IS a dict {"test_cases": [...]}.
        # So we can just add "usage" to `parsed`!
        
        if isinstance(parsed, dict):
            if "usage" in data:
                parsed["usage"] = data["usage"]
            return parsed
        elif isinstance(parsed, list):
            # If it returned a raw list, wrap it
            ret = {"test_cases": parsed}
            if "usage" in data:
                ret["usage"] = data["usage"]
            return ret
        else:
             return parsed

    except requests.exceptions.RequestException as e:
        msg = f"Error communicating with AI Server: {e}"
        print(msg)
        return {"error": msg}
    except json.JSONDecodeError:
        print("DEBUG: JSON Parse failed. Attempting auto-repair...")
        try:
             target_str = locals().get('to_parse', raw_response)
             repaired_json = repair_json(target_str)
             repaired_json = repaired_json.replace("```", "")
             
             parsed = json.loads(repaired_json)
             if "test_cases" in parsed:
                 print("DEBUG: Auto-repair success!")
                 # We still want to return dictionary with usage if possible
                 if "usage" in data:
                     parsed["usage"] = data["usage"]
                 return parsed
             else:
                 return parsed
        except Exception as repair_e:
             print(f"DEBUG: Repair failed: {repair_e}")
             
        msg = "Error: Model did not return valid JSON."
        print(msg)
        return {"error": msg + f" Raw: {raw_response[:100]}..."}
    except Exception as e:
        msg = f"An unexpected error occurred: {e}"
        print(msg)
        return {"error": msg}

if __name__ == "__main__":
    # Test run
    test_input = "Login page"
    result = generate_cases_from_server(test_input, "llama3") 
    if result:
        print(json.dumps(result, indent=2))

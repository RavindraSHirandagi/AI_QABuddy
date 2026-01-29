import requests
import json
import sys

def generate_cases_from_lm_studio(prompt, model, base_url="http://localhost:1234"):
    """
    Generates test cases from LM Studio (OpenAI compatible) given a prompt.
    Returns a list of dictionaries.
    """
    # Clean base url
    base_url = base_url.rstrip('/')

    # Try flexible connection if default
    candidates = [base_url]
    if "localhost" in base_url:
        candidates.append(base_url.replace("localhost", "127.0.0.1"))
    elif "127.0.0.1" in base_url:
        candidates.append(base_url.replace("127.0.0.1", "localhost"))
    
    url = None
    
    # Simple check to see which one works
    for base in candidates:
        try:
            # Quick check if server is reachable
            test_resp = requests.get(f"{base}/v1/models", timeout=1)
            if test_resp.status_code == 200:
                url = f"{base}/v1/chat/completions"
                break
        except:
            continue
            
    if not url:
        print(f"Error: Could not find running LM Studio instance at {base_url}.")
        # Fallback to provided url even if check failed, just in case
        url = f"{base_url}/v1/chat/completions"
    
    if not model:
        print("Error: No model specified.")
        return None

    # System instruction + User prompt
    system_message = "You are a QA Engineer. Output ONLY valid JSON."
    
    user_message = f"""
    Act as a Senior QA Engineer. Generate detailed test cases for the following requirement: "{prompt}"

    ### RULES:
    1.  **Test Types**: You MUST generate test cases for ALL of the following categories:
        *   **Functional**
        *   **Non-Functional**
        *   **Negative**
        *   **Positive**
        *   **Security**
    2.  **Quantity**: Generate **AT LEAST 5** test cases for **EACH** category. (Total minimum 25 test cases).
    3.  **Format**: Return ONLY valid JSON.
    
    ### JSON Structure:
    {{
      "test_cases": [
        {{
          "TID": "TC_001",
          "TestCaseName": "Verify user login with valid credentials",
          "Steps": "1. Open URL\\n2. Enter User\\n3. Enter Pass\\n4. Click Login",
          "Expected_Result": "User should be logged in successfully.",
          "Priority": "High",
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
        "stream": False
    }
    
    try:
        print(f"Generating test cases with {model} via LM Studio...")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        
        # OpenAI format: choices[0].message.content
        if "choices" in data and len(data["choices"]) > 0:
            raw_response = data["choices"][0]["message"]["content"]
        else:
            print("Error: Unexpected response format from LM Studio.")
            print(f"Full response: {data}")
            return None
        
        # DEBUG: Print raw response
        print(f"DEBUG info: {raw_response[:200]}...")

        # Attempt to clean up JSON (Remove markdown ```json ... ```)
        import re
        json_match = re.search(r"\{.*\}", raw_response, re.DOTALL)
        if json_match:
            raw_response = json_match.group(0)
        
        # Parse JSON
        parsed = json.loads(raw_response)
        
        # Handle cases where the model wraps it in a top-level key or just returns the list
        if "test_cases" in parsed:
             return parsed["test_cases"]
        else:
             return parsed

    except requests.exceptions.RequestException as e:
        print(f"Error communicating with LM Studio: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Model did not return valid JSON.")
        print(f"Raw output snippet: {raw_response}...")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    # Test run (ensure you have a model running or replace validation)
    test_input = "Login page with username and password"
    # Pass a dummy model name for the test run if needed, or rely on caller
    result = generate_cases_from_lm_studio(test_input, "mistral") 
    if result:
        print(json.dumps(result, indent=2))

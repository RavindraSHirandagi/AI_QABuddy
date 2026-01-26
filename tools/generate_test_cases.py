import requests
import json
import sys

def generate_cases_from_ollama(prompt, model="qwen3:4b"):
    """
    Generates test cases from Ollama given a prompt.
    Returns a list of dictionaries.
    """
    url = "http://localhost:11434/api/generate"
    
    
    # Simplified prompt for VL model which might behave better with direct instructions
    final_prompt = f"""
    You are a QA Engineer. Generate test cases for this requirement: "{prompt}"
    
    Return ONLY valid JSON with this structure:
    {{
      "test_cases": [
        {{
          "test_name": "...",
          "steps": "...",
          "expected_result": "..."
        }}
      ]
    }}
    """
    
    payload = {
        "model": model,
        "prompt": final_prompt,
        "stream": False
        # "format": "json" # Disabled to prevent empty response from VL model
    }
    
    try:
        print(f"Generating test cases with {model}...")
        response = requests.post(url, json=payload)
        response.raise_for_status()
        
        data = response.json()
        raw_response = data.get("response", "")
        
        # DEBUG: Print raw response to see what went wrong
        print(f"DEBUG info: {raw_response}")

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
        print(f"Error communicating with Ollama: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: Model did not return valid JSON.")
        print(f"Raw output snippet: {raw_response}...")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

if __name__ == "__main__":
    # Test run
    test_input = "Login page with username and password"
    result = generate_cases_from_ollama(test_input)
    print(json.dumps(result, indent=2))

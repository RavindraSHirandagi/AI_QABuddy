
import requests
import json
import sys
import subprocess
import time

def check_ai_server(base_url="http://localhost:11434"):
    """
    Checks if the AI Server (e.g. Ollama) is running and returns a list of available models.
    """
    # Ensure base_url doesn't end with slash for consistency
    base_url = base_url.rstrip('/')
    
    # We try both localhost and 127.0.0.1 (if default) to be robust
    urls = [f"{base_url}/v1/models"]
    if "localhost" in base_url:
        urls.append(base_url.replace("localhost", "127.0.0.1") + "/v1/models")
    elif "127.0.0.1" in base_url:
        urls.append(base_url.replace("127.0.0.1", "localhost") + "/v1/models")
        
    # Also try Ollama standard /api/tags if /v1/models fails (though Ollama supports /v1 now)
    if "11434" in base_url:
        urls.append(f"{base_url}/api/tags")
    
    def try_connect():
        for url in urls:
            try:
                print(f"DEBUG: Attempting to connect to AI Server at {url}...")
                response = requests.get(url, timeout=2) 
                if response.status_code == 200:
                    print(f"SUCCESS: Connected to AI Server at {url}")
                    data = response.json()
                    
                    # Handle Ollama /api/tags format
                    if "models" in data:
                         models = data["models"]
                         # Ollama format: list of dicts with 'name'
                         return [m['name'] for m in models]

                    # Handle OpenAI /v1/models format
                    models = data.get('data', [])
                    
                    model_names = []
                    for m in models:
                        if 'id' in m:
                            model_names.append(m['id'])
                            print(f"Model found: {m['id']}")
                            
                    return model_names
            except requests.exceptions.ConnectionError:
                pass
            except Exception as e:
                print(f"ERROR: Connection error: {e}")
        return None

    # First Attempt
    models = try_connect()
    if models is not None:
        return models

    print(f"ERROR: Could not connect to AI Server at {base_url}. Is it running?")
    return []

if __name__ == "__main__":
    check_ai_server()

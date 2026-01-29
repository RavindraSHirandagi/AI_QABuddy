
import requests
import json
import sys
import subprocess
import time

def check_lm_studio(base_url="http://localhost:1234"):
    # Ensure base_url doesn't end with slash for consistency
    base_url = base_url.rstrip('/')
    
    # We try both localhost and 127.0.0.1 (if default) to be robust
    urls = [f"{base_url}/v1/models"]
    if "localhost" in base_url:
        urls.append(base_url.replace("localhost", "127.0.0.1") + "/v1/models")
    elif "127.0.0.1" in base_url:
        urls.append(base_url.replace("127.0.0.1", "localhost") + "/v1/models")
    
    def try_connect():
        for url in urls:
            try:
                print(f"DEBUG: Attempting to connect to LM Studio at {url}...")
                response = requests.get(url, timeout=2) 
                if response.status_code == 200:
                    print(f"SUCCESS: Connected to LM Studio at {url}")
                    data = response.json()
                    models = data.get('data', [])
                    
                    # Log full metadata for debug
                    # In newer LM Studio versions (0.2.x+), /v1/models lists ALL compatible files.
                    # It does not explicitly flag 'loaded'.
                    # However, we can try to filter by 'owned_by' or similar if it distinguishes.
                    # For now, we return all, but we will print them to help user debug.
                    for m in models:
                        print(f"Model found: {m['id']}")

                    model_names = [m['id'] for m in models]
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

    # If failed, try to start server using LMS CLI
    print(f"WARNING: Could not connect. Attempting to start LM Studio server via CLI (`lms server start`).")
    try:
        # Check if lms is installed
        subprocess.run(["lms", "version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Start server (detached)
        print("Starting LM Studio server...")
        subprocess.Popen(["lms", "server", "start"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for it to come up (max 10 seconds)
        for i in range(10):
            print(f"Waiting for server to start... ({i+1}/10)")
            time.sleep(1)
            models = try_connect()
            if models is not None:
                print("Server started successfully!")
                return models
                
    except FileNotFoundError:
        print("ERROR: `lms` CLI tool not found. Please install LM Studio CLI.")
    except Exception as e:
        print(f"ERROR: Failed to auto-start server: {e}")

    print(f"ERROR: Could not connect to LM Studio at {base_url}. Is it running?")
    return []

if __name__ == "__main__":
    check_lm_studio()

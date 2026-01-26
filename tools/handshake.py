
import requests
import json
import sys

def check_ollama():
    url = "http://localhost:11434/api/tags"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"SUCCESS: Connected to Ollama at {url}")
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]
            print("Available models:", model_names)
            return model_names
        else:
            print(f"ERROR: Ollama responded with status code {response.status_code}")
            return []
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to Ollama. Is it running?")
        return []

if __name__ == "__main__":
    check_ollama()

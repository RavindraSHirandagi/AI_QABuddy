import requests
import json
import sys

# Try to find a model first
try:
    models_url = "http://localhost:1234/v1/models"
    resp = requests.get(models_url)
    if resp.status_code == 200:
        models = resp.json().get('data', [])
        if models:
            model_name = models[0]['id']
        else:
            model_name = "local-model" # Fallback
    else:
        model_name = "local-model"
except:
    print("Could not connect to LM Studio at http://localhost:1234")
    sys.exit(1)

url = "http://localhost:1234/v1/chat/completions"
payload = {
    "model": model_name,
    "messages": [
        {"role": "user", "content": "Hello, are you there?"}
    ],
    "stream": False
}

print(f"Testing model {model_name} on LM Studio...")
try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
except Exception as e:
    print(f"Error: {e}")

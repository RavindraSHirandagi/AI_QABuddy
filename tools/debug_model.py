import requests
import json

url = "http://localhost:11434/api/generate"
payload = {
    "model": "qwen3:4b",
    "prompt": "Hello, are you there?",
    "stream": False
}

print(f"Testing model {payload['model']}...")
try:
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
except Exception as e:
    print(f"Error: {e}")

import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENROUTER_API_KEY')
print(f"API Key: {api_key[:20]}...")

# Test with working free models
models = [
    "google/gemini-flash-1.5-8b",
    "meta-llama/llama-3.1-8b-instruct",
    "mistralai/mistral-7b-instruct"
]

for model in models:
    print(f"\nTesting: {model}")
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://talentsync.ai",
                "X-Title": "TalentSync Test"
            },
            json={
                "model": model,
                "messages": [{"role": "user", "content": "Say hello"}],
                "max_tokens": 50
            },
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✓ SUCCESS: {data['choices'][0]['message']['content']}")
            break
        else:
            print(f"✗ FAILED: {response.text}")
    except Exception as e:
        print(f"✗ ERROR: {e}")

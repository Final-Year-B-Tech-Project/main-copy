import requests

api_key = "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"

print("Testing OpenRouter API...")
print(f"API Key: {api_key[:20]}...")

# Test with multiple models
models = [
    "google/gemini-flash-1.5-8b",
    "meta-llama/llama-3.1-8b-instruct",
    "mistralai/mistral-7b-instruct",
    "anthropic/claude-3-haiku"
]

for model in models:
    print(f"\n{'='*50}")
    print(f"Testing: {model}")
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
                "messages": [{"role": "user", "content": "Say hello in 5 words"}],
                "max_tokens": 20
            },
            timeout=15
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] SUCCESS!")
            print(f"Response: {data['choices'][0]['message']['content']}")
            print(f"\n*** THIS MODEL WORKS: {model} ***")
            break
        else:
            print(f"[X] FAILED")
            print(f"Error: {response.text[:200]}")
            
    except Exception as e:
        print(f"[X] ERROR: {e}")

print(f"\n{'='*50}")
print("Test complete")

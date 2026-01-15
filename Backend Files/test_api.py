#!/usr/bin/env python3
"""Test script to verify OpenRouter API key is working."""

import requests
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

def test_openrouter_api():
    """Test OpenRouter API with your key."""
    
    api_key = os.getenv('OPENROUTER_API_KEY')
    base_url = os.getenv('OPENROUTER_BASE_URL', 'https://openrouter.ai/api/v1')
    
    print("=== OpenRouter API Test ===")
    print(f"API Key: {api_key[:20]}..." if api_key else "No API key found")
    print(f"Base URL: {base_url}")
    print()
    
    if not api_key or api_key == 'your-actual-api-key-here':
        print("ERROR: No valid API key found in .env file")
        return False
    
    # Test with a simple request
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5000",
        "X-Title": "AI Interview Agent Test"
    }
    
    # Try different free models
    models_to_test = [
        "qwen/qwen-2.5-coder-32b-instruct:free",
        "deepseek/deepseek-r1:free",
        "z-ai/glm-4.5-air:free"
    ]
    
    for model in models_to_test:
        print(f"\nTesting model: {model}")
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Say 'Hello, API is working!' in JSON format: {\"message\": \"your response\"}"}
            ],
            "max_tokens": 100,
            "temperature": 0.1
        }
        
        try:
            response = requests.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                print(f"SUCCESS! API Response: {content}")
                return True
            elif response.status_code == 429:
                print(f"Rate limited - trying next model...")
                continue
            else:
                print(f"ERROR: {response.status_code}")
                print(f"Response: {response.text}")
                continue
                
        except Exception as e:
            print(f"EXCEPTION: {e}")
            continue
    
    print("\nAll models are rate-limited or unavailable")
    return False

if __name__ == "__main__":
    success = test_openrouter_api()
    print("\n" + "="*50)
    if success:
        print("SUCCESS: Your OpenRouter API is working correctly!")
        print("You can now run interviews with AI-generated questions.")
    else:
        print("Troubleshooting tips:")
        print("1. Check your API key at https://openrouter.ai/")
        print("2. Make sure you have credits/free tier access")
        print("3. Verify the key is correctly copied to .env file")
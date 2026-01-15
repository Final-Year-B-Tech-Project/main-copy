#!/usr/bin/env python3
"""Debug script to check environment variable loading."""

import os
from dotenv import load_dotenv

print("=== Environment Debug ===")

# Load .env file
load_dotenv()

# Check if variables are loaded
api_key = os.getenv('OPENROUTER_API_KEY')
base_url = os.getenv('OPENROUTER_BASE_URL')

print(f"API Key loaded: {bool(api_key)}")
print(f"API Key value: {api_key[:20]}..." if api_key else "None")
print(f"Base URL: {base_url}")

# Check if .env file exists
env_path = os.path.join(os.getcwd(), '.env')
print(f".env file exists: {os.path.exists(env_path)}")
print(f"Current directory: {os.getcwd()}")
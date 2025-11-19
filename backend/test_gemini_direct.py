#!/usr/bin/env python3
"""
Direct test of Gemini API key and model
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment
env_path = os.path.join(os.path.dirname(__file__), '..', 'sidecar', '.env')
load_dotenv(env_path)

api_key = os.getenv("GEMINI_API_KEY")
model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

print(f"API Key: {api_key[:20]}..." if api_key else "API Key: NOT FOUND")
print(f"Model Name: {model_name}")

if not api_key:
    print("ERROR: GEMINI_API_KEY not found in environment")
    exit(1)

try:
    genai.configure(api_key=api_key)
    print("✓ API key configured")

    # List available models
    print("\nListing available models...")
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")

    # Test the model
    print(f"\nTesting model: {model_name}")
    model = genai.GenerativeModel(model_name)
    response = model.generate_content("Say 'API test successful' in one sentence.")
    print(f"Response: {response.text}")
    print("\n✓ GEMINI API IS WORKING!")

except Exception as e:
    print(f"\n✗ ERROR: {type(e).__name__}: {str(e)}")
    exit(1)

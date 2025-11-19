#!/usr/bin/env python3
"""
Test script for Gemini API key and model availability
"""
import os
import sys

try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai package not installed")
    print("Install with: pip install google-generativeai")
    sys.exit(1)

# Test API Key
API_KEY = "AIzaSyCFe1c5oJi9D8gSm5b8InhvoIydmdDj9NE"
MODEL_NAME = "gemini-2.5-flash"

print("=" * 60)
print("GEMINI API TESTING")
print("=" * 60)
print(f"API Key: {API_KEY[:20]}...{API_KEY[-10:]}")
print(f"Model Name: {MODEL_NAME}")
print("=" * 60)

# Configure the API
genai.configure(api_key=API_KEY)

# Test 1: List available models
print("\n[TEST 1] Listing available models...")
print("-" * 60)
try:
    models = genai.list_models()
    print("Available Gemini models:")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
            if hasattr(model, 'display_name'):
                print(f"    Display Name: {model.display_name}")
            if hasattr(model, 'description'):
                print(f"    Description: {model.description}")
    print("-" * 60)
except Exception as e:
    print(f"ERROR listing models: {e}")
    print("-" * 60)

# Test 2: Try with the specified model name
print(f"\n[TEST 2] Testing with model: {MODEL_NAME}")
print("-" * 60)
try:
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content("Say 'API key is working!' in one sentence.")
    print(f"SUCCESS: {response.text}")
    print("-" * 60)
except Exception as e:
    print(f"ERROR with {MODEL_NAME}: {e}")
    print("-" * 60)

# Test 3: Try common Gemini model names
print("\n[TEST 3] Testing common Gemini model names...")
print("-" * 60)
common_models = [
    "gemini-2.0-flash",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-pro",
    "models/gemini-2.0-flash-exp",
    "models/gemini-1.5-flash",
    "models/gemini-1.5-pro"
]

for model_name in common_models:
    try:
        print(f"\nTrying: {model_name}")
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'Working!' in one word.")
        print(f"  SUCCESS: {response.text.strip()}")
    except Exception as e:
        print(f"  FAILED: {str(e)[:100]}")

print("-" * 60)
print("\nTest completed!")

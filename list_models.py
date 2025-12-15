
import google.generativeai as genai
import os



# Check environment variables first
api_keys = []
target_key = "AIzaSyA6B76kpY0wHUxreOJAQljI-7tvhWDjIu0"
api_keys.append(target_key)

if api_keys:
    genai.configure(api_key=api_keys[0])
    print(f"Using key starting with: {api_keys[0][:5]}...")
    
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
else:
    print("No keys found")

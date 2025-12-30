import google.generativeai as genai
import os

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    # Try to find one from .env
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("GEMINI_API_KEY"):
                    api_key = line.split("=")[1].strip().strip('"')
                    break
    except:
        pass

if api_key:
    genai.configure(api_key=api_key)
    try:
        print("Listing models...")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"{m.name} (input limit: {m.input_token_limit})")
    except Exception as e:
        print(f"Error: {e}")
else:
    print("No API key found.")

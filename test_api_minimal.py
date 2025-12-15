
import google.generativeai as genai
import os
from dotenv import load_dotenv
import time

load_dotenv()

# Manual key loading to be super sure
api_keys = []
with open(".env", "r") as f:
    for line in f:
        if line.startswith("GEMINI_API_KEY") and "=" in line:
             api_keys.append(line.split("=", 1)[1].strip().strip('"').strip("'"))

print(f"Found {len(api_keys)} keys.")

models_to_try = [
    "models/gemini-flash-latest",
    "models/gemini-pro-latest", 
    "models/gemini-2.0-flash-exp",
    "models/gemini-1.5-flash" # Retrying just in case
]

print(f"GenAI Version: {genai.__version__}")

for key in api_keys[:1]: # Just try the first one for now
    print(f"\nTesting Key: {key[:5]}...")
    genai.configure(api_key=key)
    
    for m in models_to_try:
        print(f"  - Trying model: {m} ... ", end="")
        try:
            model = genai.GenerativeModel(m)
            response = model.generate_content("Hello, reply with 'OK'.")
            print(f"✅ SUCCESS! Response: {response.text.strip()}")
            break # Found a working one!
        except Exception as e:
            if "429" in str(e) or "ResourceExhausted" in str(e):
                print("❌ RATE LIMIT")
            elif "404" in str(e) or "not found" in str(e):
                 print("❌ NOT FOUND")
            else:
                 print(f"❌ ERROR: {e}")

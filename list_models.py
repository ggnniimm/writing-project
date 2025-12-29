import google.generativeai as genai
import os

# Load API Key
api_keys = []
env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY") and "=" in line:
                k_val = line.split("=", 1)[1].strip().strip('"').strip("'")
                if k_val:
                    api_keys.append(k_val)

if api_keys:
    genai.configure(api_key=api_keys[0])
    print("Available Models:")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)
else:
    print("No API Key found")

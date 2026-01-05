import google.generativeai as genai
import os

def load_api_keys():
    api_keys = []
    # Check .env file in parent directory
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY") and "=" in line:
                    k_val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if k_val:
                        api_keys.append(k_val)
    return api_keys

keys = load_api_keys()
if not keys:
    print("No keys found")
else:
    genai.configure(api_key=keys[0])
    print("Listing models...")
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(m.name)

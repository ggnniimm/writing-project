
import google.generativeai as genai
import os

# Load keys
api_keys = []
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY") and "=" in line:
                 api_keys.append(line.split("=", 1)[1].strip().strip('"').strip("'"))

if len(api_keys) < 3:
    print("Need at least 3 keys to test Key #3")
    exit(1)

key3 = api_keys[2]
print(f"Testing SDK with Key #3: ...{key3[-5:]}")

genai.configure(api_key=key3)
model = genai.GenerativeModel('models/gemini-2.5-flash')

try:
    response = model.generate_content("Hello")
    print("✅ SUCCESS!")
    print(response.text)
except Exception as e:
    print(f"❌ FAILED: {e}")

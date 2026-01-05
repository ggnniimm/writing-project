import google.generativeai as genai
import os
import time

def load_keys_from_env():
    keys = []
    env_path = os.path.join(os.getcwd(), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY") and "=" in line:
                    name, val = line.split("=", 1)
                    val = val.strip().strip('"').strip("'")
                    if val:
                        keys.append((name.strip(), val))
    return keys

keys = load_keys_from_env()
leaked_keys = []

print(f"Testing {len(keys)} keys...")

for name, val in keys:
    genai.configure(api_key=val)
    model = genai.GenerativeModel('gemini-2.0-flash')
    try:
        # Simple light call to check key status
        response = model.generate_content("Hi", request_options={"timeout": 10})
        print(f"✅ {name}: OK")
    except Exception as e:
        error_msg = str(e)
        if "leaked" in error_msg.lower() or "403" in error_msg:
            print(f"❌ {name}: LEAKED ({error_msg})")
            leaked_keys.append(name)
        else:
            print(f"⚠️ {name}: ERROR ({error_msg})")

if leaked_keys:
    print("\nLeaked Keys to remove:")
    for k in leaked_keys:
        print(f"- {k}")
else:
    print("\nNo leaked keys identified.")

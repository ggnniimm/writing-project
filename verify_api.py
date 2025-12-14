
import os
import google.generativeai as genai
from google.api_core import exceptions

def verify_keys():
    print("🔍 Starting API Key Verification...")
    
    # 1. Load Keys (Same logic as update_diary.py)
    api_keys = []
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if line.strip() and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        value = value.strip().strip("'").strip('"')
                        if key.startswith("GEMINI_API_KEY") and value:
                             api_keys.append((key, value))
    
    if not api_keys:
        print("❌ No API Keys found in .env")
        return

    print(f"🔑 Found {len(api_keys)} keys. Testing each one...\n")

    for key_name, key_value in api_keys:
        print(f"👉 Testing {key_name} ({key_value[:5]}...{key_value[-5:]})")
        
        # Warning for potential typos (O vs 0)
        if "AIza" in key_value:
             # Basic heuristics
             pass
        else:
             print("   ⚠️  Warning: Key does not start with 'AIza'. Might be invalid format.")

        try:
            genai.configure(api_key=key_value)
            model = genai.GenerativeModel('models/gemini-flash-latest')
            response = model.generate_content("Say 'OK'", generation_config={"max_output_tokens": 5})
            print(f"   ✅ Valid! Response: {response.text.strip()}")
        except exceptions.InvalidArgument:
             print("   ❌ Invalid Key (InvalidArgument). Please check for typos.")
        except exceptions.ResourceExhausted:
             print("   ⚠️. Key Valid but Quota Exceeded (Rate Limited).")
        except Exception as e:
             print(f"   ❌ Error: {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    verify_keys()

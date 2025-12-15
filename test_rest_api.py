import requests
import os
import json

# Manual .env loading
# Check environment variables first
api_keys = []
target_key = os.environ.get("GEMINI_API_KEY")
api_keys.append(target_key)


models = [
    "models/gemini-1.5-flash",
    "models/gemini-1.5-flash-latest",
    "models/gemini-2.0-flash-exp",
    "models/gemini-2.5-flash" 
]

for i, key in enumerate(api_keys):
    masked_key = f"...{key[-5:]}"
    print(f"\n🔑 Testing Key #{i+1} ({masked_key})")
    for m in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/{m}:generateContent?key={key}"
        headers = {'Content-Type': 'application/json'}
        data = {
            "contents": [{
                "parts": [{"text": "Hello"}]
            }]
        }
        
        print(f"  - Model: {m:<30}", end=" ")
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 200:
                print("✅ SUCCESS!")
            else:
                print(f"❌ FAILED: {response.status_code}")
                # Print the error details to see Day vs Minute
                try:
                    err = response.json()
                    print(json.dumps(err, indent=2))
                except:
                    print(response.text[:200])
        except Exception as e:
            print(f"❌ ERROR: {e}")

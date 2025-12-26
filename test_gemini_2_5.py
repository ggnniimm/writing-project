
import google.generativeai as genai
import os
import time

# Load keys
api_keys = []
if os.path.exists(".env"):
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("GEMINI_API_KEY") and "=" in line:
                 api_keys.append(line.split("=", 1)[1].strip().strip('"').strip("'"))

if not api_keys:
    print("❌ No API Keys found!")
    exit(1)

key_to_use = api_keys[0] # Try first key
print(f"Testing SDK with Key: ...{key_to_use[-5:]}")

genai.configure(api_key=key_to_use)
model_name = 'models/gemini-2.5-flash-preview-09-2025'
model = genai.GenerativeModel(model_name)

print(f"🤖 Model: {model_name}")

# Test 1: Text Generation
print("\n--- Test 1: Simple Text Generation ---")
try:
    response = model.generate_content("Hello, reply with 'OK'.")
    print(f"✅ Text Response: {response.text.strip()}")
except Exception as e:
    print(f"❌ Text Generation FAILED: {e}")

# Test 2: File API (Small PDF)
print("\n--- Test 2: File API (Small PDF) ---")
# Create a dummy pdf or use a small existing one? 
# I'll create a dummy text file pretending to be a document for upload check, 
# but for PDF specific processing, I need a real PDF. 
# Let's try to upload the test script itself as a text file first to verify upload works.

test_file_path = "test_gemini_2_5.py" 
try:
    print(f"🚀 Uploading {test_file_path}...")
    uploaded_file = genai.upload_file(test_file_path, mime_type="text/plain")
    print(f"   Uploaded: {uploaded_file.name}")
    
    while uploaded_file.state.name == "PROCESSING":
        print(".", end="", flush=True)
        time.sleep(1)
        uploaded_file = genai.get_file(uploaded_file.name)
        
    print(f"\n   State: {uploaded_file.state.name}")
    
    if uploaded_file.state.name == "ACTIVE":
        print("🧠 Generating content from file...")
        response = model.generate_content(["Summarize this file", uploaded_file])
        print(f"✅ File Response: {response.text[:100]}...")
        
        # Cleanup
        uploaded_file.delete()
        print("🗑️ Deleted remote file")
    else:
        print(f"❌ File not active: {uploaded_file.state.name}")

except Exception as e:
    print(f"❌ File API FAILED: {e}")

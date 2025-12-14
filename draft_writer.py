import os
import sys
import argparse
import json
import urllib.request
import urllib.error
import ssl
from datetime import datetime

def load_spec(topic):
    """
    Smartly finds the relevant spec based on keywords in the topic.
    """
    spec_dir = "standards"
    specs = {
        "102": "section_102_spec.md",
        "ขยายเวลา": "section_102_spec.md",
        # Future: "97": "section_97_spec.md"
    }

    selected_spec = None
    for keyword, filename in specs.items():
        if keyword in topic:
            selected_spec = filename
            break
    
    if selected_spec:
        spec_path = os.path.join(spec_dir, selected_spec)
        if os.path.exists(spec_path):
            with open(spec_path, "r", encoding="utf-8") as f:
                return f.read()
    
    return None


def call_gemini_api(prompt, api_key):
    """
    Sends the prompt to Google Gemini API (Flash model) for fast generation.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
        context = ssl._create_unverified_context()
        with urllib.request.urlopen(req, context=context) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result['candidates'][0]['content']['parts'][0]['text']
    except urllib.error.HTTPError as e:
        print(f"❌ API Error: HTTP {e.code} {e.reason}")
        try:
             print(e.read().decode('utf-8'))
        except:
             pass
        return None
    except Exception as e:
        print(f"❌ API Error: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="AI Writer with Auto-Spec Injection")
    parser.add_argument("topic", help="The topic or title of the article you want to write")
    parser.add_argument("--auto-send", action="store_true", help="Automatically send to Gemini API")
    args = parser.parse_args()

    print(f"🤖 AI Writer System Initialized...")
    print(f"📄 Target Topic: {args.topic}")

    # 1. Auto-Detect & Load Spec
    print(f"🔍 Searching for relevant Content Specs...")
    spec_content = load_spec(args.topic)

    if spec_content:
        print(f"✅ Found applicable Spec! Injecting content rules...")
    else:
        print(f"⚠️ No specific spec found for this topic. Using general standard.")
        spec_content = "General Golden Rule: Write with precision, neutrality, and clear references."

    # 2. Construct the Strict Prompt
    final_prompt = f"""
# MASTER INSTRUCTION (NON-NEGOTIABLE)
You are an expert legal writer specializing in Thai Procurement Law.
You are tasked with writing an article on the topic: "{args.topic}"

## 🚨 CRITICAL CONTENT SPECIFICATION
You MUST strictly adhere to the following rules. Any deviation will result in rejection.

---
{spec_content}
---

## WRITING INSTRUCTION
Based on the rules above, write a comprehensive, easy-to-read article for the general public/contractors.
Ensure you use the Correct Terminology defined in the Spec.
"""

    # 3. Output or Send
    if args.auto_send:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("⚠️  GEMINI_API_KEY not found in environment.")
            api_key = input("� Please paste your Google AI Studio Key here: ").strip()
            
        if not api_key:
            print("❌ Error: No API Key provided.")
            return

        print("🚀 Sending to Gemini API (Auto-Mode)...")
        content = call_gemini_api(final_prompt, api_key)
        
        if content:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"articles/draft_{timestamp}.md"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Article Generated Successfully!")
            print(f"📂 Saved to: {filename}")
    else:
        output_filename = "ready_to_write_prompt.txt"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write(final_prompt)
        print(f"\n✨ Prompt Assembled Successfully!")
        print(f"📜 File: {output_filename}")
        print(f"� Tip: Use --auto-send to let AI write it for you immediately.")

if __name__ == "__main__":
    main()

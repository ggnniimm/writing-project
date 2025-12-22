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
    parser.add_argument("--source-file", help="Path to a source text file (e.g. extracted PDF markdown) to use as context.")
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

    # 1.5 Load Source File if provided
    source_context = ""
    if args.source_file:
        if os.path.exists(args.source_file):
            print(f"📖 Reading Source File: {args.source_file}")
            try:
                with open(args.source_file, "r", encoding="utf-8") as f:
                    source_text = f.read()
                    source_context = f"""
## SOURCE MATERIAL
The following text is the raw content extracted from a relevant document (e.g. court judgment). 
Use this material as the primary factual basis for your article. Quote specific sections if necessary.

---
{source_text[:50000]} 
---
(Truncated if too long)
"""
            except Exception as e:
                print(f"❌ Error reading source file: {e}")
        else:
            print(f"⚠️ Source file not found: {args.source_file}")

    # 2. Construct the Strict Prompt
    final_prompt = f"""
You are a legal content writer for the "Learning from Judgments" (เรียนรู้จากคำพิพากษา) series. 
Your goal is to write an educational article based on the provided court ruling source material.

## TARGET AUDIENCE
- Contractors, government officials, engineers, and legal officers involved in public procurement.
- Tone: Professional, accessible, storytelling (explaining complex legal concepts simply), and engaging. Use "ครับ" ending.

## ARTICLE FORMAT (STRICTLY FOLLOW THIS STRUCTURE)

# EP.xx [Catchy Title related to the Key Issue] (Case Number, e.g., อ. xxx/25xx)

[**Introduction/Hook**]: Start with a relatable question or scenario involved in this case. (e.g., "Have you ever encountered...?", "What happens when...")

---

## 🏗️ เรื่องราว (The Story)
[Summarize the background facts as a storytelling narrative or numbered list]
1. **The Project:** What was the contract?
2. **The Problem:** What happened? (Delay, obstruction, termination, fine?)
3. **The Action:** What did the parties do?

## 💥 จุดแตกหัก (The Conflict)
[Describe the specific dispute. Why did they go to court? What is the core argument of each side?]

## ⚖️ คำตัดสิน (The Ruling)
[Explain the court's decision and reasoning clearly. Break it down into numbered key legal principles.]
### 1. [Principle Name in Thai] (English Legal Concept)
[Explanation of the court's logic. Why did they decide this way? Use bold text for emphasis.]

### 2. ...

## 📝 บทสรุปและข้อคิด (Key Takeaways)

### สำหรับผู้รับจ้าง (For Contractors)
- [Practical advice 1]
- [Practical advice 2]

### สำหรับหน่วยงานของรัฐ (For Government Officials)
- [Practical advice 1]
- [Practical advice 2]

---
**📚 อ้างอิง:**
*   **คำพิพากษาศาลปกครองสูงสุดที่ [Case Number]**

## INPUT CONTEXT
{spec_content}
---

{source_context}

## WRITING INSTRUCTION
Based on the provided SOURCE MATERIAL, write the article following the format above.
- Extract the Red Case Number (คดีหมายเลขแดง) for the title. If the Episode Number (EP.xx) is not provided, use "EP.xx".
- Focus on the *Ratio Decidendi* (the rationale for the decision).
- Use emojis as specified in the structure.
- **Language:** Thai (Main content) with some English legal terms in brackets where appropriate.
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


import os
import sys
import json
import time
import google.generativeai as genai
from google.api_core import exceptions

def extract_and_name_with_gemini(filepath):
    # 1. Get API Key
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        env_path = os.path.join(os.path.dirname(__file__), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if line.strip().startswith("GEMINI_API_KEY="):
                        api_key = line.strip().split("=", 1)[1].strip().strip('"').strip("'")
                        break
    
    if not api_key:
        print("❌ Error: GEMINI_API_KEY not found.")
        sys.exit(1)

    genai.configure(api_key=api_key)

    if not os.path.exists(filepath):
        print(f"❌ Error: File not found: {filepath}")
        return

    print(f"🚀 Processing: {os.path.basename(filepath)}")

    # 2. Upload File (handles large files automatically)
    try:
        print("📤 Uploading file to Gemini...")
        sample_file = genai.upload_file(path=filepath, display_name=os.path.basename(filepath))
        
        # Check state
        while sample_file.state.name == "PROCESSING":
            print("⏳ Processing file on server...", end='\r')
            time.sleep(2)
            sample_file = genai.get_file(sample_file.name)
        
        if sample_file.state.name == "FAILED":
             print("\n❌ File processing failed on Gemini server.")
             return

        print(f"\n✅ Upload complete: {sample_file.uri}")

    except Exception as e:
        print(f"❌ Upload Error: {e}")
        return

    # 3. Generate Content
    # Use gemini-flash-latest (Confirmed available)
    model = genai.GenerativeModel('models/gemini-flash-latest') 

    prompt_text = """
    You are a professional document digitization assistant. 
    Task 1: Transcribe ALL text from this document VERBATIM. 
            - This is a legal document. Do NOT summarize. Do NOT omit any sections. 
            - If the document is an image/scan, perform character-by-character OCR. 
            - Preserve the original Thai language wording exactly. 
            - Convert the layout to clean Markdown (headers, lists, tables).
    Task 2: Generate a concise, descriptive English filename for this document based on its content. The filename should use snake_case and end with '.md'.
    Task 3: Analyze and Draft (Legal Expert Role).
            - **Identify Issuing Authority:** Explicitly state if this is from the "Comptroller General's Committee (กวจ.)" or "Office of the Attorney General (อสส.)" or "Administrative Court (ศาลปกครอง)".
            - Identify relevance to "Section 97" or "Section 102".
            - If relevant:
                1. **Summary:** Briefly summarize the legal principle (Thai).
                2. **Draft Content:** Write a high-quality Markdown block (Thai) ready to be pasted into the article. Use key legal terms, bullet points, and citation placeholders.
                3. **Placement:** Suggest exactly where in the article this should go (e.g., "New Case Study", "Under General Principles").
            - Append this to the generated file under a header "## 🤖 AI Draft & Analysis".
    
    Output Format: Return only a valid JSON object with the following structure:
    {
        "filename": "generated_filename.md",
        "content": "# Full Document Content...\n\n## 🤖 AI Draft & Analysis\n(Content here)"
    }
    """

    retry_delay = 5
    max_retries = 5 # Increased retries for large tasks

    for attempt in range(max_retries):
        try:
            print(f"🤖 Generating content (Attempt {attempt+1}/{max_retries})...")
            response = model.generate_content(
                [prompt_text, sample_file],
                generation_config={"response_mime_type": "application/json"}
            )
            
            # 4. Parse & Save
            try:
                result_json = json.loads(response.text)
                md_filename = result_json.get("filename", "extracted.md")
                md_content = result_json.get("content", "")

                if not md_content:
                    print("⚠️ Warning: Empty content returned.")
                    return

                # Save logic
                output_dir = os.path.dirname(filepath)
                output_path = os.path.join(output_dir, md_filename)
                
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(md_content)
                
                print(f"✅ Success! Extracted to: {output_path}")
                
                # Cleanup (Optional but good practice)
                try:
                    sample_file.delete()
                    # print("🗑️  Remote file cleaned up.")
                except:
                    pass

                return

            except json.JSONDecodeError:
                print(f"❌ JSON Error. Raw text: {response.text[:100]}...")
                # Retry if JSON is bad? Usually better to fail or try again.
            
        except exceptions.ResourceExhausted:
            print(f"⏳ Rate limit hit. Waiting {retry_delay}s...")
            time.sleep(retry_delay)
            retry_delay *= 2
        except Exception as e:
            print(f"❌ Generation Error: {e}")
            # If it's a 500 error, maybe retry.
            if "500" in str(e) or "503" in str(e):
                 time.sleep(5)
                 continue
            break

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 gemini_pdf_to_md.py <filepath>")
        sys.exit(1)
    
    extract_and_name_with_gemini(sys.argv[1])

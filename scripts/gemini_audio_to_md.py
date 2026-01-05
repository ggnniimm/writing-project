import os
import sys
import time
import google.generativeai as genai
from google.api_core import exceptions

def transcribe_audio_gemini(filepath, output_filename):
    # 1. Load API Keys
    api_keys = []
    # Check environment variables
    for key, value in os.environ.items():
        if key.startswith("GEMINI_API_KEY") and value:
            api_keys.append(value)
    
    # Check .env file
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("GEMINI_API_KEY") and "=" in line:
                    k_val = line.split("=", 1)[1].strip().strip('"').strip("'")
                    if k_val:
                        api_keys.append(k_val)
    
    api_keys = list(set(api_keys))
    if not api_keys:
        print("❌ Error: GEMINI_API_KEY not found.")
        sys.exit(1)

    print(f"🔑 Loaded {len(api_keys)} API Key(s).")
    
    # 2. Upload and Transcribe
    success = False
    final_text = ""
    
    current_key_index = 0
    
    for i in range(len(api_keys)):
        key_index = (current_key_index + i) % len(api_keys)
        api_key = api_keys[key_index]
        print(f"🔑 Using Key #{key_index + 1} (Mask: ...{api_key[-5:]})")
        
        genai.configure(api_key=api_key)
        
        try:
            # Upload
            print(f"🚀 Uploading {filepath}...")
            # Detect mime type roughly
            mime_type = "audio/mpeg" # Default for MP3
            
            uploaded_file = genai.upload_file(filepath, mime_type=mime_type)
            print(f"   Uploaded: {uploaded_file.display_name}")
            
            # Wait for processing
            while uploaded_file.state.name == "PROCESSING":
                print("   ⏳ Processing...", end="\r")
                time.sleep(2)
                uploaded_file = genai.get_file(uploaded_file.name)
            
            if uploaded_file.state.name == "FAILED":
                raise Exception("File processing failed.")
                
            print("   ✅ File Ready.")
            
            # Generate
            print("🧠 Transcribing...")
            model = genai.GenerativeModel('models/gemini-2.5-flash') # Using 2.5 as found in model list
            
            prompt = """
            Transcribe this audio file into text.
            Language: Thai (primary) and English (technical terms).
            Format: Markdown.
            
            Rules:
            1. Transcribe verbatim.
            2. Identify speakers if possible (Speaker A, Speaker B, etc.).
            3. Use bullet points or paragraphs for readability.
            4. If there are technical legal concepts regarding construction contracts, ensure accuracy.
            """
            
            response = model.generate_content([prompt, uploaded_file], stream=True)
            
            for chunk in response:
                if chunk.text:
                    final_text += chunk.text
                    print(".", end="", flush=True)
            
            # Cleanup
            try:
                uploaded_file.delete()
            except:
                pass
                
            success = True
            break
            
        except Exception as e:
            print(f"\n❌ Error with Key #{key_index + 1}: {e}")
            if "429" in str(e) or "ResourceExhausted" in str(e):
                time.sleep(5)
                continue
            else:
                 time.sleep(5)
                 continue

    if not success:
        print("\n❌ Failed to transcribe.")
        sys.exit(1)
        
    # Save
    if final_text:
        # Determine output path
        # If output_filename is just a name, put it in references/audio_transcripts/
        # If it has no extension, add .md
        
        if not output_filename.endswith(".md"):
            output_filename += ".md"
            
        # Target directory: references/audio_transcripts
        target_dir = "references/audio_transcripts"
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        final_path = os.path.join(target_dir, output_filename)
        
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(final_text)
            
        print(f"\n✅ Saved transcript to: {final_path}")
        
if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 gemini_audio_to_md.py <input_audio_path> <output_name>")
        sys.exit(1)
        
    transcribe_audio_gemini(sys.argv[1], sys.argv[2])

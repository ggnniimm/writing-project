#!/usr/bin/env python3
"""
Robust extraction script for Volume 11 with auto-retry for 429 errors.
"""

import os
import sys
import time
import subprocess
import glob

def get_missing_parts():
    parts_dir = "etc/Academic_291121_112321_parts"
    all_pdfs = sorted(glob.glob(os.path.join(parts_dir, "Academic_291121_112321_part_*.pdf")))
    missing = []
    
    for pdf in all_pdfs:
        basename = os.path.basename(pdf)
        part_name = basename.replace('.pdf', '')
        md_file = os.path.join(parts_dir, f"{part_name}.md")
        
        if not os.path.exists(md_file) or os.path.getsize(md_file) == 0:
            missing.append((pdf, md_file))
            
    return missing

def extract_with_retry(pdf, md):
    max_retries = 100 # Effectively infinite
    
    for attempt in range(max_retries):
        print(f"🔄 Extracting {os.path.basename(pdf)} (Attempt {attempt+1})...")
        
        try:
            # Run the extraction script
            result = subprocess.run(
                ["python3", "extract_pdf_simple.py", pdf, md],
                capture_output=True,
                text=True
            )
            
            # Combine output to check for errors
            combined_output = result.stdout + result.stderr
            
            if result.returncode == 0 and os.path.exists(md) and os.path.getsize(md) > 0:
                print(f"✅ Success: {os.path.basename(md)}")
                return True
            else:
                # Check for rate limit in output
                if "429" in combined_output or "Quota exceeded" in combined_output:
                    print("⚠️  Rate Limit (429) hit.")
                    print("⏳ Waiting 70 seconds...")
                    time.sleep(70)
                    continue
                else:
                    print(f"❌ Error: {combined_output}")
                    # If it's not a rate limit, maybe waiting won't help, but for now we assume transient
                    # But if it's a persistent error, we might want to skip or stop.
                    # For safety, let's wait a bit and retry, or stop.
                    # Let's wait 30s.
                    time.sleep(30)
                    
        except Exception as e:
            print(f"❌ Exception: {e}")
            time.sleep(30)
            
    return False

def main():
    print("🚀 Starting Robust Extraction for Volume 11")
    
    missing_parts = get_missing_parts()
    print(f"📋 Found {len(missing_parts)} missing parts.")
    
    for pdf, md in missing_parts:
        success = extract_with_retry(pdf, md)
        if not success:
            print(f"🛑 Failed to extract {os.path.basename(pdf)} after multiple attempts.")
            # Decide whether to continue or stop. Let's continue to try others? 
            # No, if one fails hard, others likely will too or we need to fix the script.
            # But if it's just one bad file, we might want to skip.
            # For now, let's stop to avoid wasting quota on broken process.
            sys.exit(1)
            
        # Optional small delay between successes to be nice to API
        time.sleep(5)
        
    print("\n✨ All missing parts extracted!")

if __name__ == "__main__":
    main()

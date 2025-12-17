
import sys
import os

# Mock google.generativeai to avoid import errors if credentials are missing during this test
# (We only need determine_filename_and_path which is pure logic)
from unittest.mock import MagicMock
sys.modules["google.generativeai"] = MagicMock()
sys.modules["google.api_core"] = MagicMock()
sys.modules["google.api_core.exceptions"] = MagicMock()

# Now import the module
import gemini_pdf_to_md

def test_naming():
    test_cases = [
        (
            "คดีหมายเลขแดงที่ อ. 104/2563", 
            "ref_sac_o_104_2563.md"
        ),
        (
            "คดีหมายเลขแดงที่ ๑.๑๐๔/๒๕๖๓", # Thai digits + dot
            "ref_sac_o_104_2563.md" # Logic removes dot in number if starts with 1. and no prefix? 
                                    # Wait, logic says: if no prefix and starts with 1., treat 1. as prefix O.
                                    # Here regex match for prefix might be empty if it doesn't match 'อ.' exactly.
                                    # Let's see how regex `(อ\.|อ)` works.
                                    # Thai '๑' is not 'อ'. So prefix group is empty.
                                    # Number match `[\d.,]+` captures `๑.๑๐๔`.
                                    # normalize converts to `1.104`.
                                    # `number_raw` = `1.104`.
                                    # Logic: `if not prefix_str and number_raw.startswith("1."): prefix_str="o_"; number_raw=number_raw[2:]`
                                    # So `104`.
                                    # Result: `ref_sac_o_104_2563.md`
        ),
        (
            "คดีหมายเลขแดงที่ อ. 16/2547",
            "ref_sac_o_16_2547.md"
        ),
        (
            "คดีหมายเลขแดงที่ 1.16/2557",
            "ref_sac_o_16_2557.md"
        ),
        (
            "คดีหมายเลขแดงที่ 123/2566", # No prefix, normal number
            "ref_sac_123_2566.md"
        )
    ]

    print("Running Tests...\n")
    failed = False
    for content, expected in test_cases:
        # We need enough text to cover "ศาลปกครอง" trigger if needed?
        # The function checks `if "ศาลปกครอง" in content_sample`.
        # So we must prepend that.
        full_content = "ศาลปกครองสูงสุด\n" + content
        
        result, _ = gemini_pdf_to_md.determine_filename_and_path(full_content)
        
        if result == expected:
            print(f"✅ PASS: {content} -> {result}")
        else:
            print(f"❌ FAIL: {content}\n   Expected: {expected}\n   Got:      {result}")
            failed = True
            
    if failed:
        sys.exit(1)
    else:
        print("\nAll tests passed.")

if __name__ == "__main__":
    test_naming()

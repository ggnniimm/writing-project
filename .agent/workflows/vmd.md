---
description: Verify the accuracy and completeness of an extracted Markdown file against its source PDF.
---

1. Run the verification script
   
   ```bash
   python3 scripts/verify_md_content.py "$1" "$2"
   ```

2. **Verify against PDF Source**:
   If the verification script reports issues (e.g., Arabic numerals in Thai text) or if there are any doubts, YOU MUST verify the content against the original PDF.

   Use `pdftotext` to extract the relevant section or the whole file to check the actual characters used in the source.

   ```bash
   pdftotext -layout "$2" - | grep -C 3 "context string"
   ```

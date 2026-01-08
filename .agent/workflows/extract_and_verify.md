---
description: How to extract and verify court rulings with strict footnote checks
---
1.  **Extract Content:**
    Run the extraction script on your PDF. This script now includes strict rules for footnote formatting (superscripts).
    ```bash
    python3 scripts/gemini_pdf_to_md.py <path_to_pdf> <output_md_path>
    ```

2.  **Verify Extraction:**
    Run the verification script. This now checks for:
    *   **Numerals:** Ensures no Arabic numerals in Thai text.
    *   **Footnotes:** Checks sequence (1, 2, 3...) and ensures every reference (`<sup>1</sup>`) has a matching definition.
    *   **Content Fidelity:** Checks length ratio and content overlap with PDF.
    ```bash
    python3 scripts/verify_md_content.py <output_md_path> <path_to_pdf>
    ```

3.  **Review Output:**
    *   If `Footnote Validation Issues` are reported (e.g., "GAP in Footnote References", "Definitions without References"), inspect the Markdown file.
    *   Use `multi_replace_file_content` to fix any missing superscripts or definitions.

// turbo
4.  **Auto-Fix (Optional Check):**
    If verification passes but you suspect issues, you can run a targeted grep to see all footnotes:
    ```bash
    grep -E "<sup>|</sup>" <output_md_path>
    ```

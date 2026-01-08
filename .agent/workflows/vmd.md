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

   In your final report, YOU MUST include the **Character Count** for both the PDF and Markdown files, and the **Ratio**, as outputted by the verification script.

4. **Verify Footnotes & Superscripts**:
   If the document contains footnotes, perform the following strict checks:

   **A. Check Superscript Formatting**
   Run the following command to see all superscripts and isolated numbers (potential footnote labels):
   ```bash
   grep -n -E "<sup>|^\s*[๑-๙๐-๙]+(-[๑-๙๐-๙]+)?\s*$" "$1"
   ```
   - Ensure all superscript numbers in the text are wrapped in `<sup>...</sup>` tags.
   - Ensure the sequence of superscripts is continuous (e.g., 1, 2, 3...) without gaps unless justified.

   **B. Verify Footnote Labels**
   - Check the bottom of pages/sections for the corresponding footnote definitions.
   - Verify that labels are clean and accurate (e.g., `๑` not `*` or `\๑`).
   - Watch out for OCR errors in labels (e.g., `٩` instead of `๔-๖`). as seen in Vol 7.

   **C. One-to-One Mapping**
   - **CRITICALLY**: Every superscript in the text MUST have a corresponding footnote definition at the bottom of the relevant page/section.
   - Conversely, every footnote definition must correspond to a superscript in the text.

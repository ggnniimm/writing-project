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
   If the document contains footnotes, perform the following strict checks (See `README.md` Sec 3):

   **A. Check Superscript Formatting (In-Text)**
   Run the following command to see all superscripts and isolated numbers:
   ```bash
   grep -n -E "<sup>|^\s*[๑-๙๐-๙]+(-[๑-๙๐-๙]+)?\s*$" "$1"
   ```
   - All citations must be `<sup>๑</sup>`.
   - No spaces before the `<sup>` tag.

   **B. Verify Footnote Definitions (Bottom)**
   - Definitions must also start with `<sup>`.
   - Format: `<sup>๑</sup> คำอธิบาย` (Note the space after tag).
   - Check the bottom of pages/sections.
   - Example command to check definitions:
     ```bash
     grep -n "^<sup>" "$1"
     ```

   **C. One-to-One Mapping**
   - **CRITICALLY**: Every superscript in the text MUST have a corresponding footnote definition at the bottom.
   - Conversely, every footnote definition must correspond to a superscript in the text.

---

## ⚠️ Lessons Learned

### Arabic Numeral Verification (CRITICAL)
When the verification script flags Arabic numerals in Thai text:
1. **DO NOT assume** Arabic `5` → Thai `๕`. OCR may have misread the digit entirely.
2. **ALWAYS verify against PDF source first** using `pdftotext` before making any changes.
3. Example: Arabic `5` was found in MD, but PDF source showed `๖` — the OCR misread the digit shape, not just the script.

```bash
# Verify specific numeral context in PDF
pdftotext -layout "$2" - | grep -C 2 "มาตรา"
```

### Missing Page Detection (CRITICAL)
When Ratio is below 0.95 (e.g., 0.93), **suspect missing pages**:

1. **Check page headers are sequential**:
   ```bash
   grep -n "แนวคำวินิจฉัยของศาลปกครอง ๗" "$1"
   ```
   - Headers should follow odd-number sequence: ๗๑, ๗๓, ๗๕, ๗๗, ๗๙
   - Missing header = missing page content

2. **Calculate expected deficit**:
   - ~2,000 chars/page typical
   - Deficit of 3,000 chars ≈ 1.5 pages missing

3. **Extract and insert missing content from PDF**:
   ```bash
   pdftotext -layout -f PAGE_NUM -l PAGE_NUM "$2" -
   ```


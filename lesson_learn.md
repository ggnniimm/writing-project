### 🧠 บทเรียนและแนวทางป้องกัน (Lesson Learned)
**Date:** 2026-01-16
**Incident:** Inserted duplicate content (Pages 453-468) into `part_25.md`.
**Root Cause:**
1.  **PDF Overlap Blind Spot:** `part_25.pdf` contained pages 452-469, but `part_25.md` was intended to start at 469. I assumed the PDF extraction was the 1:1 target for the MD file.
2.  **Isolated Verification:** I verified `part_25.md` in isolation without checking the end of `part_24.md`. If I had checked `part_24.md`, I would have seen Page 468 there.
**Prevention Plan:**
1.  **Neighbor Check:** Before adding "missing" pages to the start of a file, ALWAYS check the *end* of the *previous* file (`part_N-1.md`).
2.  **Overlap Awareness:** Recognize that split PDFs often contain overlapping pages (context) from previous sections. Do not assume all PDF content belongs in the current MD file.
3.  **Strict Continuity Rule:** If `Start_Page(Current_MD) > Start_Page(Source_PDF)`, verification is PASSED if `End_Page(Prev_MD) == Start_Page(Current_MD) - 1`.

### 🧠 บทเรียนและแนวทางป้องกัน (Lesson Learned)
**Date:** 2026-01-16
**Incident:** Verification script failed to detect unformatted Footnote 68 in `part_29.md`.
**Observation:**
- Footnote 68 appeared as a stray line containing only `๖๘` (Lines 603, 606) instead of `<sup>๖๘</sup>`.
- The `verify_md_content.py` script relies on finding `<sup>` tags to identify footnotes. Since these tags were missing, the script assumed the footnote sequence ended at 67.
**Root Cause:**
1.  **Tag-Dependency:** Verification logic is too dependent on correct formatting (`<sup>`). It blindly trusts that if a tag isn't there, it's not a footnote.
2.  **No "Stray Number" Check:** There was no check for isolated Thai numerals (OCR artifacts) that often represent malformed headers or footnotes.
**Prevention Plan:**
1.  **Enhance Verification Script:** Update `verify_md_content.py` to scan for "Suspicious Stray Numbers" (Thai numerals 1-3 digits appearing on their own line or isolated).
2.  **Regex Strategy:** Implement a check like `^[ \t]*[๐-๙]{1,3}[ \t]*$` to flag lines that are likely unformatted footnote numbers.

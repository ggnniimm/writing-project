---
description: Search, Extract, and Write (SEW) workflow for Thai Administrative Court Judgments.
---

This workflow allows you to go from a Case Number to a Draft Article in one go.

**Usage:** "Run sew for Case Red No. 506/2562"

## Workflow Steps

1.  **Search & Download**
    - **Parsing:**
        - If command is `sew อ. <num>/<year>` (e.g. `sew อ. 111/2555`): Target is **Judgment** (คำพิพากษา) for Case "อ. <num>/<year>".
        - If command is `sew c <num>/<year>` (e.g. `sew c 111/2555`): Target is **Order** (คำสั่ง) for Case "<num>/<year>".
    - **Search:**
        - Navigate to `https://www.admincourt.go.th/admincourt/site/05SearchSuit.html`.
        - **CRITICAL INPUT RULE:** Extract **ONLY** the numbers.
            - Input `<num>` into the first Red Number box (input[7]).
            - Input `<year>` into the second Red Number box (input[8]).
            - **NEVER** type "อ." or "c" into the search box.
            - **ALWAYS** clear Black Number boxes (input[5], input[6]) using JS.
    - **Download:**
        - **CRITICAL FILTER:** Look for the row where "Court Name" (or similar column) indicates **"Supreme Administrative Court"** (ศาลปกครองสูงสุด). Ignore lower courts (e.g., Nakhon Si Thammarat, Chiang Mai) unless explicitly requested.
        - If Target is **Judgment**: Click the link in the "คำพิพากษา" column for the Supreme Court row.
        - If Target is **Order**: 
            - Look for the link in the "คำสั่ง" column for the Supreme Court row.
            - **CRITICAL VERIFICATION:** Ensure the text says "คำสั่งที่ <num>/<year>" with **NO alphabetic prefix** (e.g. "180/2563", NOT "ค. 180/2563").
    - Download the file to `raw_pdfs/`. Name it meaningfully (e.g. `raw_pdfs/sac_judge_111_2555.pdf` or `raw_pdfs/sac_order_111_2555.pdf`).

2.  **Extract Content**
    - Run the extractor script:
    ```bash
    ./eee raw_pdfs/<downloaded_filename>.pdf
    ```
    - Capture the output path of the generated Markdown file (usually in `references/rulings_court/`).

3.  **Rename Extracted Files (Naming Convention)**
    - **For Orders (คำสั่ง):**
        - Rename markdown: `ref_sac_cmd_<num>_<year>.md` (e.g., `ref_sac_cmd_180_2563.md`)
        - Rename PDF: `ref_sac_cmd_<num>_<year>.pdf`
    - **For Judgments (คำพิพากษา):**
        - Keep pattern: `ref_sac_o_<num>_<year>.md` and PDF.

4.  **Write Draft**
    - Run the draft writer with the source file:
    ```bash
    // turbo
    python3 draft_writer.py "Summary of Case <Case Number>" --source-file <path_to_markdown_from_step_2> --auto-send
    ```

5.  **Finalize & Organize**
    - Check `articles/learning_from_judgments/` for the last "epXX" number.
    - Rename the generated draft to `ep<Next>_<topic>_<case_no>.md` (e.g., `ep48_suing_wrong_party_o_180_2563.md`).
    - Move it to `articles/learning_from_judgments/`.

## Example
1. **Judgment Flow:**
   - User: "sew อ. 111/2555"
   - Agent: Opens browser -> JS injects Red No: "111", Year: "2555" (Clears others) -> Clicks Search.
   - Agent: Finds row. Checks "คำพิพากษา" column. Downloads file `raw_pdfs/sac_judge_111_2555.pdf`.
   - Agent: `./eee ...` -> `draft_writer.py ...`

2. **Order Flow:**
   - User: "sew c 111/2555"
   - Agent: Opens browser -> JS injects Red No: "111", Year: "2555" (Clears others) -> Clicks Search.
   - Agent: Finds row. Checks "คำสั่ง" column. Downloads file `raw_pdfs/sac_order_111_2555.pdf`.
   - Agent: `./eee ...` -> `draft_writer.py ...`

---
description: Search, Extract, and Write (SEW) workflow for Thai Administrative Court Judgments.
---

This workflow allows you to go from a Case Number to a Draft Article in one go.

**Usage:** "Run sew for Case Red No. 506/2562"

## Workflow Steps

1.  **Search & Download**
    - Use the `browser_subagent` to search for the case on `https://www.admincourt.go.th/admincourt/site/05SearchSuit.html`.
    - **Crucial:** You must specify "Red Case" (ศาลปกครอง) or "Black Case" depending on the input.
    - Download the file to `raw_pdfs/`. name it meaningfully (e.g. `raw_pdfs/sac_red_506_2562.pdf`).

2.  **Extract Content**
    - Run the extractor script:
    ```bash
    ./eee raw_pdfs/<downloaded_filename>.pdf
    ```
    - Capture the output path of the generated Markdown file (usually in `references/rulings_court/`).

3.  **Write Draft**
    - Run the draft writer with the source file:
    ```bash
    // turbo
    python3 draft_writer.py "Summary of Case <Case Number>" --source-file <path_to_markdown_from_step_2> --auto-send
    ```

## Example
1. User says "sew Case 506/2562".
2. Agent searches browser -> finds PDF URL.
3. Agent: `curl -o raw_pdfs/case_506_2562.pdf <url>`
4. Agent: `./eee raw_pdfs/case_506_2562.pdf` -> outputs `references/rulings_court/ref_sac_o_506_2562.md`
5. Agent: `python3 draft_writer.py "Summary of Red Case 506/2562" --source-file references/rulings_court/ref_sac_o_506_2562.md --auto-send`

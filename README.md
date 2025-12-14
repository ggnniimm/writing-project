# 📚 Writing Project: Procurement Law

## 🤖 AI Agent Guidelines (Important!)
If you are an AI assistant opening this project for the first time, please follow these rules:

### 1. 📝 Diary Format (Hybrid Narrative)
We use a specific format for `git_diary.md`.
- **Header:** `## 📅 YYYY-MM-DD` followed by a **summary** of the day.
- **Log:** Use `### 📝 บันทึกการปฏิบัติงาน (Operations Log)` for detailed entries.
- **Style:** "Captain's Log" - Tell a story about what you are **Doing**, what you are **Thinking**, or what you were **Ordered** to do. Focus on the *why* and *how*.
- **Automation:** Use `ppp` (push-work) to generate entries. **Do not manually edit the diary unless necessary.**
- **Naming Convention:**
    - Always use **"คำวินิจฉัย อสส. ที่ [เลขที่]/[ปี]"** when referring to Office of the Attorney General rulings. (e.g., *คำวินิจฉัย อสส. ที่ 133/2561*)
    - **Strict Thai Policy:** All diary entries, commit messages, and contexts MUST be written in **Thai (ภาษาไทย)**. English is allowed only for technical terms or code references.
    - **Daily Retrospective:** DO NOT fill in the summary section (Accomplished, Pending, etc.) manually during the day. This section is reserved for the end-of-day process triggered by `nnn`. Leave it empty or `(รอสรุป...)`.

### 2. ⚡ Workflow Commands
The user interacts with this repo primarily through **custom scripts**.
*   **`./push-work` (Alias: `ppp`):** The main command.
    *   **Usage:** `./push-work "Message" "Context (Why & How)"`
    *   Stages all files.
    *   Analyzes changes using `update_diary.py`.
    *   **Context is MANDATORY:** If running manually, always provide the 2nd argument. If running interactively, fill in the prompt.
    *   Updates `git_diary.md` automatically.
    *   Commits and Pushes to GitHub.

*   **`./eee` (Extract & Auto-Integrate):**
    *   **Usage:** `./eee references/raw_pdfs/filename.pdf`
    *   **Workflow:** 
        1.  Extracts text and saves to `references/`.
        2.  **Auto-Analysis:** AI Drafts a summary and content block.
        3.  **Auto-Integration (Agent Rule):** The Agent MUST immediately review the "Draft Content" and insert it into the relevant Article (e.g., Section 97/102) *without* waiting for user confirmation.
    *   Then, sync work with `ppp`.

*   **`./bbb` (Begin Day):**
    *   **Usage:** `./bbb`
    *   **Purpose:** Start of day routine.
    *   Pulls latest code (`git pull`).
    *   Displays project guidelines.
    *   **Initializes Diary:** Creates a new daily entry with *only* "Pending / Planned" items.
    *   Shows the latest diary summary.

*   **`./nnn` (End Day):**
    *   **Usage:** `./nnn`
    *   **Purpose:** End of day routine.
    *   **Auto-Summary:** automatically generates "Accomplished" list from the day's operations logs.
    *   Updates the diary summary (no survey).
    *   Auto-pushes work.

---

## 💻 Setup for New Machine (Human Only)
To set up this workflow on a new macOS machine:

1.  **Clone the Repo:**
    ```bash
    git clone https://github.com/ggnniimm/writing-project.git
    cd writing-project
    ```

2.  **Enable Scripts:**
    ```bash
    chmod +x push-work
    ```

3.  **Create Alias (`ppp`):**
    Add this to your `~/.zshrc` or run it in current session:
    ```bash
    alias ppp="./push-work"
    ```
    *Now you can just type `ppp` to sync your work!*

4.  **Dependencies:**
    Ensure you have Python 3 installed for the analysis script:
    ```bash
    python3 --version
    ```

## 📂 File Structure
*   `articles/`: Content files (Markdown).
*   `references/`: PDFs and source materials.
*   `git_diary.md`: The main work log (Hybrid Narrative).
*   `update_diary.py`: The brain behind the auto-diary.
### 3. 📂 Reference Protocol
*   **Rule:** Every time a new document, file, or image is provided for content analysis, a corresponding Markdown file must be created in the `references/` directory.
*   **Content:** The file should contain the original content (transcribed or excerpted) without modification, followed by any analysis if applicable.
*   **Naming:** Use descriptive names, e.g., `ref_[source]_[number]_[year].md`.

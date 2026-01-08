---
description: Extract court ruling books (แนวคำวินิจฉัยศาลปกครอง) from PDF to Markdown
---

# Court Ruling Book Extraction Workflow

This workflow extracts large court ruling book PDFs (500-1000+ pages) into clean, verified Markdown files.

**Volumes Completed:** 10, 11, 12, 13, 14

---

## Prerequisites

### Required Tools
- `pypdf` - PDF splitting
- `pdfplumber` - PDF text verification
- `google-generativeai` - Gemini API for OCR
- `pdftotext` - Backup text extraction (via poppler)

### API Keys
Add multiple Gemini API keys to `.env` for rate limit handling:
```
GEMINI_API_KEY_1=your_key_1
GEMINI_API_KEY_2=your_key_2
GEMINI_API_KEY_3=your_key_3
```

---

## Workflow Steps

### 1. Prepare PDF

// turbo
```bash
# Create output directory
mkdir -p etc/<source_pdf_name>_parts/

# Split PDF into ~20 pages each
python3 split_pdf.py raw_pdfs/<source_pdf>.pdf etc/<source_pdf_name>_parts/
```

**Output:** `<source_pdf>_part_01.pdf`, `<source_pdf>_part_02.pdf`, ...

---

### 2. Extract Content (Gemini API)

**Option A: Use extraction script (recommended)**
```bash
# Edit extract_vol10.py - update these lines:
# input_dir = "etc/<source_pdf>_parts"

python3 extract_vol10.py
```

**Features:**
- Automatic API key rotation on rate limit (429)
- Infinite retry until success
- Skips already-extracted parts (resume support)

**Option B: Manual extraction per part**
```bash
./eee etc/<source_pdf>_parts/<part>.pdf
```

---

### 3. Verify & Clean

#### 3.1 Verify Content Completeness
```bash
# Edit verify_vol10.py - update parts_dir, total_parts

python3 verify_vol10.py
```

**Checks:**
- All parts present
- Content end matches PDF end

#### 3.2 Clean Footers
```bash
# Remove administrative footers
sed -i '' '/สายด่วนศาลปกครอง.*๑๓๕๕/d' etc/<parts>/*.md
sed -i '' '/ข้อมูลฉับไว.*ใส่ใจประชาชน/d' etc/<parts>/*.md
sed -i '' '/^TRUST$/d' etc/<parts>/*.md
```

#### 3.3 Fix OCR Errors (PDF-Verified)
```bash
# Check for ASCII digits (should be Thai)
grep -c "[0-9]" etc/<parts>/*.md | grep -v ":0$"

# Compare against PDF source
pdftotext -layout etc/<parts>/<part>.pdf - | grep "<context>"

# Fix based on PDF verification
# Common: 5→๖, 4→๔, dimension fixes like ๒๖๕๔๐→๒๖ x ๔๐

#### 3.4 Verify Footnotes & Superscripts
```bash
# Check superscripts vs footnote labels
grep -n -E "<sup>|^\s*[๑-๙๐-๙]+(-[๑-๙๐-๙]+)?\s*$" etc/<parts>/*.md
```

**Verification Rules:**
- **Superscript Formatting:** Ensure referenced numbers in text are wrapped in `<sup>` (e.g., `ข้อ ๑๐<sup>๔</sup>`).
- **Label Accuracy:** Check bottom-of-page footnote labels for OCR errors (e.g., `*` or `٩` instead of `๔-๖`).
- **One-to-One Mapping:** Every superscript must have a corresponding footnote definition.
- **Content Integrity:** Verify footnote text matches PDF (watch for OCR errors in section numbers, e.g., `๔๒๑` vs `๘๒๑`).
```

---

### 4. Combine Parts

```bash
# Combine all parts into single file
cat etc/<source_pdf>_parts/<source_pdf>_part_{01..XX}.md > administrative_court_rulings_vol_<N>.md

# Move to final location
mv administrative_court_rulings_vol_<N>.md references/court_rulings_books/
```

---

### 5. Final Verification

```bash
# Check file size and line count
wc -l references/court_rulings_books/administrative_court_rulings_vol_<N>.md
ls -lh references/court_rulings_books/administrative_court_rulings_vol_<N>.md

# Verify no ASCII digits remain
grep -c "[0-9]" references/court_rulings_books/administrative_court_rulings_vol_<N>.md
# Should be 0

# Verify no footers remain
grep -c "สายด่วนศาลปกครอง\|TRUST" references/court_rulings_books/administrative_court_rulings_vol_<N>.md
# Should be 0
```

---

## Key Scripts Reference

| Script | Purpose |
|--------|---------|
| `split_pdf.py` | Split large PDF into 20-page parts |
| `extract_vol10.py` | Extract with API key rotation |
| `verify_vol10.py` | Verify content completeness |
| `combine_vol10.py` | Combine parts into single file |

---

## Common Issues & Solutions

### Rate Limit (429 Error)
- Script auto-rotates to next API key
- After all keys exhausted, waits 60s and retries
- Add more keys to `.env` for faster processing

### Missing Content
- Re-run extraction for affected part
- Check page count: `pdfinfo <part>.pdf`
- Verify with: `pdftotext -layout <part>.pdf -`

### OCR Errors (Thai Numerals)
- Always verify against PDF source before correcting
- Common confusions: ๖↔5, ๘↔8, ๔↔4
- Dimensions often merge: "๒๖ x ๔๐" → "๒๖๕๔๐"

### Encoding Issues
- Use `fix_thai.py` for tone mark fixes
- Check for broken Thai: `grep "[ก-๙]\s[ก-๙]" <file>.md`

---

## Example: Volume 10 Summary

| Metric | Value |
|--------|-------|
| Source PDF | Academic_281020_102051.pdf |
| Total Pages | 978 |
| Parts | 49 |
| OCR Fixes | 151 (9 dimensions + 142 numerals) |
| Footers Removed | 3 types across all parts |
| Final Size | 5.6M (32,381 lines) |

---

## Checklist Template

```markdown
## Volume <N> Extraction

- [ ] Split PDF into parts
- [ ] Extract all parts (Gemini API)
- [ ] Verify content completeness  
- [ ] Clean administrative footers
- [ ] Fix OCR errors (PDF-verified)
- [ ] Verify Footnotes (Superscripts, Labels, Mappings)
- [ ] Combine into single file
- [ ] Final verification
- [ ] Move to references/court_rulings_books/
- [ ] Update git_diary.md
- [ ] Git push
```

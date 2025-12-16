# 📄 Best Practice: PDF Extraction using Gemini File API

**Date:** 2025-12-16
**Status:** ✅ Proven & implemented in `gemini_pdf_to_md.py`

## 1. 🌟 The Concept: Why File API?

We moved from a "Page Splitting" (Chunking) strategy to using **Google Gemini's File API**.

| Feature | ❌ Old Strategy (Chunking) | ✅ New Strategy (File API) |
| :--- | :--- | :--- |
| **Integrity** | Breaks document context. AI doesn't see page 1 and 10 together. | **Full Context.** AI "reads" the whole book at once. |
| **File Size** | Limited by Base64 payload (approx < 20MB safe limit). | Supports up to **2GB** per file. |
| **Complexity** | High. Requires `pypdf`, split logic, re-combining text. | **Low.** Just Upload -> Wait -> Generate. |
| **Rate Limit** | High risk. Many API calls (1 per chunk). | **Low risk.** 1 API call per document. |

## 2. 🔑 Key Component: The "Wait Loop"

The most critical part of this implementation is the **Active Waiting** phase. You cannot generate content immediately after upload; you must wait for Google's server to process the file.

```python
# Vital: Wait for processing
while uploaded_file.state.name == "PROCESSING":
    print("⏳ Processing...", end="\r")
    time.sleep(2)
    uploaded_file = genai.get_file(uploaded_file.name)

if uploaded_file.state.name == "FAILED":
    raise Exception("Processing failed")
```

## 3. 🧠 Recommended Model

*   **Model:** `gemini-2.5-flash`
*   **Why:** It is currently the most stable and cost-effective model for high-volume OCR.
*   *Note:* `gemini-1.5-flash` was deprecated/not found in the specific API version used (v1beta), causing 404 errors. Always check `list_models()` if 404 occurs.

## 4. 📝 The "Golden Code" (Core Implementation)

This is the snippet you should use for future projects.

```python
import google.generativeai as genai
import time

def extract_pdf_with_file_api(filepath, api_key):
    genai.configure(api_key=api_key)

    # 1. Upload
    print(f"🚀 Uploading {filepath}...")
    uploaded_file = genai.upload_file(filepath, mime_type="application/pdf")
    
    # 2. Add Wait Loop (CRITICAL!)
    while uploaded_file.state.name == "PROCESSING":
        time.sleep(2)
        uploaded_file = genai.get_file(uploaded_file.name)
        
    if uploaded_file.state.name != "ACTIVE":
        raise Exception(f"File processing failed: {uploaded_file.state.name}")
        
    # 3. Generate
    model = genai.GenerativeModel('models/gemini-2.5-flash')
    response = model.generate_content(
        ["Extract verbatim text...", uploaded_file],
        stream=True
    )
    
    # 4. Collect Stream
    full_text = ""
    for chunk in response:
        full_text += chunk.text
        
    # 5. Cleanup (Save storage cost)
    uploaded_file.delete()
    
    return full_text
```

## 5. 📂 Backup Location
The full working script snapshot has been saved to:
`backups/scripts/gemini_pdf_to_md_20251216_file_api.py`

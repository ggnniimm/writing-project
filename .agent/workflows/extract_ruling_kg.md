---
description: Extract ruling content and link to Knowledge Graph
---

1. Put the ruling PDF in `raw_pdfs/`.
2. Extract text with **exact line-by-line fidelity** to the original PDF:
   - Preserve all original line breaks.
   - Maintain indentation and structural hierarchy.
   - Include catchwords or page markers exactly as they appear.
   - This standard is essential for precise citation (page, paragraph, line).
3. Identify:
   - Case ID (e.g., อ. 456/2567).
   - Laws/Sections cited.
   - Related court rulings.
   - Core legal principles established.
4. Update the Knowledge Graph:
   - Run `python scripts/light_rag_indexer.py <path_to_markdown>` to add nodes, edges, and embeddings.
5. Save the Markdown to `references/rulings_court/`.
6. Summarize briefly in the Knowledge Graph metadata.

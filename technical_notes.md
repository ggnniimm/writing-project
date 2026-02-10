# Technical Notes & Engineering Roadmap

This file tracks technical ideas, architectural designs, and future scaling strategies for the writing project.

## 🚀 Idea: ADE Format for Vector DB (RAG)
**Date:** 2026-02-10
**Context:** Leveraging the high-quality ADE extraction for an AI-powered search/Q&A system.

### 1. Metadata Mapping (from YAML)
- Extract fields from YAML frontmatter (`type`, `ref_number`, `date`) into Vector DB metadata.
- Enables **Hybrid Search**: Filter by year/type before performing semantic search.

### 2. Hierarchical Chunking
- Use the Markdown Headers (`##`, `###`) as natural split points for text chunking.
- Ensures each chunk maintains a focused context (e.g., "Facts Only" vs "Legal Opinion").

### 3. Footnote & Citation Inlining
- **Challenge:** Standard chunking loses the meaning of `<sup>[1]</sup>` if the reference section is in a different chunk.
- **Solution:** During ingestion, replace `<sup>[n]</sup>` tags with inline references (e.g., `(Ref: กวจ. 2223/2568)`) to make each chunk self-contained.

### 4. Thai Tokenization
- The standardized Thai spacing in ADE format improves the accuracy of tokenizers (like OpenAI/Gemini or PyThaiNLP), reducing "broken word" issues in the vector space.

---

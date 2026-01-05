---
description: Query the system using LightRAG (Vector + Graph)
---

1. Run the query script:
```bash
python scripts/light_rag_query.py "Your Question Here"
```

The system will:
1.  **Embed** your query to find relevant nodes (Local Search).
2.  **Traverse** the Knowledge Graph to find related context (Global Search).
3.  **Synthesize** an answer using Gemini based on the combined context.

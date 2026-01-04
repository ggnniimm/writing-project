---
description: Query the system using GraphRAG (Context + Traversal)
---

1. Search for relevant rulings using semantic search (Vector RAG).
2. For each relevant ruling, traverse the Knowledge Graph:
   - Find cited cases (CITES).
   - Find related laws (APPLIES).
   - Find established principles (ESTABLISHES).
3. Combine all retrieved content as context.
4. Synthesize the answer based on the augmented context.

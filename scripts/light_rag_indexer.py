import os
import sys
import json
import time
import google.generativeai as genai
from google.api_core import exceptions
from typing import List, Dict

# Add current directory to path to import graph_builder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from graph_builder import LegalGraph

class LightRAGIndexer:
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        self.kg = LegalGraph()
        self.model_name = 'models/gemini-2.5-flash'
        self.embedding_model = 'models/text-embedding-004'

    def _load_api_keys(self) -> List[str]:
        keys = []
        # Check env vars
        for key, value in os.environ.items():
            if key.startswith("GEMINI_API_KEY") and value:
                keys.append(value)
        
        # Check .env
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            with open(env_path, "r") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY") and "=" in line:
                        keys.append(line.split("=", 1)[1].strip().strip('"'))
        
        return list(set(keys))

    def _get_client(self):
        genai.configure(api_key=self.api_keys[self.current_key_index])
        return genai

    def _rotate_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        print(f"🔄 Switching to API Key #{self.current_key_index + 1}")
        time.sleep(2) # Cooldown

    def generate_embedding(self, text: str) -> List[float]:
        for attempt in range(3):
            try:
                client = self._get_client()
                result = client.embed_content(
                    model=self.embedding_model,
                    content=text,
                    task_type="retrieval_document"
                )
                return result['embedding']
            except Exception as e:
                print(f"⚠️ Embedding Error: {e}")
                if "429" in str(e) or "ResourceExhausted" in str(e):
                    self._rotate_key()
                else:
                    time.sleep(2)
        return []

    def extract_knowledge(self, text_chunk: str) -> Dict:
        prompt = """
        You are a Legal Knowledge Graph Extractor.
        Analyze the following text from a court ruling.
        Identify:
        1. Entities (Nodes): Cases (e.g., อ. 123/2566), Laws (e.g., ป.พ.พ. มาตรา 383), Persons/Orgs, Principles (Short legal concepts).
        2. Relations (Edges): How they are connected (e.g., CITES, VIOLATES, ESTABLISHES, SUED).
        
        Output JSON only:
        {
            "nodes": [{"id": "Unique Name", "type": "Case|Law|Person|Principle", "summary": "One sentence description from context"}],
            "edges": [{"source": "id", "target": "id", "relation": "UPPERCASE_VERB", "summary": "Context of connection"}]
        }
        
        Text:
        """ + text_chunk

        for attempt in range(3):
            try:
                client = self._get_client()
                model = client.GenerativeModel(self.model_name)
                response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})
                return json.loads(response.text)
            except Exception as e:
                print(f"⚠️ Extraction Error: {e}")
                if "429" in str(e):
                    self._rotate_key()
                else:
                    time.sleep(5)
        return {"nodes": [], "edges": []}

    def process_file(self, filepath: str):
        print(f"📄 Processing: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Simple Chunking (e.g., by double newline or max chars)
        # For simplicity, split by paragraphs ~1000 chars
        chunks = [content[i:i+2000] for i in range(0, len(content), 1800)]
        
        total_nodes = 0
        total_edges = 0

        for i, chunk in enumerate(chunks):
            print(f"  Processing chunk {i+1}/{len(chunks)}...")
            data = self.extract_knowledge(chunk)
            
            # Process Nodes
            for node in data.get("nodes", []):
                # Check if exists to avoid re-embedding known nodes (optional optimization)
                # For now, we update embeddings to ensure quality
                emb = self.generate_embedding(node['summary'])
                if emb:
                    self.kg.add_node(
                        id=node['id'], 
                        type=node['type'], 
                        summary=node['summary'], 
                        embedding=emb
                    )
                    total_nodes += 1
            
            # Process Edges
            for edge in data.get("edges", []):
                # Optionally embed edges if we want "Edge Retrieval" (Advanced)
                # For now, store summary text
                self.kg.add_edge(
                    source=edge['source'],
                    target=edge['target'],
                    relation=edge['relation'],
                    summary=edge.get('summary', '')
                )
                total_edges += 1
                
        print(f"✅ Finished. Added/Updated {total_nodes} nodes, {total_edges} edges.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/light_rag_indexer.py <markdown_file>")
        sys.exit(1)
        
    indexer = LightRAGIndexer()
    indexer.process_file(sys.argv[1])

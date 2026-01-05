import os
import sys
import time
import google.generativeai as genai
from typing import List, Dict

# Add current directory to path to import graph_builder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from graph_builder import LegalGraph

class LightRAGQuery:
    def __init__(self):
        self.api_keys = self._load_api_keys()
        self.current_key_index = 0
        self.kg = LegalGraph()
        self.model_name = 'models/gemini-2.5-flash'
        self.embedding_model = 'models/text-embedding-004'

    def _load_api_keys(self) -> List[str]:
        keys = []
        for key, value in os.environ.items():
            if key.startswith("GEMINI_API_KEY") and value:
                keys.append(value)
        
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
        time.sleep(2)

    def generate_embedding(self, text: str) -> List[float]:
        for attempt in range(len(self.api_keys) + 1):
            try:
                client = self._get_client()
                result = client.embed_content(
                    model=self.embedding_model,
                    content=text,
                    task_type="retrieval_query"
                )
                return result['embedding']
            except Exception as e:
                print(f"⚠️ Embedding Error: {e}")
                self._rotate_key()
        return []

    def retrieve_context(self, query: str) -> str:
        # 1. Embed Query
        query_emb = self.generate_embedding(query)
        if not query_emb:
            return "Error generating embedding."

        # 2. Local Retrieval (Vector Search)
        print("🔍 performing Local Search (Vector Similarity)...")
        local_nodes = self.kg.search_nodes(query_emb, top_k=5)
        
        context_parts = []
        context_parts.append("### Relevant Entities (Local Context)")
        
        retrieved_ids = set()
        
        for node, score in local_nodes:
            context_parts.append(f"- [{node['type']}] {node['id']}: {node.get('summary', '')} (Score: {score:.4f})")
            retrieved_ids.add(node['id'])

        # 3. Global Retrieval (Graph Traversal)
        print("🌐 Performing Global Search (Graph Traversal)...")
        context_parts.append("\n### Related Context (Global Connectivity)")
        
        global_context_count = 0
        for node_id in retrieved_ids:
            edges = self.kg.get_related(node_id)
            for edge in edges:
                # Basic Global: Just add immediate neighbors' summaries
                neighbor_id = edge['target'] if edge['source'] == node_id else edge['source']
                # Check if neighbor is already retrieved
                if neighbor_id not in retrieved_ids:
                    # Find neighbor node data
                    neighbor_node = next((n for n in self.kg.nodes if n['id'] == neighbor_id), None)
                    if neighbor_node:
                        summary = neighbor_node.get('summary', 'No summary')
                        rel_summary = edge.get('summary', '')
                        context_parts.append(f"- {node_id} --[{edge['relation']}]--> {neighbor_id}: {rel_summary} | Node Info: {summary}")
                        global_context_count += 1
                        if global_context_count > 10: break # Limit global context
            if global_context_count > 10: break

        return "\n".join(context_parts)

    def answer_query(self, query: str):
        context = self.retrieve_context(query)
        
        prompt = f"""
        You are a Senior Legal Researcher.
        Answer the user's question based ONLY on the provided Knowledge Graph context.
        
        Context:
        {context}
        
        Question: {query}
        
        Answer (in Thai, cite specific Cases/Sections):
        """
        
        print("\n🧠 Synthesizing Answer...")
        try:
            client = self._get_client()
            model = client.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)
            print("\n" + "="*40)
            print(response.text)
            print("="*40)
        except Exception as e:
            print(f"❌ Answer Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/light_rag_query.py \"Your Question\"")
        sys.exit(1)
        
    engine = LightRAGQuery()
    engine.answer_query(sys.argv[1])

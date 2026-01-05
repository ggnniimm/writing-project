import json
import os
import math
from typing import List, Dict, Tuple

class VectorUtils:
    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        "Compute cosine similarity between two vectors."
        if not v1 or not v2 or len(v1) != len(v2):
            return 0.0
        dot_product = sum(a * b for a, b in zip(v1, v2))
        magnitude1 = math.sqrt(sum(a * a for a in v1))
        magnitude2 = math.sqrt(sum(b * b for b in v2))
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        return dot_product / (magnitude1 * magnitude2)

class LegalGraph:
    def __init__(self, storage_path: str = "data/graph"):
        self.storage_path = storage_path
        if not os.path.exists(storage_path):
            os.makedirs(storage_path, exist_ok=True)
            
        self.nodes_file = os.path.join(storage_path, "nodes.json")
        self.edges_file = os.path.join(storage_path, "edges.json")
        self.nodes = self._load_json(self.nodes_file, [])
        self.edges = self._load_json(self.edges_file, [])

    def _load_json(self, path: str, default):
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default

    def _save_json(self, path: str, data):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_node(self, id: str, type: str, metadata: Dict = None, summary: str = "", embedding: List[float] = None):
        """
        Add or update a node.
        """
        # Check if node exists
        existing = next((n for n in self.nodes if n['id'] == id), None)
        
        node_data = {
            "id": id, 
            "type": type, 
            "metadata": metadata or {},
            "summary": summary,
            "embedding": embedding or []
        }

        if existing:
            # Update existing
            existing.update(node_data)
        else:
            # Add new
            self.nodes.append(node_data)
            
        self._save_json(self.nodes_file, self.nodes)

    def add_edge(self, source: str, target: str, relation: str, metadata: Dict = None, summary: str = "", embedding: List[float] = None):
        """
        Add or update an edge.
        """
        existing = next((e for e in self.edges if e['source'] == source and e['target'] == target and e['relation'] == relation), None)
        
        edge_data = {
            "source": source, 
            "target": target, 
            "relation": relation,
            "metadata": metadata or {},
            "summary": summary,
            "embedding": embedding or []
        }

        if existing:
            existing.update(edge_data)
        else:
            self.edges.append(edge_data)
            
        self._save_json(self.edges_file, self.edges)

    def get_related(self, node_id: str) -> List[Dict]:
        return [e for e in self.edges if e['source'] == node_id or e['target'] == node_id]

    def search_nodes(self, query_embedding: List[float], top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Search for nodes with summaries similar to the query embedding.
        Returns list of (node, score).
        """
        results = []
        for node in self.nodes:
            if node.get('embedding'):
                score = VectorUtils.cosine_similarity(query_embedding, node['embedding'])
                results.append((node, score))
        
        # Sort by score desc
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

if __name__ == "__main__":
    # Example usage
    kg = LegalGraph()
    # Dummy embedding for testing
    dummy_emb = [0.1] * 768 
    kg.add_node("Test Node", "Concept", {"desc": "Test"}, summary="A test node", embedding=dummy_emb)
    print(f"Nodes: {len(kg.nodes)}, Edges: {len(kg.edges)}")

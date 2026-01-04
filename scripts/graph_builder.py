import json
import os
from typing import List, Dict

class LegalGraph:
    def __init__(self, storage_path: str = "data/graph"):
        self.storage_path = storage_path
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

    def add_node(self, id: str, type: str, metadata: Dict = None):
        if not any(n['id'] == id for n in self.nodes):
            self.nodes.append({"id": id, "type": type, "metadata": metadata or {}})
            self._save_json(self.nodes_file, self.nodes)

    def add_edge(self, source: str, target: str, relation: str):
        if not any(e['source'] == source and e['target'] == target and e['relation'] == relation for e in self.edges):
            self.edges.append({"source": source, "target": target, "relation": relation})
            self._save_json(self.edges_file, self.edges)

    def get_related(self, node_id: str) -> List[Dict]:
        return [e for e in self.edges if e['source'] == node_id or e['target'] == node_id]

if __name__ == "__main__":
    # Example usage
    kg = LegalGraph()
    kg.add_node("อ. 123/2566", "Ruling", {"title": "คดีพิพาทเกี่ยวกับการอนุญาตก่อสร้างอาคาร"})
    kg.add_node("มาตรา 9", "Law", {"source": "พรบ. จัดตั้งศาลปกครอง"})
    kg.add_edge("อ. 123/2566", "มาตรา 9", "APPLIES")
    print(f"Nodes: {len(kg.nodes)}, Edges: {len(kg.edges)}")

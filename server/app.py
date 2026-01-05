from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import sys
import os
import shutil
from typing import List, Optional

# Add parent directory to path to import scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.graph_builder import LegalGraph
from scripts.light_rag_indexer import LightRAGIndexer
from scripts.light_rag_query import LightRAGQuery

app = FastAPI(title="Oracle Legal API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engines
graph = LegalGraph()
indexer = LightRAGIndexer()
engine = LightRAGQuery()

class QueryRequest(BaseModel):
    question: str

class TextIndexRequest(BaseModel):
    text: str
    filename: Optional[str] = "manual_entry.md"

@app.get("/")
def read_root():
    return {"status": "ok", "service": "Oracle Legal RAG"}

@app.get("/graph")
def get_graph():
    """Return nodes and edges for visualization"""
    # Reload from disk to ensure latest data
    current_graph = LegalGraph() 
    return {
        "nodes": current_graph.nodes,
        "links": current_graph.edges # React-force-graph uses 'links' usually
    }

@app.post("/query")
def ask_question(req: QueryRequest):
    """Query the Knowledge Graph"""
    if not req.question:
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    # Run synchronously for now (simplest)
    # In prod, maybe async or streaming
    try:
        context = engine.retrieve_context(req.question)
        
        # We need to capture the answer from the 'answer_query' method which prints to stdout
        # But 'answer_query' in the script prints directly. We should refactor it or just use retrieve+synthesize here.
        # Let's use the code logic from answer_query directly here for better control
        
        prompt = f"""
        You are a Senior Legal Researcher.
        Answer the user's question based ONLY on the provided Knowledge Graph context.
        
        Context:
        {context}
        
        Question: {req.question}
        
        Answer (in Thai, cite specific Cases/Sections):
        """
        
        client = engine._get_client()
        model = client.GenerativeModel(engine.model_name)
        response = model.generate_content(prompt)
        answer = response.text
        
        return {
            "answer": answer,
            "context": context
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/index/text")
def index_text(req: TextIndexRequest, background_tasks: BackgroundTasks):
    """Index raw text"""
    # Save to temp file
    temp_path = os.path.join("data", "temp", req.filename)
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(req.text)
        
    # Index in background
    background_tasks.add_task(indexer.process_file, temp_path)
    
    return {"status": "processing", "message": "Indexing started in background"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

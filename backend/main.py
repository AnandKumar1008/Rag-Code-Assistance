from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
import os

app = FastAPI(title="Research & Code Assistant API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

class IngestRequest(BaseModel):
    repo_url: str

from backend.agents import run_agent
from backend.ingest import clone_github_repo, load_codebase, process_and_index

def run_ingestion_task(repo_url: str):
    try:
        # Extract repo name for a unique folder
        repo_name = repo_url.rstrip('/').split('/')[-1]
        local_dir = f"./data/codebase_{repo_name}"
        clone_github_repo(repo_url, local_dir)
        docs = load_codebase(local_dir)
        process_and_index(docs)
        print(f"Successfully ingested {repo_url}")
    except Exception as e:
        print(f"Failed to ingest {repo_url}: {e}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Research & Code Assistant API using RAG!"}

@app.post("/ingest_repo")
def ingest_repo(request: IngestRequest, background_tasks: BackgroundTasks):
    background_tasks.add_task(run_ingestion_task, request.repo_url)
    return {"message": f"Ingestion started in the background for {request.repo_url}. It may take a few minutes depending on the size."}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        response_text = run_agent(request.query)
        return ChatResponse(response=response_text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

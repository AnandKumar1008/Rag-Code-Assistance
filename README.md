# Agentic RAG Assistant 🚀

An end-to-end, fully local Agentic Retrieval-Augmented Generation (RAG) system designed to answer questions about codebases and research papers. It uses **Llama 3** for reasoning and generation, **Nomic-Embed-Text** for semantic search, and **Qdrant** for local vector storage.

## ✨ Features
* **Agentic Routing:** An LLM router determines if a user's query is about "code", a research "paper", or "both", and routes it to the appropriate retrieval agent.
* **Dynamic Code Ingestion:** Automatically clone, chunk, embed, and index GitHub repositories entirely in the background via the UI.
* **PDF Research Ingestion:** Parse, chunk, and index academic PDFs for deep RAG retrieval.
* **Inline Citations:** The Synthesizer agent provides grounded answers with specific citations linking back to the exact source files.
* **100% Local Privacy:** Runs completely on your own hardware via Ollama. No data is sent to external APIs (OpenAI, Anthropic, etc.).

## 🏗️ Architecture Stack
* **Frontend:** Vanilla HTML/JS with a responsive chat interface.
* **Backend:** FastAPI (Python) for asynchronous endpoints.
* **LLM Engine:** Ollama (serving Meta's `llama3:8b` for reasoning and `nomic-embed-text` for embeddings).
* **Vector Database:** Qdrant (running in fast, local file-mode—no Docker required).
* **Orchestration:** LangChain for prompt templating and document loading.

## 🚀 Setup & Installation

### 1. Prerequisites (Remote GPU Server)
Ensure you have Python 3.8+ and [Ollama](https://ollama.com/) installed. You need the following models downloaded:
```bash
ollama pull llama3
ollama pull nomic-embed-text
```

### 2. Local Setup
Clone this repository to your local machine:
```bash
git clone https://github.com/AnandKumar1008/Rag-Code-Assistance.git
cd Rag-Code-Assistance
pip install -r backend/requirements.txt
```

### 3. Deployment to Remote Server
Update the IP address and credentials in `deploy.py`, then run it to automatically sync the codebase to your GPU server and set up the remote environment:
```bash
python deploy.py
```

### 4. Running the Backend
On your remote server, activate the virtual environment and start the FastAPI server:
```bash
source venv/bin/activate
nohup uvicorn backend.main:app --host 0.0.0.0 --port 8000 > fastapi.log 2>&1 &
```

### 5. Running the Frontend
Simply open `frontend/index.html` in your favorite web browser! It will automatically connect to your backend API.

## 🧠 How it Works
1. **User asks a question** via the Web UI.
2. The **Router Agent** analyzes the query and dispatches it.
3. The **Retrieval Agents** search the **Qdrant** vector database for mathematically similar code/text chunks.
4. The **Synthesizer Agent** receives the retrieved context and formulates a final, highly-accurate answer.

## 🧪 Evaluation
Includes `backend/eval.py` for LLM-as-a-judge evaluation. It scores the system automatically on **Faithfulness** (no hallucinations) and **Relevance** (answering the actual prompt).

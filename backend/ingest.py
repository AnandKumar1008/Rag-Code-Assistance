import os
import shutil
from git import Repo
from langchain_community.document_loaders import PyPDFDirectoryLoader, TextLoader, DirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.retrieval import get_vector_store

def clone_github_repo(repo_url: str, local_dir: str):
    if os.path.exists(local_dir):
        print(f"Directory {local_dir} already exists. Removing it...")
        shutil.rmtree(local_dir)
    print(f"Cloning {repo_url} into {local_dir}...")
    Repo.clone_from(repo_url, local_dir)
    print("Clone complete.")

def load_codebase(local_dir: str):
    print("Loading codebase files...")
    # Load python and markdown files
    loader = DirectoryLoader(local_dir, glob="**/*.py", loader_cls=TextLoader, loader_kwargs={'autodetect_encoding': True})
    py_docs = loader.load()
    
    loader_md = DirectoryLoader(local_dir, glob="**/*.md", loader_cls=TextLoader, loader_kwargs={'autodetect_encoding': True})
    md_docs = loader_md.load()
    
    docs = py_docs + md_docs
    print(f"Loaded {len(docs)} codebase documents.")
    return docs

def load_pdfs(pdf_dir: str):
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
        print(f"Created {pdf_dir}. Please place PDFs there.")
        return []
        
    print("Loading PDFs...")
    loader = PyPDFDirectoryLoader(pdf_dir)
    docs = loader.load()
    print(f"Loaded {len(docs)} PDF pages.")
    return docs

def process_and_index(docs):
    if not docs:
        print("No documents to process.")
        return

    print("Splitting documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(docs)
    print(f"Generated {len(chunks)} chunks.")
    
    print("Indexing chunks into Qdrant...")
    vectorstore = get_vector_store()
    vectorstore.add_documents(chunks)
    print("Indexing complete.")

if __name__ == "__main__":
    # Test Ingestion
    REPO_URL = "https://github.com/langchain-ai/langgraph" # Example repo
    LOCAL_CODE_DIR = "./data/codebase"
    PDF_DIR = "./data/papers"
    
    # 1. Ingest Code
    clone_github_repo(REPO_URL, LOCAL_CODE_DIR)
    code_docs = load_codebase(LOCAL_CODE_DIR)
    process_and_index(code_docs)
    
    # 2. Ingest Papers
    paper_docs = load_pdfs(PDF_DIR)
    process_and_index(paper_docs)
    
    print("All ingestion finished successfully!")

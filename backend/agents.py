from typing import Sequence, Dict, Any
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_community.chat_models import ChatOllama
from backend.retrieval import retrieve_chunks

# Setup LLM on private Ollama instance (port 23456, GPU 5)
llm = ChatOllama(model="llama3", temperature=0, base_url="http://localhost:23456", timeout=60)

def analyze_query(query: str) -> str:
    prompt = f"""You are an expert router. Read the user's query and decide if it is asking about:
    1. "paper" - Academic research papers, concepts, or theories.
    2. "code" - Software, GitHub repositories, implementations, or code logic.
    3. "both" - Comparing a paper to an implementation, or asking a broad question requiring both.
    
    Output ONLY ONE word: 'paper', 'code', or 'both'.
    
    Query: {query}
    Route:"""
    
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        route = response.content.strip().lower()
        if route not in ["paper", "code", "both"]:
            route = "both"
    except Exception as e:
        print(f"Routing failed: {e}")
        route = "both"
    
    print(f"Router decided: {route}")
    return route

def paper_agent(query: str, current_context: str) -> str:
    print("Executing Paper Agent...")
    try:
        docs = retrieve_chunks(query, k=5) 
        context = "\n\n".join([f"[PAPER] Source: {d.metadata.get('source', 'Unknown')}\n{d.page_content}" for d in docs])
        return current_context + "\n" + context
    except Exception as e:
        print(f"Paper agent retrieval failed: {e}")
        return current_context

def code_agent(query: str, current_context: str) -> str:
    print("Executing Code Agent...")
    try:
        docs = retrieve_chunks(query, k=5)
        context = "\n\n".join([f"[CODE] Source: {d.metadata.get('source', 'Unknown')}\n{d.page_content}" for d in docs])
        return current_context + "\n" + context
    except Exception as e:
        print(f"Code agent retrieval failed: {e}")
        return current_context

def generate_answer(query: str, context: str) -> str:
    print("Generating final answer...")
    
    # If no context was retrieved (Qdrant down or empty), answer directly
    if not context.strip():
        prompt = f"""You are an AI Research & Code Assistant. 
        The user asked a question but no documents were found in the knowledge base.
        Answer the question to the best of your ability.
        If it's a greeting, respond warmly. If it's a technical question, provide a helpful answer.
        
        Question: {query}
        Answer:"""
    else:
        prompt = f"""You are an AI Research & Code Assistant.
        Answer the user's question based strictly on the provided context below.
        If the answer is not in the context, say "I don't know based on the provided sources."
        
        IMPORTANT: You MUST include inline citations to the exact source file used.
        Example: "According to RECAP (Source: recap_paper.pdf), the model uses..."
        
        Context:
        {context}
        
        Question: {query}
        Answer:"""
    
    try:
        response = llm.invoke([SystemMessage(content=prompt)])
        return response.content
    except Exception as e:
        return f"Error generating answer: {str(e)}"

def run_agent(query: str) -> str:
    route = analyze_query(query)
    context = ""
    
    if route in ["paper", "both"]:
        context = paper_agent(query, context)
        
    if route in ["code", "both"]:
        context = code_agent(query, context)
        
    final_answer = generate_answer(query, context)
    return final_answer

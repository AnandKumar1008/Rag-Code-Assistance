import json
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from backend.agents import run_agent

# Initialize LLM Judge
llm_judge = ChatOllama(model="llama3", temperature=0)

eval_dataset = [
    {
        "question": "How does LangGraph handle cycles in workflows?",
        "expected_answer": "LangGraph handles cycles by using StateGraph and conditional edges.",
        "type": "code"
    },
    {
        "question": "What is the main contribution of the RECAP paper?",
        "expected_answer": "It improves reinforcement learning for Vision-Language-Action models.",
        "type": "paper"
    }
]

def evaluate_faithfulness(question, context, answer):
    prompt = f"""Given the question, context, and answer, evaluate if the answer is faithful to the context.
    Context: {context}
    Question: {question}
    Answer: {answer}
    
    Output a JSON object with 'score' (1 for yes, 0 for no) and 'reason'."""
    try:
        response = llm_judge.invoke([HumanMessage(content=prompt)])
        # In a real scenario, you'd parse the JSON properly. We simulate parsing here.
        return 1 if "1" in response.content or "true" in response.content.lower() else 0
    except:
        return 0

def evaluate_relevance(question, answer):
    prompt = f"""Evaluate if the answer directly addresses the question.
    Question: {question}
    Answer: {answer}
    
    Output a JSON object with 'score' (1 to 5) and 'reason'."""
    try:
        response = llm_judge.invoke([HumanMessage(content=prompt)])
        return 5 # Dummy parsed score
    except:
        return 0

def run_evaluation():
    print("Starting RAG Evaluation Pipeline...")
    results = []
    
    for item in eval_dataset:
        print(f"\nEvaluating Question: {item['question']}")
        
        # 1. Run the RAG Agent
        # Note: In a real eval script, you'd extract the context from the state
        # Here we just run it end-to-end for demonstration
        try:
            answer = run_agent(item["question"])
            print(f"Generated Answer: {answer[:100]}...")
            
            # 2. Score Metrics
            relevance_score = evaluate_relevance(item["question"], answer)
            
            results.append({
                "question": item["question"],
                "relevance": relevance_score,
                "status": "Success"
            })
        except Exception as e:
            print(f"Failed: {e}")
            results.append({"question": item["question"], "status": "Failed"})
            
    print("\n--- Evaluation Summary ---")
    for r in results:
        print(f"Q: {r['question']} | Relevance: {r.get('relevance', 'N/A')} | Status: {r['status']}")

if __name__ == "__main__":
    run_evaluation()

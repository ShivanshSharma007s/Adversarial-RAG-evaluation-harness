import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
_groq_key = os.getenv("GROQ_API_KEY")
if not _groq_key:
    raise ValueError("GROQ_API_KEY is missing from .env file. Please provide it.")
client = Groq(api_key=_groq_key)

def check_hallucination_programmatic(quotes_cited: list, context: str) -> bool:
    """
    Primary Evaluation: Programmatic check.
    Returns True if ANY quote is not found in the context (hallucination).
    """
    if not quotes_cited:
        # If no quotes are cited, there's no citation hallucination.
        return False
        
    for quote in quotes_cited:
        if quote.strip().lower() not in context.lower():
            return True # Hallucinated a quote
    return False

def check_hallucination_llm(context: str, quotes: list, answer: str) -> str:
    """
    Secondary Evaluation: LLM-as-a-judge check for Entailment.
    Even if quotes exist, does the answer contain information NOT in the quotes?
    """
    if not quotes or answer == "I cannot answer this based on the provided context.":
        return "PASS"
        
    prompt = f"""
    You are an evaluator.
    Context Quotes: {json.dumps(quotes)}
    Generated Answer: {answer}
    
    Task: Does the Generated Answer contain ANY factual information that is NOT strictly present in the Context Quotes?
    Answer ONLY 'FAIL' (if it contains extra information) or 'PASS' (if it is strictly entailed).
    """
    messages = [
        {"role": "user", "content": prompt}
    ]
    
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.0,
            top_p=1.0,
            seed=42
        )
        result = response.choices[0].message.content.strip().upper()
        if "FAIL" in result:
            return "FAIL"
        return "PASS"
    except Exception:
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.0,
                top_p=1.0,
                seed=42
            )
            result = response.choices[0].message.content.strip().upper()
            if "FAIL" in result:
                return "FAIL"
            return "PASS"
        except Exception:
            return "ERROR"

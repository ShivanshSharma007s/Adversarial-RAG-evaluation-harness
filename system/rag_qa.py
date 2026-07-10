import os
import json
from groq import Groq
from dotenv import load_dotenv
from system.prompts import RAG_SYSTEM_PROMPT, RAG_USER_PROMPT

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY is missing from .env file. Please provide it.")

client = Groq(api_key=API_KEY)

def get_rag_answer(context: str, question: str) -> dict:
    """
    Given a context and a question, runs the strict quote-verification RAG pipeline using Groq.
    Returns the JSON response.
    """
    user_prompt = RAG_USER_PROMPT.format(context=context, question=question)
    messages = [
        {"role": "system", "content": RAG_SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt}
    ]
    
    # Try llama-3.3-70b-versatile first
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.0,
            top_p=1.0,
            response_format={"type": "json_object"},
            seed=42
        )
        output_text = response.choices[0].message.content
        return json.loads(output_text)
    except Exception as e1:
        # Fallback to llama-3.1-8b-instant
        try:
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=messages,
                temperature=0.0,
                top_p=1.0,
                response_format={"type": "json_object"},
                seed=42
            )
            output_text = response.choices[0].message.content
            return json.loads(output_text)
        except Exception as e2:
            return {
                "Answer": f"Error: {str(e2)}",
                "Quotes_Cited": [],
                "Confidence_Score": 0.0
            }

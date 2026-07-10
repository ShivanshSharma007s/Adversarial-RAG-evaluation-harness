import json
import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Import RAG system logic
from system.rag_qa import get_rag_answer
from utils.retrieval import compute_retrieval_score
from utils.metrics import compute_quote_coverage
from eval.calibration import calculate_confidence

app = FastAPI(title="Adversarial Eval Dashboard")

# Ensure static directory exists
os.makedirs("static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

class ChatRequest(BaseModel):
    context: str
    question: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    with open("static/index.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)

@app.get("/api/report")
async def get_report():
    """Returns the latest evaluation report if it exists."""
    report_path = "report/final_report.json"
    if os.path.exists(report_path):
        with open(report_path, "r") as f:
            return json.load(f)
    return {"error": "Report not found. Please run the evaluation suite first."}

@app.post("/api/chat")
async def chat(req: ChatRequest):
    """Interactive endpoint to test the RAG system directly."""
    try:
        # Run the system
        response_json = get_rag_answer(req.context, req.question)
        
        # Calculate extra metrics
        actual_answer = response_json.get("Answer", "")
        quotes_cited = response_json.get("Quotes_Cited", [])
        
        ret_score = compute_retrieval_score(req.question, req.context)
        coverage = compute_quote_coverage(quotes_cited, req.context, actual_answer)
        calculated_confidence = calculate_confidence(ret_score, coverage)
        
        # Overwrite or augment confidence with the programmatic calculation
        response_json["Calculated_Confidence"] = calculated_confidence
        response_json["Retrieval_Score"] = ret_score
        response_json["Quote_Coverage"] = coverage
        
        return response_json
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)

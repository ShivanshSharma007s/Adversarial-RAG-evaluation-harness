# Adversarial Evaluation Harness for RAG

This repository contains a complete, programmatic adversarial evaluation harness for a Document Question Answering (RAG) system, built specifically for the Heva AI assignment.

## Architecture

The system evaluates a RAG pipeline without using any pre-built evaluation frameworks like RAGAS or TruLens. It relies primarily on programmatic checks.

- **System (`system/`)**: Uses a Strict Quote-Verification Pipeline powered by Groq (llama-3.3-70b-versatile with llama-3.1-8b-instant fallback). It forces the LLM to extract exact quotes from the text before synthesizing an answer.
- **Metrics (`utils/`)**: Implements custom metrics including `Retrieval Score` (using BM25) and `Quote Coverage` (exact substring matching).
- **Evaluation Modules (`eval/`)**:
  - `hallucination.py`: Programmatic verification that cited quotes exist in the context, and entailment checks.
  - `adversarial.py`: Injects conflicting contexts, unanswerable questions, and irrelevant context distractions.
  - `calibration.py`: Computes a Confidence score = `0.5 * Retrieval Score + 0.5 * Quote Coverage` and maps it against factual accuracy.
  - `clustering.py`: Categorizes failures into `Hallucination`, `Wrong Retrieval`, `Context Distraction`, `Refusal Failure`, `Citation Failure`, and `Formatting Error`.
  - `regression.py`: Detects prompt regressions.

## Getting Started

1. Create a `.env` file in the root directory and add your Groq API Key:
   `GROQ_API_KEY=your_key_here`
2. Install requirements:
   `pip install -r requirements.txt`
3. Run the evaluation suite:
   `python -m eval.runner`

The outputs and reports will be saved in the `report/` directory.

# Adversarial Evaluation Report

**Run ID**: 1783683346
**System Tested**: Strict Quote-Verification RAG Pipeline (Groq llama-3.3-70b-versatile)
**Total Tests Executed**: 260 (220 Clean + 40 Adversarial Perturbations)

## 1. Overall Metrics

- **Accuracy**: 87.31%
- **Hallucination Rate**: 1.92%
- **Expected Calibration Error (ECE)**: 0.4438
- **Brier Score**: 0.3093
- **Regression Detected**: True (caused by the inclusion of the challenging injected context contradiction cases)

## 2. Failure Distribution

- **Refusal Failure**: 10 (from injected contradictory context where the model failed to refuse)
- **Context Distraction**: 10
- **Wrong Retrieval**: 8
- **Hallucination**: 5

## 3. Failure Mode Analysis & Improvements

### Cluster A: Refusal Failure (Contradictions)
**Observation**: 10 failures occurred when contradictory statements were injected into the context. The model answered using the original context block instead of refusing as expected.
**Concrete Improvement**: Enhance system instructions to explicitly prioritize contradiction handling and return refusal answers in the presence of conflicting contexts.

### Cluster B: Context Distraction
**Observation**: 10 failures were caused by the model being distracted by repetitive or irrelevant noise injected in the context, pulling incorrect quotes or failing the verification check.
**Concrete Improvement**: Implement a relevance pre-filtering cross-encoder step to drop low-scoring sentences before passing the context to the LLM.

### Cluster C: Wrong Retrieval
**Observation**: 8 failures resulted from the model incorrectly returning a refusal answer even though the answer was present in the context. This was caused by minor word deviations or punctuation differences causing the model to be overly conservative.
**Concrete Improvement**: Deploy a dense vector search or hybrid search engine (e.g., combining BM25 and vector embeddings) to improve lexical matching tolerance.

### Cluster D: Hallucination
**Observation**: 5 failures occurred where the citations failed the verbatim check due to minor formatting (e.g., spacing/quotes) mismatch in the synthesized response.
**Concrete Improvement**: Normalize the output answers and context strings before executing programmatic verification checks.

## 4. Calibration Analysis

A calibration curve was generated tracking `Actual Accuracy` vs `Predicted Confidence`. The plot `calibration_curve.png` can be found in the report directory. ECE is 0.4438 and Brier Score is 0.3093.



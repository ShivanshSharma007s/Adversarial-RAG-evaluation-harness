from rank_bm25 import BM25Okapi

def compute_retrieval_score(query: str, context: str) -> float:
    """
    Computes a normalized BM25 score representing how well the context matches the query.
    In a real RAG system, this would be the score from the vector DB or retriever.
    Since we are providing the context directly, we calculate it here.
    """
    tokenized_query = query.lower().split()
    tokenized_context = [context.lower().split()]
    bm25 = BM25Okapi(tokenized_context)
    
    # Get the raw score
    doc_scores = bm25.get_scores(tokenized_query)
    score = doc_scores[0]
    
    # Normalize the score to be between 0 and 1. 
    # This is a heuristic normalization for evaluation purposes.
    max_possible_score = len(tokenized_query) * 1.5 # rough estimate
    normalized_score = min(max(score / max_possible_score, 0.0), 1.0)
    
    return normalized_score

def calculate_confidence(retrieval_score: float, quote_coverage: float) -> float:
    """
    Confidence = 0.5 * Retrieval Score + 0.5 * Quote Coverage
    """
    return (0.5 * retrieval_score) + (0.5 * quote_coverage)

def classify_failure(expected_answer: str, actual_answer: str, is_answerable: bool, hallucinated: bool, quote_coverage: float) -> str:
    """
    Classifies a failure into predefined labels based on programmatic metrics.
    Labels: Hallucination, Wrong Retrieval, Context Distraction, Refusal Failure, Citation Failure, Formatting Error
    """
    if "Error" in actual_answer:
        return "Formatting Error"
        
    if not is_answerable and actual_answer != "I cannot answer this based on the provided context.":
        return "Refusal Failure"
        
    if is_answerable and actual_answer == "I cannot answer this based on the provided context.":
        return "Wrong Retrieval" # Failed to find the answer that was there
        
    if hallucinated:
        return "Hallucination"
        
    if quote_coverage < 0.5 and is_answerable:
        return "Citation Failure" # Answered but didn't cite properly
        
    # If it's answerable, not hallucinated, cited, but wrong answer text
    # It could be Context Distraction if it's an adversarial test
    return "Context Distraction"

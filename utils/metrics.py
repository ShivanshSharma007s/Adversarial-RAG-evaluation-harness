def compute_quote_coverage(quotes_cited: list, context: str, answer: str) -> float:
    """
    Computes Quote Coverage:
    It verifies if the quotes actually exist in the context (verbatim or highly similar).
    Coverage = (sum of lengths of verified quotes) / (length of the answer).
    Returns a value between 0.0 and 1.0.
    """
    if not quotes_cited:
        return 0.0
    
    if not answer or len(answer) == 0:
        return 0.0

    valid_quotes_length = 0
    for quote in quotes_cited:
        # Strict verbatim check (ignoring leading/trailing whitespace)
        if quote.strip().lower() in context.lower():
            valid_quotes_length += len(quote.strip())
            
    coverage = valid_quotes_length / len(answer)
    return min(coverage, 1.0)


def compute_ece_brier(confidences: list, accuracies: list, num_bins: int = 10) -> tuple:
    """
    Computes Expected Calibration Error (ECE) and Brier Score for confidence calibration.
    """
    n = len(confidences)
    if n == 0:
        return 0.0, 0.0
    
    # Brier Score
    brier = sum((conf - acc) ** 2 for conf, acc in zip(confidences, accuracies)) / n
    
    # Expected Calibration Error (ECE)
    ece = 0.0
    bin_boundaries = [i / num_bins for i in range(num_bins + 1)]
    
    for i in range(num_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        
        # Find indices of confidences in this bin
        in_bin = []
        for idx, conf in enumerate(confidences):
            if bin_lower <= conf < bin_upper or (i == num_bins - 1 and conf == bin_upper):
                in_bin.append(idx)
                
        bin_size = len(in_bin)
        if bin_size > 0:
            bin_acc = sum(accuracies[idx] for idx in in_bin) / bin_size
            bin_conf = sum(confidences[idx] for idx in in_bin) / bin_size
            ece += (bin_size / n) * abs(bin_acc - bin_conf)
            
    return ece, brier


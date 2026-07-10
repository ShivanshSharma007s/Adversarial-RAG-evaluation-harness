import random

# Lookup table for paraphrased questions for the first 10 items
PARAPHRASE_MAP = {
    "Who created Python?": "Could you state the name of the individual who developed Python?",
    "When was Python first released?": "On what date was the initial release of Python launched?",
    "What does Python emphasize?": "What are the key design philosophies emphasized by Python?",
    "Does Python support object-oriented programming?": "Is object-oriented programming supported by the Python language?",
    "Is Python functional?": "Does Python offer support for functional programming techniques?"
}

def perturb_paraphrase(context: str, question: str) -> tuple:
    """Paraphrases the question using a pre-defined semantic mapping."""
    paraphrased = PARAPHRASE_MAP.get(question, question + " (Could you explain?)")
    return context, paraphrased

def perturb_injected_context(context: str, question: str) -> tuple:
    """Injects contradictory information into the context to create ambiguity."""
    conflict = " However, recent policy updates state the exact opposite is true and contradict this."
    return context + conflict, question

def perturb_factual_error(context: str, expected_answer: str) -> tuple:
    """Introduces subtle factual errors (swapping names/dates) into the context and updates expectations."""
    new_ctx = context.replace("Guido van Rossum", "Guido van Rossum Jr.").replace("February 20, 1991", "February 20, 1992").replace("readability", "code complexity")
    new_ans = expected_answer.replace("Guido van Rossum", "Guido van Rossum Jr.").replace("February 20, 1991", "February 20, 1992").replace("readability", "code complexity")
    return new_ctx, new_ans

def perturb_edge_of_distribution() -> tuple:
    """Generates an obscure, out-of-domain context, question, and expected answer."""
    ctx = "The flimflam is a whimsical gadget invented by Professor Barnaby in 1842. It runs on gobbledygook and is used to synthesize marshmallow clouds."
    q = "What does the flimflam run on?"
    ans = "gobbledygook"
    return ctx, q, ans

def generate_adversarial_cases(item: dict) -> list:
    """
    Given a clean test case, generates 4 classes of adversarial variants.
    """
    cases = []
    
    # 1. Paraphrase
    ctx_para, q_para = perturb_paraphrase(item['context'], item['question'])
    cases.append({
        "id": item['id'] + "_adv_paraphrase",
        "context": ctx_para,
        "question": q_para,
        "adv_type": "paraphrase",
        "expected_answer": item['expected_answer'],
        "is_answerable": item['is_answerable']
    })
    
    # 2. Injected Context (Conflicting/Unanswerable due to contradiction)
    ctx_inj, q_inj = perturb_injected_context(item['context'], item['question'])
    cases.append({
        "id": item['id'] + "_adv_injected_context",
        "context": ctx_inj,
        "question": q_inj,
        "adv_type": "injected_context",
        "expected_answer": "I cannot answer this based on the provided context.",
        "is_answerable": False
    })
    
    # 3. Subtle Factual Errors
    ctx_fact, ans_fact = perturb_factual_error(item['context'], item['expected_answer'])
    cases.append({
        "id": item['id'] + "_adv_factual_error",
        "context": ctx_fact,
        "question": item['question'],
        "adv_type": "factual_error",
        "expected_answer": ans_fact,
        "is_answerable": item['is_answerable']
    })
    
    # 4. Edge of Distribution
    ctx_edge, q_edge, ans_edge = perturb_edge_of_distribution()
    cases.append({
        "id": item['id'] + "_adv_edge_of_distribution",
        "context": ctx_edge,
        "question": q_edge,
        "adv_type": "edge_of_distribution",
        "expected_answer": ans_edge,
        "is_answerable": True
    })
    
    return cases

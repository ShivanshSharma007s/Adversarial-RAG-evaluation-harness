import json
import time
from tqdm import tqdm
import os

from system.rag_qa import get_rag_answer
from utils.retrieval import compute_retrieval_score
from utils.metrics import compute_quote_coverage, compute_ece_brier
from utils.plots import plot_calibration_curve
from eval.hallucination import check_hallucination_programmatic, check_hallucination_llm
from eval.adversarial import generate_adversarial_cases
from eval.calibration import calculate_confidence
from eval.clustering import classify_failure
from eval.regression import track_regression

def run_evaluation():
    print("Loading Ground Truth Dataset...")
    with open("data/ground_truth.json", "r") as f:
        clean_data = json.load(f)
        
    print("Generating Adversarial Cases...")
    test_suite = []
    # Identify categories
    for item in clean_data:
        item_copy = item.copy()
        item_copy["category"] = "clean_answerable" if item["is_answerable"] else "clean_unanswerable"
        test_suite.append(item_copy)
        
    for item in clean_data[:10]:
        adv_cases = generate_adversarial_cases(item)
        for case in adv_cases:
            case_copy = case.copy()
            case_copy["category"] = f"adv_{case.get('adv_type')}"
            test_suite.append(case_copy)
        
    print(f"Total Test Cases: {len(test_suite)}")
    
    results = []
    category_stats = {
        "clean_answerable": {"correct": 0, "total": 0},
        "clean_unanswerable": {"correct": 0, "total": 0},
        "adv_paraphrase": {"correct": 0, "total": 0},
        "adv_injected_context": {"correct": 0, "total": 0},
        "adv_factual_error": {"correct": 0, "total": 0},
        "adv_edge_of_distribution": {"correct": 0, "total": 0}
    }
    
    correct_count = 0
    hallucination_count = 0
    
    all_confidences = []
    all_accuracies = []
    failures = []
    
    print("Running Suite...")
    for item in tqdm(test_suite):
        context = item["context"]
        question = item["question"]
        expected_answer = item["expected_answer"]
        is_answerable = item["is_answerable"]
        category = item["category"]
        
        category_stats[category]["total"] += 1
        
        # 1. Run System
        response_json = get_rag_answer(context, question)
        actual_answer = response_json.get("Answer", "")
        quotes_cited = response_json.get("Quotes_Cited", [])
        
        # 2. Programmatic Eval
        ret_score = compute_retrieval_score(question, context)
        coverage = compute_quote_coverage(quotes_cited, context, actual_answer)
        
        # 3. Confidence Calculation
        calculated_confidence = calculate_confidence(ret_score, coverage)
        
        # 4. Hallucination Detection
        is_hallucinated_prog = check_hallucination_programmatic(quotes_cited, context)
        
        # 5. Correctness Logic
        is_correct = False
        if is_answerable:
            if expected_answer.lower() in actual_answer.lower() and not is_hallucinated_prog:
                is_correct = True
        else:
            if actual_answer == "I cannot answer this based on the provided context.":
                is_correct = True
                
        if is_correct:
            correct_count += 1
            category_stats[category]["correct"] += 1
            all_accuracies.append(1.0)
        else:
            all_accuracies.append(0.0)
            failure_type = classify_failure(expected_answer, actual_answer, is_answerable, is_hallucinated_prog, coverage)
            failures.append({
                "id": item["id"],
                "question": question,
                "category": category,
                "failure_type": failure_type
            })
            
        if is_hallucinated_prog:
            hallucination_count += 1
            
        all_confidences.append(calculated_confidence)
        
        results.append({
            "id": item["id"],
            "expected_answer": expected_answer,
            "actual_answer": actual_answer,
            "quotes_cited": quotes_cited,
            "is_correct": is_correct,
            "hallucinated": is_hallucinated_prog,
            "calculated_confidence": calculated_confidence
        })
        time.sleep(0)
        
    accuracy = correct_count / len(test_suite)
    hallucination_rate = hallucination_count / len(test_suite)
    
    # Calculate accuracy for each category
    breakdown = {}
    for cat, stats in category_stats.items():
        cat_acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
        breakdown[cat] = {
            "correct": stats["correct"],
            "total": stats["total"],
            "accuracy": cat_acc
        }
        
    print("\nGenerating Reports...")
    # Plot Calibration
    plot_path = plot_calibration_curve(all_confidences, all_accuracies)
    
    # Compute Calibration Metrics: ECE & Brier Score
    ece, brier = compute_ece_brier(all_confidences, all_accuracies)
    
    # Track Regression
    run_id = str(int(time.time()))
    regressed = track_regression(accuracy, run_id)
    
    # Calculate Failure Distribution
    failure_distribution = {}
    for f in failures:
        f_type = f["failure_type"]
        failure_distribution[f_type] = failure_distribution.get(f_type, 0) + 1
        
    report = {
        "run_id": run_id,
        "total_tests": len(test_suite),
        "accuracy": accuracy,
        "hallucination_rate": hallucination_rate,
        "failure_distribution": failure_distribution,
        "regression_detected": regressed,
        "accuracy_breakdown": breakdown,
        "expected_calibration_error": ece,
        "brier_score": brier
    }
    
    os.makedirs("report", exist_ok=True)
    with open("report/final_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    print(f"Evaluation Complete! Accuracy: {accuracy:.2%} | Hallucination Rate: {hallucination_rate:.2%}")
    print(f"Expected Calibration Error (ECE): {ece:.4f} | Brier Score: {brier:.4f}")

if __name__ == "__main__":
    run_evaluation()

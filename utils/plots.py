import matplotlib.pyplot as plt
import numpy as np

def plot_calibration_curve(confidences, accuracies, output_path="report/calibration_curve.png"):
    """
    Plots a calibration curve: Actual Accuracy vs Predicted Confidence.
    """
    # Define bins
    bins = np.linspace(0, 1, 6) # 5 bins: 0-0.2, 0.2-0.4, ...
    bin_indices = np.digitize(confidences, bins) - 1
    
    bin_accuracies = []
    bin_confidences = []
    
    for i in range(len(bins)-1):
        # Indices of items in this bin
        in_bin = (bin_indices == i)
        if np.any(in_bin):
            bin_accuracies.append(np.mean(np.array(accuracies)[in_bin]))
            bin_confidences.append(np.mean(np.array(confidences)[in_bin]))
        else:
            bin_accuracies.append(0.0)
            bin_confidences.append((bins[i] + bins[i+1]) / 2)
            
    plt.figure(figsize=(8, 6))
    plt.plot(bin_confidences, bin_accuracies, marker='o', linestyle='-', label='Model Calibration')
    plt.plot([0, 1], [0, 1], linestyle='--', color='gray', label='Perfect Calibration')
    
    plt.title('Calibration Curve')
    plt.xlabel('Predicted Confidence')
    plt.ylabel('Actual Accuracy')
    plt.legend()
    plt.grid(True)
    plt.savefig(output_path)
    plt.close()
    
    return output_path

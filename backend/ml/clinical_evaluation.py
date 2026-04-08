"""
Clinical Evaluation Framework

Provides clinically-relevant metrics beyond standard ML metrics:
- Sensitivity/Specificity at clinically meaningful thresholds
- Positive/Negative Predictive Values
- Number Needed to Evaluate (NNE)
- Clinical utility curves
- Alert burden analysis
- Early warning performance
"""

import numpy as np
from sklearn.metrics import (
    confusion_matrix, precision_recall_curve,
    roc_curve, auc
)
from typing import Dict, List, Tuple
import json


class ClinicalEvaluator:
    """
    Evaluate model from clinical perspective
    """
    
    def __init__(self):
        self.clinical_thresholds = {
            'high_sensitivity': 0.3,  # Catch most cases (screening)
            'balanced': 0.5,           # Balance sensitivity/specificity
            'high_specificity': 0.7    # Reduce false alarms
        }
    
    def calculate_clinical_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        threshold: float = 0.5
    ) -> Dict:
        """
        Calculate clinical performance metrics at a specific threshold
        
        Returns:
            Dictionary with sensitivity, specificity, PPV, NPV, etc.
        """
        y_pred_binary = (y_pred >= threshold).astype(int)
        
        # Confusion matrix
        tn, fp, fn, tp = confusion_matrix(y_true, y_pred_binary).ravel()
        
        # Basic metrics
        sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0
        specificity = tn / (tn + fp) if (tn + fp) > 0 else 0
        ppv = tp / (tp + fp) if (tp + fp) > 0 else 0  # Positive Predictive Value
        npv = tn / (tn + fn) if (tn + fn) > 0 else 0  # Negative Predictive Value
        
        # F1 score
        f1 = 2 * (ppv * sensitivity) / (ppv + sensitivity) if (ppv + sensitivity) > 0 else 0
        
        # Accuracy
        accuracy = (tp + tn) / (tp + tn + fp + fn)
        
        # Number Needed to Evaluate (NNE)
        # How many alerts needed to find one true positive
        nne = (tp + fp) / tp if tp > 0 else float('inf')
        
        # Alert burden (percentage of patients flagged)
        alert_rate = (tp + fp) / (tp + tn + fp + fn)
        
        return {
            'threshold': float(threshold),
            'sensitivity': float(sensitivity),
            'specificity': float(specificity),
            'ppv': float(ppv),
            'npv': float(npv),
            'f1_score': float(f1),
            'accuracy': float(accuracy),
            'true_positives': int(tp),
            'true_negatives': int(tn),
            'false_positives': int(fp),
            'false_negatives': int(fn),
            'number_needed_to_evaluate': float(nne),
            'alert_rate': float(alert_rate)
        }
    
    def find_optimal_threshold(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        criterion: str = 'youden'
    ) -> Tuple[float, Dict]:
        """
        Find optimal operating threshold
        
        Args:
            criterion: 'youden' (max sensitivity+specificity-1)
                      'f1' (max F1 score)
                      'ppv80' (maximize sensitivity while PPV >= 0.8)
        
        Returns:
            (optimal_threshold, metrics_at_threshold)
        """
        fpr, tpr, thresholds = roc_curve(y_true, y_pred)
        
        if criterion == 'youden':
            # Youden's J statistic
            j_scores = tpr - fpr
            optimal_idx = np.argmax(j_scores)
            optimal_threshold = thresholds[optimal_idx]
        
        elif criterion == 'f1':
            # Maximum F1 score
            precision, recall, thresholds_pr = precision_recall_curve(y_true, y_pred)
            f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
            optimal_idx = np.argmax(f1_scores)
            optimal_threshold = thresholds_pr[optimal_idx]
        
        elif criterion == 'ppv80':
            # Max sensitivity while maintaining PPV >= 0.8
            precision, recall, thresholds_pr = precision_recall_curve(y_true, y_pred)
            valid_indices = precision >= 0.8
            if valid_indices.any():
                optimal_idx = np.argmax(recall[valid_indices])
                optimal_threshold = thresholds_pr[valid_indices][optimal_idx]
            else:
                optimal_threshold = 0.5
        
        else:
            optimal_threshold = 0.5
        
        metrics = self.calculate_clinical_metrics(y_true, y_pred, optimal_threshold)
        
        return optimal_threshold, metrics
    
    def early_warning_analysis(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        time_to_event: np.ndarray,
        warning_windows: List[int] = [24, 48, 72]
    ) -> Dict:
        """
        Analyze early warning performance
        
        Args:
            time_to_event: Hours until deterioration (for positive cases)
            warning_windows: Warning windows to evaluate (hours)
        
        Returns:
            Performance at different warning windows
        """
        results = {}
        
        for window in warning_windows:
            # Cases where we have enough time to intervene
            early_cases = (time_to_event >= window) | (y_true == 0)
            
            if early_cases.sum() > 0:
                metrics = self.calculate_clinical_metrics(
                    y_true[early_cases],
                    y_pred[early_cases],
                    threshold=0.5
                )
                results[f'{window}h_window'] = metrics
        
        return results
    
    def clinical_utility_curve(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        cost_fp: float = 1.0,
        cost_fn: float = 10.0
    ) -> Dict:
        """
        Calculate clinical utility at different thresholds
        
        Clinical utility = (TP * benefit) - (FP * cost_fp) - (FN * cost_fn)
        
        Args:
            cost_fp: Cost of false positive (unnecessary intervention)
            cost_fn: Cost of false negative (missed deterioration)
        
        Returns:
            Utility curve data
        """
        thresholds = np.linspace(0, 1, 100)
        utilities = []
        
        for threshold in thresholds:
            y_pred_binary = (y_pred >= threshold).astype(int)
            tn, fp, fn, tp = confusion_matrix(y_true, y_pred_binary).ravel()
            
            # Utility = benefit of catching cases - cost of false alarms - cost of misses
            utility = tp - (fp * cost_fp) - (fn * cost_fn)
            utilities.append(utility)
        
        utilities = np.array(utilities)
        optimal_idx = np.argmax(utilities)
        
        return {
            'thresholds': thresholds.tolist(),
            'utilities': utilities.tolist(),
            'optimal_threshold': float(thresholds[optimal_idx]),
            'max_utility': float(utilities[optimal_idx]),
            'cost_fp': cost_fp,
            'cost_fn': cost_fn
        }
    
    def comprehensive_clinical_evaluation(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        model_name: str = "Model"
    ) -> Dict:
        """
        Complete clinical evaluation report
        """
        report = {
            'model_name': model_name,
            'dataset_stats': {
                'n_samples': len(y_true),
                'n_positive': int(y_true.sum()),
                'prevalence': float(y_true.mean())
            }
        }
        
        # 1. Performance at standard thresholds
        report['threshold_analysis'] = {}
        for name, threshold in self.clinical_thresholds.items():
            report['threshold_analysis'][name] = self.calculate_clinical_metrics(
                y_true, y_pred, threshold
            )
        
        # 2. Optimal thresholds
        report['optimal_thresholds'] = {}
        for criterion in ['youden', 'f1', 'ppv80']:
            threshold, metrics = self.find_optimal_threshold(y_true, y_pred, criterion)
            report['optimal_thresholds'][criterion] = {
                'threshold': threshold,
                'metrics': metrics
            }
        
        # 3. Clinical utility
        report['clinical_utility'] = self.clinical_utility_curve(
            y_true, y_pred,
            cost_fp=1.0,
            cost_fn=10.0  # Missing deterioration is 10x worse than false alarm
        )
        
        # 4. Alert burden analysis
        report['alert_burden'] = {
            'low_threshold_0.3': self.calculate_clinical_metrics(y_true, y_pred, 0.3)['alert_rate'],
            'medium_threshold_0.5': self.calculate_clinical_metrics(y_true, y_pred, 0.5)['alert_rate'],
            'high_threshold_0.7': self.calculate_clinical_metrics(y_true, y_pred, 0.7)['alert_rate']
        }
        
        return report


def generate_clinical_report(
    y_true: np.ndarray,
    model_predictions: Dict[str, np.ndarray],
    save_path: str = 'models/clinical_evaluation.json'
) -> Dict:
    """
    Generate comprehensive clinical evaluation report
    
    Args:
        y_true: True labels
        model_predictions: Dictionary of {model_name: predictions}
        save_path: Where to save report
    
    Returns:
        Clinical evaluation report
    """
    evaluator = ClinicalEvaluator()
    
    full_report = {
        'models': {},
        'comparison': {}
    }
    
    print("\n" + "=" * 70)
    print("CLINICAL EVALUATION")
    print("=" * 70)
    
    # Evaluate each model
    for model_name, y_pred in model_predictions.items():
        print(f"\n📋 Evaluating {model_name}...")
        report = evaluator.comprehensive_clinical_evaluation(y_true, y_pred, model_name)
        full_report['models'][model_name] = report
        
        # Print summary
        balanced = report['threshold_analysis']['balanced']
        print(f"  At balanced threshold (0.5):")
        print(f"    Sensitivity: {balanced['sensitivity']:.3f}")
        print(f"    Specificity: {balanced['specificity']:.3f}")
        print(f"    PPV: {balanced['ppv']:.3f}")
        print(f"    Alert Rate: {balanced['alert_rate']:.1%}")
    
    # Comparison summary
    print("\n" + "=" * 70)
    print("CLINICAL COMPARISON SUMMARY")
    print("=" * 70)
    
    comparison_table = []
    for model_name in model_predictions.keys():
        balanced = full_report['models'][model_name]['threshold_analysis']['balanced']
        comparison_table.append({
            'model': model_name,
            'sensitivity': balanced['sensitivity'],
            'specificity': balanced['specificity'],
            'ppv': balanced['ppv'],
            'f1': balanced['f1_score'],
            'alert_rate': balanced['alert_rate']
        })
    
    full_report['comparison']['summary_table'] = comparison_table
    
    # Print comparison
    print(f"\n{'Model':<25} {'Sens':<8} {'Spec':<8} {'PPV':<8} {'F1':<8} {'Alert%':<8}")
    print("-" * 70)
    for row in comparison_table:
        print(f"{row['model']:<25} {row['sensitivity']:<8.3f} {row['specificity']:<8.3f} "
              f"{row['ppv']:<8.3f} {row['f1']:<8.3f} {row['alert_rate']:<8.1%}")
    
    # Save report
    with open(save_path, 'w') as f:
        json.dump(full_report, f, indent=2)
    
    print(f"\n✅ Clinical evaluation report saved to: {save_path}")
    
    return full_report


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)
    
    # Simulate data
    n_samples = 500
    y_true = np.random.binomial(1, 0.2, n_samples)
    
    predictions = {
        'Baseline Model': np.random.beta(2, 5, n_samples),
        'Our Model': np.random.beta(3, 2, n_samples) * 0.7 + y_true * 0.3
    }
    
    # Generate report
    report = generate_clinical_report(y_true, predictions)

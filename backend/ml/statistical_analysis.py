"""
Statistical Analysis and Significance Testing

Provides rigorous statistical validation for IEEE Q1 publication:
- Bootstrap confidence intervals
- Statistical significance tests (p-values)
- Cross-validation
- Calibration analysis
- McNemar's test for model comparison
"""

import numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.calibration import calibration_curve
from sklearn.model_selection import StratifiedKFold
from typing import Dict, List, Tuple
import json


class StatisticalAnalyzer:
    """
    Comprehensive statistical analysis for model validation
    """
    
    def __init__(self, n_bootstrap=1000, alpha=0.05):
        """
        Args:
            n_bootstrap: Number of bootstrap samples
            alpha: Significance level (default 0.05 for 95% CI)
        """
        self.n_bootstrap = n_bootstrap
        self.alpha = alpha
    
    def bootstrap_ci(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        metric_fn,
        metric_name: str = "AUROC"
    ) -> Dict:
        """
        Calculate bootstrap confidence intervals for a metric
        
        Args:
            y_true: True labels
            y_pred: Predicted probabilities
            metric_fn: Metric function (e.g., roc_auc_score)
            metric_name: Name of metric
        
        Returns:
            Dictionary with point estimate and confidence interval
        """
        n = len(y_true)
        bootstrap_scores = []
        
        np.random.seed(42)
        for _ in range(self.n_bootstrap):
            # Resample with replacement
            indices = np.random.choice(n, size=n, replace=True)
            
            # Skip if only one class in sample
            if len(np.unique(y_true[indices])) < 2:
                continue
            
            score = metric_fn(y_true[indices], y_pred[indices])
            bootstrap_scores.append(score)
        
        bootstrap_scores = np.array(bootstrap_scores)
        
        # Calculate percentile confidence interval
        lower = np.percentile(bootstrap_scores, (self.alpha / 2) * 100)
        upper = np.percentile(bootstrap_scores, (1 - self.alpha / 2) * 100)
        point_estimate = metric_fn(y_true, y_pred)
        
        return {
            'metric': metric_name,
            'point_estimate': float(point_estimate),
            'ci_lower': float(lower),
            'ci_upper': float(upper),
            'ci_width': float(upper - lower),
            'std': float(bootstrap_scores.std())
        }
    
    def compare_models(
        self,
        y_true: np.ndarray,
        y_pred_1: np.ndarray,
        y_pred_2: np.ndarray,
        model_1_name: str = "Model 1",
        model_2_name: str = "Model 2"
    ) -> Dict:
        """
        Statistical comparison of two models using bootstrap
        
        Returns:
            Dictionary with comparison results and p-value
        """
        n = len(y_true)
        differences = []
        
        np.random.seed(42)
        for _ in range(self.n_bootstrap):
            indices = np.random.choice(n, size=n, replace=True)
            
            if len(np.unique(y_true[indices])) < 2:
                continue
            
            auroc_1 = roc_auc_score(y_true[indices], y_pred_1[indices])
            auroc_2 = roc_auc_score(y_true[indices], y_pred_2[indices])
            
            differences.append(auroc_2 - auroc_1)
        
        differences = np.array(differences)
        
        # Calculate p-value (two-tailed test)
        p_value = np.mean(differences <= 0) * 2
        p_value = min(p_value, 1.0)
        
        # Point estimates
        auroc_1 = roc_auc_score(y_true, y_pred_1)
        auroc_2 = roc_auc_score(y_true, y_pred_2)
        
        return {
            'model_1': model_1_name,
            'model_2': model_2_name,
            'auroc_1': float(auroc_1),
            'auroc_2': float(auroc_2),
            'difference': float(auroc_2 - auroc_1),
            'p_value': float(p_value),
            'significant': bool(p_value < self.alpha),
            'ci_difference_lower': float(np.percentile(differences, 2.5)),
            'ci_difference_upper': float(np.percentile(differences, 97.5))
        }
    
    def mcnemar_test(
        self,
        y_true: np.ndarray,
        y_pred_1: np.ndarray,
        y_pred_2: np.ndarray,
        threshold: float = 0.5
    ) -> Dict:
        """
        McNemar's test for comparing two classifiers
        
        Tests if the two models make significantly different errors
        """
        # Convert probabilities to binary predictions
        pred_1_binary = (y_pred_1 >= threshold).astype(int)
        pred_2_binary = (y_pred_2 >= threshold).astype(int)
        
        # Create contingency table
        # n01: Model 1 wrong, Model 2 correct
        # n10: Model 1 correct, Model 2 wrong
        n01 = np.sum((pred_1_binary != y_true) & (pred_2_binary == y_true))
        n10 = np.sum((pred_1_binary == y_true) & (pred_2_binary != y_true))
        
        # McNemar's test statistic (with continuity correction)
        if n01 + n10 == 0:
            statistic = 0
            p_value = 1.0
        else:
            statistic = ((abs(n01 - n10) - 1) ** 2) / (n01 + n10)
            p_value = 1 - stats.chi2.cdf(statistic, df=1)
        
        return {
            'test': 'McNemar',
            'n01_model1_wrong_model2_correct': int(n01),
            'n10_model1_correct_model2_wrong': int(n10),
            'statistic': float(statistic),
            'p_value': float(p_value),
            'significant': bool(p_value < self.alpha)
        }
    
    def calibration_analysis(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        n_bins: int = 10
    ) -> Dict:
        """
        Analyze model calibration
        
        Returns:
            Calibration metrics and curve data
        """
        # Calculate calibration curve
        prob_true, prob_pred = calibration_curve(
            y_true, y_pred, n_bins=n_bins, strategy='uniform'
        )
        
        # Expected Calibration Error (ECE)
        # Handle empty bins which calibration_curve excludes
        bin_counts, _ = np.histogram(y_pred, bins=n_bins, range=(0, 1))
        non_empty = bin_counts > 0
        bin_weights = bin_counts[non_empty] / len(y_pred)
        
        ece = np.sum(bin_weights * np.abs(prob_true - prob_pred))
        
        # Maximum Calibration Error (MCE)
        if len(prob_true) > 0:
            mce = np.max(np.abs(prob_true - prob_pred))
        else:
            mce = 0.0
        
        # Brier score
        brier = brier_score_loss(y_true, y_pred)
        
        return {
            'expected_calibration_error': float(ece),
            'maximum_calibration_error': float(mce),
            'brier_score': float(brier),
            'calibration_curve': {
                'predicted_probabilities': prob_pred.tolist(),
                'true_frequencies': prob_true.tolist()
            },
            'is_well_calibrated': bool(ece < 0.1)  # Threshold for good calibration
        }
    
    def cross_validation_analysis(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model_fn,
        n_folds: int = 5
    ) -> Dict:
        """
        K-fold cross-validation with statistical analysis
        
        Args:
            X: Features
            y: Labels
            model_fn: Function that returns a trained model
            n_folds: Number of folds
        
        Returns:
            Cross-validation results with confidence intervals
        """
        skf = StratifiedKFold(n_splits=n_folds, shuffle=True, random_state=42)
        
        fold_aurocs = []
        fold_auprcs = []
        
        for fold, (train_idx, val_idx) in enumerate(skf.split(X, y)):
            X_train, X_val = X[train_idx], X[val_idx]
            y_train, y_val = y[train_idx], y[val_idx]
            
            # Train model
            model = model_fn(X_train, y_train)
            
            # Predict
            y_pred = model.predict(X_val)
            
            # Metrics
            auroc = roc_auc_score(y_val, y_pred)
            auprc = average_precision_score(y_val, y_pred)
            
            fold_aurocs.append(auroc)
            fold_auprcs.append(auprc)
        
        fold_aurocs = np.array(fold_aurocs)
        fold_auprcs = np.array(fold_auprcs)
        
        return {
            'n_folds': n_folds,
            'auroc': {
                'mean': float(fold_aurocs.mean()),
                'std': float(fold_aurocs.std()),
                'ci_lower': float(fold_aurocs.mean() - 1.96 * fold_aurocs.std()),
                'ci_upper': float(fold_aurocs.mean() + 1.96 * fold_aurocs.std()),
                'folds': fold_aurocs.tolist()
            },
            'auprc': {
                'mean': float(fold_auprcs.mean()),
                'std': float(fold_auprcs.std()),
                'ci_lower': float(fold_auprcs.mean() - 1.96 * fold_auprcs.std()),
                'ci_upper': float(fold_auprcs.mean() + 1.96 * fold_auprcs.std()),
                'folds': fold_auprcs.tolist()
            }
        }
    
    def comprehensive_analysis(
        self,
        y_true: np.ndarray,
        predictions: Dict[str, np.ndarray]
    ) -> Dict:
        """
        Run comprehensive statistical analysis on all models
        
        Args:
            y_true: True labels
            predictions: Dictionary of {model_name: predictions}
        
        Returns:
            Complete statistical analysis report
        """
        report = {
            'bootstrap_confidence_intervals': {},
            'pairwise_comparisons': {},
            'calibration': {},
            'summary': {}
        }
        
        model_names = list(predictions.keys())
        
        # 1. Bootstrap CIs for each model
        print("\n📊 Calculating bootstrap confidence intervals...")
        for model_name, y_pred in predictions.items():
            report['bootstrap_confidence_intervals'][model_name] = {
                'auroc': self.bootstrap_ci(y_true, y_pred, roc_auc_score, 'AUROC'),
                'auprc': self.bootstrap_ci(y_true, y_pred, average_precision_score, 'AUPRC')
            }
        
        # 2. Pairwise comparisons
        print("\n📊 Performing pairwise statistical comparisons...")
        for i, model_1 in enumerate(model_names):
            for model_2 in model_names[i+1:]:
                key = f"{model_1} vs {model_2}"
                report['pairwise_comparisons'][key] = self.compare_models(
                    y_true, predictions[model_1], predictions[model_2],
                    model_1, model_2
                )
        
        # 3. Calibration analysis
        print("\n📊 Analyzing model calibration...")
        for model_name, y_pred in predictions.items():
            report['calibration'][model_name] = self.calibration_analysis(y_true, y_pred)
        
        # 4. Summary statistics
        print("\n📊 Generating summary statistics...")
        for model_name, y_pred in predictions.items():
            auroc = roc_auc_score(y_true, y_pred)
            auprc = average_precision_score(y_true, y_pred)
            brier = brier_score_loss(y_true, y_pred)
            
            report['summary'][model_name] = {
                'auroc': float(auroc),
                'auprc': float(auprc),
                'brier_score': float(brier),
                'n_samples': len(y_true),
                'n_positive': int(y_true.sum()),
                'prevalence': float(y_true.mean())
            }
        
        return report


def generate_statistical_report(
    test_samples: List[Dict],
    model_predictions: Dict[str, np.ndarray],
    save_path: str = 'models/statistical_analysis.json'
):
    """
    Generate complete statistical analysis report for publication
    
    Args:
        test_samples: Test dataset
        model_predictions: Dictionary of {model_name: predictions}
        save_path: Where to save the report
    """
    # Extract labels
    y_true = np.array([s['label'] for s in test_samples])
    
    # Run analysis
    analyzer = StatisticalAnalyzer(n_bootstrap=1000, alpha=0.05)
    report = analyzer.comprehensive_analysis(y_true, model_predictions)
    
    # Save report
    with open(save_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n✅ Statistical analysis report saved to: {save_path}")
    
    # Print summary
    print("\n" + "=" * 70)
    print("STATISTICAL ANALYSIS SUMMARY")
    print("=" * 70)
    
    for model_name in model_predictions.keys():
        auroc_ci = report['bootstrap_confidence_intervals'][model_name]['auroc']
        print(f"\n{model_name}:")
        print(f"  AUROC: {auroc_ci['point_estimate']:.4f} "
              f"[95% CI: {auroc_ci['ci_lower']:.4f}-{auroc_ci['ci_upper']:.4f}]")
        
        calib = report['calibration'][model_name]
        print(f"  Calibration: ECE = {calib['expected_calibration_error']:.4f} "
              f"({'Well-calibrated' if calib['is_well_calibrated'] else 'Needs improvement'})")
    
    print("\n" + "=" * 70)
    
    return report


if __name__ == "__main__":
    # Example usage
    np.random.seed(42)
    
    # Simulate test data
    n_samples = 500
    y_true = np.random.binomial(1, 0.2, n_samples)
    
    # Simulate predictions from different models
    predictions = {
        'Baseline': np.random.beta(2, 5, n_samples),
        'Our Model': np.random.beta(3, 2, n_samples) * 0.8 + y_true * 0.2
    }
    
    # Run analysis
    analyzer = StatisticalAnalyzer()
    report = analyzer.comprehensive_analysis(y_true, predictions)
    
    print(json.dumps(report, indent=2))

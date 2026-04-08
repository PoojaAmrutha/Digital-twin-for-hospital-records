"""
Baseline Models for Comparative Analysis

Implements simple baseline models to demonstrate the superiority
of the Multi-Modal Temporal Fusion Network.

Baselines:
1. Logistic Regression (on latest vitals only)
2. Random Forest (on aggregated features)
3. Simple LSTM (no attention, no text, no personalization)
"""

import numpy as np
import torch
import torch.nn as nn
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
import joblib
from typing import Dict, List, Tuple
import json


class LogisticRegressionBaseline:
    """
    Baseline 1: Logistic Regression on latest vitals only
    
    Uses only the most recent vital signs (no temporal information)
    """
    
    def __init__(self):
        self.model = LogisticRegression(max_iter=1000, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, samples: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Extract latest vitals + static features"""
        X = []
        y = []
        
        for sample in samples:
            # Latest vitals (last time point)
            latest_vitals = sample['vitals_sequence'][-1]  # (4,)
            
            # Static features
            static = sample['static_features']  # (10,)
            
            # Concatenate
            features = np.concatenate([latest_vitals, static])
            X.append(features)
            y.append(sample['label'])
        
        return np.array(X), np.array(y)
    
    def train(self, train_samples: List[Dict]):
        """Train logistic regression"""
        X_train, y_train = self.prepare_features(train_samples)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        print(f"✓ Logistic Regression trained on {len(train_samples)} samples")
    
    def predict(self, test_samples: List[Dict]) -> np.ndarray:
        """Predict probabilities"""
        X_test, _ = self.prepare_features(test_samples)
        X_test_scaled = self.scaler.transform(X_test)
        return self.model.predict_proba(X_test_scaled)[:, 1]
    
    def evaluate(self, test_samples: List[Dict]) -> Dict:
        """Evaluate on test set"""
        X_test, y_test = self.prepare_features(test_samples)
        X_test_scaled = self.scaler.transform(X_test)
        
        y_pred = self.model.predict_proba(X_test_scaled)[:, 1]
        
        return {
            'model': 'Logistic Regression',
            'auroc': roc_auc_score(y_test, y_pred),
            'auprc': average_precision_score(y_test, y_pred),
            'brier_score': brier_score_loss(y_test, y_pred)
        }


class RandomForestBaseline:
    """
    Baseline 2: Random Forest on aggregated temporal features
    
    Uses statistical aggregations (mean, std, min, max) over time
    """
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def prepare_features(self, samples: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Extract aggregated temporal features"""
        X = []
        y = []
        
        for sample in samples:
            vitals_seq = sample['vitals_sequence']  # (48, 4)
            
            # Aggregate statistics over time
            mean_vitals = vitals_seq.mean(axis=0)  # (4,)
            std_vitals = vitals_seq.std(axis=0)    # (4,)
            min_vitals = vitals_seq.min(axis=0)    # (4,)
            max_vitals = vitals_seq.max(axis=0)    # (4,)
            
            # Trend (difference between last and first)
            trend = vitals_seq[-1] - vitals_seq[0]  # (4,)
            
            # Static features
            static = sample['static_features']  # (10,)
            
            # Concatenate all
            features = np.concatenate([
                mean_vitals, std_vitals, min_vitals, max_vitals, trend, static
            ])
            
            X.append(features)
            y.append(sample['label'])
        
        return np.array(X), np.array(y)
    
    def train(self, train_samples: List[Dict]):
        """Train random forest"""
        X_train, y_train = self.prepare_features(train_samples)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        
        # Train
        self.model.fit(X_train_scaled, y_train)
        self.is_trained = True
        
        print(f"✓ Random Forest trained on {len(train_samples)} samples")
    
    def predict(self, test_samples: List[Dict]) -> np.ndarray:
        """Predict probabilities"""
        X_test, _ = self.prepare_features(test_samples)
        X_test_scaled = self.scaler.transform(X_test)
        return self.model.predict_proba(X_test_scaled)[:, 1]
    
    def evaluate(self, test_samples: List[Dict]) -> Dict:
        """Evaluate on test set"""
        X_test, y_test = self.prepare_features(test_samples)
        X_test_scaled = self.scaler.transform(X_test)
        
        y_pred = self.model.predict_proba(X_test_scaled)[:, 1]
        
        return {
            'model': 'Random Forest',
            'auroc': roc_auc_score(y_test, y_pred),
            'auprc': average_precision_score(y_test, y_pred),
            'brier_score': brier_score_loss(y_test, y_pred)
        }


class SimpleLSTMBaseline(nn.Module):
    """
    Baseline 3: Simple LSTM without attention, text, or personalization
    
    Uses only temporal LSTM on vitals
    """
    
    def __init__(self, input_dim=4, hidden_dim=64, dropout=0.3):
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            dropout=dropout
        )
        
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        """
        Args:
            x: (batch, seq_len, input_dim)
        Returns:
            predictions: (batch, 1)
        """
        # LSTM
        lstm_out, (h_n, c_n) = self.lstm(x)
        
        # Use last hidden state
        last_hidden = h_n[-1]  # (batch, hidden_dim)
        
        # Predict
        output = self.fc(last_hidden)
        
        return output


def train_baseline_models(
    train_samples: List[Dict],
    val_samples: List[Dict],
    test_samples: List[Dict],
    save_dir: str = 'models/baselines'
):
    """
    Train all baseline models and save results
    
    Returns:
        Dictionary with all baseline results
    """
    import os
    os.makedirs(save_dir, exist_ok=True)
    
    results = {}
    
    print("=" * 70)
    print("TRAINING BASELINE MODELS FOR COMPARATIVE ANALYSIS")
    print("=" * 70)
    
    # 1. Logistic Regression
    print("\n[1/3] Training Logistic Regression...")
    lr_model = LogisticRegressionBaseline()
    lr_model.train(train_samples)
    lr_results = lr_model.evaluate(test_samples)
    results['logistic_regression'] = lr_results
    
    joblib.dump(lr_model, f'{save_dir}/logistic_regression.pkl')
    print(f"  AUROC: {lr_results['auroc']:.4f}")
    print(f"  AUPRC: {lr_results['auprc']:.4f}")
    
    # 2. Random Forest
    print("\n[2/3] Training Random Forest...")
    rf_model = RandomForestBaseline()
    rf_model.train(train_samples)
    rf_results = rf_model.evaluate(test_samples)
    results['random_forest'] = rf_results
    
    joblib.dump(rf_model, f'{save_dir}/random_forest.pkl')
    print(f"  AUROC: {rf_results['auroc']:.4f}")
    print(f"  AUPRC: {rf_results['auprc']:.4f}")
    
    # 3. Simple LSTM
    print("\n[3/3] Training Simple LSTM...")
    from torch.utils.data import DataLoader
    from model_trainer import DeteriorationDataset
    
    # Create simple dataset (vitals only)
    class SimpleLSTMDataset:
        def __init__(self, samples):
            self.samples = samples
        
        def __len__(self):
            return len(self.samples)
        
        def __getitem__(self, idx):
            sample = self.samples[idx]
            return {
                'vitals': torch.FloatTensor(sample['vitals_sequence']),
                'label': torch.FloatTensor([sample['label']])
            }
    
    train_dataset = SimpleLSTMDataset(train_samples)
    val_dataset = SimpleLSTMDataset(val_samples)
    test_dataset = SimpleLSTMDataset(test_samples)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32)
    test_loader = DataLoader(test_dataset, batch_size=32)
    
    # Train LSTM
    lstm_model = SimpleLSTMBaseline()
    optimizer = torch.optim.Adam(lstm_model.parameters(), lr=0.001)
    criterion = nn.BCELoss()
    
    best_auroc = 0
    for epoch in range(20):
        lstm_model.train()
        for batch in train_loader:
            vitals = batch['vitals']
            labels = batch['label']
            
            optimizer.zero_grad()
            outputs = lstm_model(vitals)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
        
        # Validate
        lstm_model.eval()
        all_preds = []
        all_labels = []
        with torch.no_grad():
            for batch in val_loader:
                vitals = batch['vitals']
                labels = batch['label']
                outputs = lstm_model(vitals)
                all_preds.extend(outputs.numpy())
                all_labels.extend(labels.numpy())
        
        auroc = roc_auc_score(all_labels, all_preds)
        if auroc > best_auroc:
            best_auroc = auroc
            torch.save(lstm_model.state_dict(), f'{save_dir}/simple_lstm.pt')
    
    # Test LSTM
    lstm_model.eval()
    all_preds = []
    all_labels = []
    with torch.no_grad():
        for batch in test_loader:
            vitals = batch['vitals']
            labels = batch['label']
            outputs = lstm_model(vitals)
            all_preds.extend(outputs.numpy())
            all_labels.extend(labels.numpy())
    
    lstm_results = {
        'model': 'Simple LSTM',
        'auroc': roc_auc_score(all_labels, all_preds),
        'auprc': average_precision_score(all_labels, all_preds),
        'brier_score': brier_score_loss(all_labels, all_preds)
    }
    results['simple_lstm'] = lstm_results
    
    print(f"  AUROC: {lstm_results['auroc']:.4f}")
    print(f"  AUPRC: {lstm_results['auprc']:.4f}")
    
    # Save all results
    with open(f'{save_dir}/baseline_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("BASELINE TRAINING COMPLETE")
    print("=" * 70)
    
    return results


if __name__ == "__main__":
    # Load data
    from synthetic_data_generator import SyntheticPatientGenerator
    
    print("Generating dataset...")
    generator = SyntheticPatientGenerator(random_seed=42)
    samples, labels = generator.generate_dataset(n_samples=1000)
    
    # Split
    n_train = int(0.7 * len(samples))
    n_val = int(0.15 * len(samples))
    
    train_samples = samples[:n_train]
    val_samples = samples[n_train:n_train+n_val]
    test_samples = samples[n_train+n_val:]
    
    # Train baselines
    results = train_baseline_models(train_samples, val_samples, test_samples)
    
    print("\n📊 BASELINE RESULTS SUMMARY:")
    for model_name, metrics in results.items():
        print(f"\n{metrics['model']}:")
        print(f"  AUROC: {metrics['auroc']:.4f}")
        print(f"  AUPRC: {metrics['auprc']:.4f}")

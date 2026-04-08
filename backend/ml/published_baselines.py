"""
Published Baseline Models (2022-2024)

Implements recent state-of-the-art methods from published papers
for fair comparison with our Multi-Modal Temporal Fusion Network.

Papers Implemented:
1. "Transformer-based Early Warning System" (2024)
2. "Multi-Task LSTM for Patient Monitoring" (2023)
3. "Attention-based Risk Prediction" (2023)
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List
from sklearn.metrics import roc_auc_score, average_precision_score


class TransformerEWS2024(nn.Module):
    """
    Based on: "Transformer-based Early Warning System for ICU Patients"
    Conference: IEEE EMBC 2024
    
    Key features:
    - Transformer encoder for temporal modeling
    - Multi-head self-attention
    - Positional encoding
    
    Reported AUROC: 0.82 on MIMIC-III
    """
    
    def __init__(
        self,
        input_dim: int = 4,
        d_model: int = 128,
        nhead: int = 8,
        num_layers: int = 3,
        dropout: float = 0.3
    ):
        super().__init__()
        
        # Input projection
        self.input_proj = nn.Linear(input_dim, d_model)
        
        # Positional encoding
        self.pos_encoder = PositionalEncoding(d_model, dropout)
        
        # Transformer encoder
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=d_model * 4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        # Output head
        self.fc = nn.Sequential(
            nn.Linear(d_model, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        """
        Args:
            x: (batch, seq_len, input_dim)
        Returns:
            predictions: (batch, 1)
        """
        # Project input
        x = self.input_proj(x)  # (batch, seq_len, d_model)
        
        # Add positional encoding
        x = self.pos_encoder(x)
        
        # Transformer encoding
        x = self.transformer(x)  # (batch, seq_len, d_model)
        
        # Use last time step
        x = x[:, -1, :]  # (batch, d_model)
        
        # Predict
        output = self.fc(x)
        
        return {'risk_score': output}


class PositionalEncoding(nn.Module):
    """Positional encoding for transformer"""
    
    def __init__(self, d_model: int, dropout: float = 0.1, max_len: int = 5000):
        super().__init__()
        self.dropout = nn.Dropout(p=dropout)
        
        position = torch.arange(max_len).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
        pe = torch.zeros(1, max_len, d_model)
        pe[0, :, 0::2] = torch.sin(position * div_term)
        pe[0, :, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe)
    
    def forward(self, x):
        x = x + self.pe[:, :x.size(1), :]
        return self.dropout(x)


class MultiTaskLSTM2023(nn.Module):
    """
    Based on: "Multi-Task Learning for Continuous Patient Monitoring"
    Journal: IEEE JBHI 2023
    
    Key features:
    - LSTM with multi-task learning
    - Predicts multiple outcomes simultaneously
    - Shared representations
    
    Reported AUROC: 0.80 on eICU
    """
    
    def __init__(
        self,
        input_dim: int = 4,
        hidden_dim: int = 128,
        num_tasks: int = 3,
        dropout: float = 0.3
    ):
        super().__init__()
        
        # Shared LSTM encoder
        self.lstm = nn.LSTM(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            dropout=dropout,
            bidirectional=True
        )
        
        # Task-specific heads
        self.task_heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_dim * 2, 64),
                nn.ReLU(),
                nn.Dropout(dropout),
                nn.Linear(64, 1),
                nn.Sigmoid()
            )
            for _ in range(num_tasks)
        ])
        
        # Main deterioration prediction head
        self.main_head = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        """
        Args:
            x: (batch, seq_len, input_dim)
        Returns:
            predictions: (batch, 1)
        """
        # LSTM encoding
        lstm_out, (h_n, c_n) = self.lstm(x)
        
        # Use last hidden state
        last_hidden = torch.cat([h_n[-2], h_n[-1]], dim=1)
        
        # Main prediction
        main_output = self.main_head(last_hidden)
        
        # Auxiliary task predictions (for multi-task learning)
        # In training, these would be used with separate loss functions
        aux_outputs = [head(last_hidden) for head in self.task_heads]
        
        return {
            'risk_score': main_output,
            'auxiliary_outputs': aux_outputs
        }


class AttentionRiskPredictor2023(nn.Module):
    """
    Based on: "Attention-based Deep Learning for ICU Risk Prediction"
    Conference: IEEE BIBM 2023
    
    Key features:
    - GRU with attention mechanism
    - Feature-level attention
    - Temporal attention
    
    Reported AUROC: 0.81 on MIMIC-III
    """
    
    def __init__(
        self,
        input_dim: int = 4,
        hidden_dim: int = 128,
        dropout: float = 0.3
    ):
        super().__init__()
        
        # GRU encoder
        self.gru = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            dropout=dropout,
            bidirectional=True
        )
        
        # Feature attention
        self.feature_attention = nn.Sequential(
            nn.Linear(input_dim, input_dim),
            nn.Tanh(),
            nn.Linear(input_dim, input_dim),
            nn.Softmax(dim=-1)
        )
        
        # Temporal attention
        self.temporal_attention = nn.Sequential(
            nn.Linear(hidden_dim * 2, 128),
            nn.Tanh(),
            nn.Linear(128, 1)
        )
        
        # Output head
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        """
        Args:
            x: (batch, seq_len, input_dim)
        Returns:
            predictions: (batch, 1)
        """
        # Feature-level attention
        feature_weights = self.feature_attention(x)
        x_attended = x * feature_weights
        
        # GRU encoding
        gru_out, _ = self.gru(x_attended)  # (batch, seq_len, hidden*2)
        
        # Temporal attention
        attention_scores = self.temporal_attention(gru_out)  # (batch, seq_len, 1)
        attention_weights = torch.softmax(attention_scores, dim=1)
        
        # Weighted sum
        context = torch.sum(gru_out * attention_weights, dim=1)  # (batch, hidden*2)
        
        # Predict
        output = self.fc(context)
        
        return {
            'risk_score': output,
            'attention_weights': attention_weights.squeeze(-1)
        }


def train_published_baselines(
    train_samples: List[Dict],
    val_samples: List[Dict],
    test_samples: List[Dict],
    epochs: int = 30,
    save_dir: str = 'models/published_baselines'
):
    """
    Train all published baseline models
    
    Returns:
        Dictionary with results for each model
    """
    import os
    os.makedirs(save_dir, exist_ok=True)
    
    from torch.utils.data import DataLoader
    from model_trainer import DeteriorationDataset
    
    results = {}
    
    print("=" * 70)
    print("TRAINING PUBLISHED BASELINE MODELS (2022-2024)")
    print("=" * 70)
    
    # Prepare datasets
    class SimpleDataset:
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
    
    train_dataset = SimpleDataset(train_samples)
    val_dataset = SimpleDataset(val_samples)
    test_dataset = SimpleDataset(test_samples)
    
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=32)
    test_loader = DataLoader(test_dataset, batch_size=32)
    
    models = [
        ('Transformer-EWS (2024)', TransformerEWS2024()),
        ('Multi-Task LSTM (2023)', MultiTaskLSTM2023()),
        ('Attention-Risk (2023)', AttentionRiskPredictor2023())
    ]
    
    for model_name, model in models:
        print(f"\n[Training] {model_name}")
        print("-" * 70)
        
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = nn.BCELoss()
        
        best_auroc = 0
        
        for epoch in range(epochs):
            # Train
            model.train()
            for batch in train_loader:
                vitals = batch['vitals']
                labels = batch['label']
                
                optimizer.zero_grad()
                outputs = model(vitals)
                loss = criterion(outputs['risk_score'], labels)
                loss.backward()
                optimizer.step()
            
            # Validate every 5 epochs
            if (epoch + 1) % 5 == 0:
                model.eval()
                all_preds = []
                all_labels = []
                
                with torch.no_grad():
                    for batch in val_loader:
                        vitals = batch['vitals']
                        labels = batch['label']
                        outputs = model(vitals)
                        all_preds.extend(outputs['risk_score'].cpu().numpy())
                        all_labels.extend(labels.cpu().numpy())
                
                auroc = roc_auc_score(all_labels, all_preds)
                
                if auroc > best_auroc:
                    best_auroc = auroc
                    torch.save(model.state_dict(), f'{save_dir}/{model_name.replace(" ", "_")}.pt')
                    print(f"  Epoch {epoch+1}: AUROC = {auroc:.4f} ✓ (new best)")
        
        # Test
        model.eval()
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for batch in test_loader:
                vitals = batch['vitals']
                labels = batch['label']
                outputs = model(vitals)
                all_preds.extend(outputs['risk_score'].cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        auroc = roc_auc_score(all_labels, all_preds)
        auprc = average_precision_score(all_labels, all_preds)
        
        results[model_name] = {
            'auroc': float(auroc),
            'auprc': float(auprc),
            'best_val_auroc': float(best_auroc)
        }
        
        print(f"\n  Final Test Results:")
        print(f"    AUROC: {auroc:.4f}")
        print(f"    AUPRC: {auprc:.4f}")
    
    # Save results
    import json
    with open(f'{save_dir}/published_baseline_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("PUBLISHED BASELINES TRAINING COMPLETE")
    print("=" * 70)
    
    print("\n📊 Comparison with Published Results:")
    print(f"{'Model':<30} {'Our AUROC':<12} {'Published AUROC':<15}")
    print("-" * 70)
    print(f"{'Transformer-EWS (2024)':<30} {results['Transformer-EWS (2024)']['auroc']:<12.4f} {'0.82':<15}")
    print(f"{'Multi-Task LSTM (2023)':<30} {results['Multi-Task LSTM (2023)']['auroc']:<12.4f} {'0.80':<15}")
    print(f"{'Attention-Risk (2023)':<30} {results['Attention-Risk (2023)']['auroc']:<12.4f} {'0.81':<15}")
    
    return results


if __name__ == "__main__":
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
    
    # Train published baselines
    results = train_published_baselines(train_samples, val_samples, test_samples, epochs=20)

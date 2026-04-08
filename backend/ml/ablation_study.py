"""
Ablation Study Framework

Systematically removes components from the full model to measure
their individual contributions to performance.

Configurations:
1. Base LSTM only (no attention, no text, no personalization)
2. + Temporal Attention
3. + Clinical Text Embeddings
4. + Personalized Calibration (Full Model)
"""

import torch
import torch.nn as nn
from typing import Dict, List
import json
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score

from temporal_fusion_model import (
    TemporalFusionNetwork,
    TemporalAttention,
    PersonalizedCalibration,
    MultiModalFusionLayer
)


class AblationModel1_BaselineLSTM(nn.Module):
    """
    Configuration 1: Base LSTM only
    - No attention
    - No text embeddings
    - No personalization
    """
    
    def __init__(self, num_vitals=4, hidden_dim=128, dropout=0.3):
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=num_vitals,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=dropout
        )
        
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, vitals_sequence, **kwargs):
        lstm_out, (h_n, c_n) = self.lstm(vitals_sequence)
        last_hidden = torch.cat([h_n[-2], h_n[-1]], dim=1)
        output = self.fc(last_hidden)
        return {'risk_score': output}


class AblationModel2_WithAttention(nn.Module):
    """
    Configuration 2: LSTM + Temporal Attention
    - Has attention
    - No text embeddings
    - No personalization
    """
    
    def __init__(self, num_vitals=4, hidden_dim=128, dropout=0.3):
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=num_vitals,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=dropout
        )
        
        self.attention = TemporalAttention(hidden_dim * 2)
        
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, vitals_sequence, **kwargs):
        lstm_out, _ = self.lstm(vitals_sequence)
        context, attention_weights = self.attention(lstm_out)
        output = self.fc(context)
        return {'risk_score': output, 'attention_weights': attention_weights}


class AblationModel3_WithText(nn.Module):
    """
    Configuration 3: LSTM + Attention + Text Embeddings
    - Has attention
    - Has text embeddings
    - No personalization
    """
    
    def __init__(self, num_vitals=4, hidden_dim=128, text_dim=384, dropout=0.3):
        super().__init__()
        
        self.lstm = nn.LSTM(
            input_size=num_vitals,
            hidden_size=hidden_dim,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=dropout
        )
        
        self.attention = TemporalAttention(hidden_dim * 2)
        
        # Simple fusion (concatenation)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2 + text_dim, 128),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
    
    def forward(self, vitals_sequence, text_embeddings, **kwargs):
        lstm_out, _ = self.lstm(vitals_sequence)
        context, attention_weights = self.attention(lstm_out)
        
        # Concatenate temporal and text features
        combined = torch.cat([context, text_embeddings], dim=1)
        output = self.fc(combined)
        
        return {'risk_score': output, 'attention_weights': attention_weights}


def run_ablation_study(
    train_samples: List[Dict],
    val_samples: List[Dict],
    test_samples: List[Dict],
    epochs: int = 30,
    save_dir: str = 'models/ablation'
):
    """
    Run complete ablation study
    
    Returns:
        Dictionary with results for each configuration
    """
    import os
    os.makedirs(save_dir, exist_ok=True)
    
    from torch.utils.data import DataLoader
    from model_trainer import DeteriorationDataset, ModelTrainer
    from temporal_fusion_model import TemporalFusionNetwork, FocalLoss
    
    results = {}
    
    print("=" * 70)
    print("ABLATION STUDY - Measuring Component Contributions")
    print("=" * 70)
    
    # Prepare text encoder for models that need it
    from sentence_transformers import SentenceTransformer
    text_encoder = SentenceTransformer('all-MiniLM-L6-v2')
    
    configurations = [
        {
            'name': 'Config 1: Base LSTM Only',
            'model_class': AblationModel1_BaselineLSTM,
            'needs_text': False,
            'needs_baseline': False,
            'needs_static': False
        },
        {
            'name': 'Config 2: + Temporal Attention',
            'model_class': AblationModel2_WithAttention,
            'needs_text': False,
            'needs_baseline': False,
            'needs_static': False
        },
        {
            'name': 'Config 3: + Text Embeddings',
            'model_class': AblationModel3_WithText,
            'needs_text': True,
            'needs_baseline': False,
            'needs_static': False
        },
        {
            'name': 'Config 4: Full Model (+ Personalization)',
            'model_class': TemporalFusionNetwork,
            'needs_text': True,
            'needs_baseline': True,
            'needs_static': True
        }
    ]
    
    for i, config in enumerate(configurations, 1):
        print(f"\n[{i}/4] Training {config['name']}...")
        
        # Initialize model
        if config['model_class'] == TemporalFusionNetwork:
            model = TemporalFusionNetwork()
            model.load_text_encoder()
        else:
            model = config['model_class']()
        
        # Create custom dataset based on needs
        class AblationDataset:
            def __init__(self, samples, text_encoder, config):
                self.samples = samples
                self.text_encoder = text_encoder
                self.config = config
                
                # Pre-encode text if needed
                if config['needs_text']:
                    all_notes = [s['clinical_notes'] for s in samples]
                    self.text_embeddings = text_encoder.encode(
                        all_notes, convert_to_tensor=True, show_progress_bar=False
                    )
            
            def __len__(self):
                return len(self.samples)
            
            def __getitem__(self, idx):
                sample = self.samples[idx]
                item = {
                    'vitals_sequence': torch.FloatTensor(sample['vitals_sequence']),
                    'label': torch.FloatTensor([sample['label']])
                }
                
                if self.config['needs_text']:
                    item['text_embedding'] = self.text_embeddings[idx]
                
                if self.config['needs_baseline']:
                    item['baseline'] = torch.FloatTensor(sample['baseline'])
                
                if self.config['needs_static']:
                    item['static_features'] = torch.FloatTensor(sample['static_features'])
                
                return item
        
        # Create datasets
        train_dataset = AblationDataset(train_samples, text_encoder, config)
        val_dataset = AblationDataset(val_samples, text_encoder, config)
        test_dataset = AblationDataset(test_samples, text_encoder, config)
        
        train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=32)
        test_loader = DataLoader(test_dataset, batch_size=32)
        
        # Train
        optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
        criterion = FocalLoss()
        
        best_auroc = 0
        for epoch in range(epochs):
            model.train()
            for batch in train_loader:
                optimizer.zero_grad()
                
                # Prepare inputs based on model needs
                if config['model_class'] == TemporalFusionNetwork:
                    outputs = model(
                        batch['vitals_sequence'],
                        batch['baseline'],
                        batch['text_embedding'],
                        batch['static_features']
                    )
                elif config['needs_text']:
                    outputs = model(batch['vitals_sequence'], batch['text_embedding'])
                else:
                    outputs = model(batch['vitals_sequence'])
                
                loss = criterion(outputs['risk_score'], batch['label'])
                loss.backward()
                optimizer.step()
            
            # Validate
            if (epoch + 1) % 5 == 0:
                model.eval()
                all_preds = []
                all_labels = []
                with torch.no_grad():
                    for batch in val_loader:
                        if config['model_class'] == TemporalFusionNetwork:
                            outputs = model(
                                batch['vitals_sequence'],
                                batch['baseline'],
                                batch['text_embedding'],
                                batch['static_features']
                            )
                        elif config['needs_text']:
                            outputs = model(batch['vitals_sequence'], batch['text_embedding'])
                        else:
                            outputs = model(batch['vitals_sequence'])
                        
                        all_preds.extend(outputs['risk_score'].cpu().numpy())
                        all_labels.extend(batch['label'].cpu().numpy())
                
                auroc = roc_auc_score(all_labels, all_preds)
                if auroc > best_auroc:
                    best_auroc = auroc
                    torch.save(model.state_dict(), f'{save_dir}/config_{i}.pt')
        
        # Test
        model.eval()
        all_preds = []
        all_labels = []
        with torch.no_grad():
            for batch in test_loader:
                if config['model_class'] == TemporalFusionNetwork:
                    outputs = model(
                        batch['vitals_sequence'],
                        batch['baseline'],
                        batch['text_embedding'],
                        batch['static_features']
                    )
                elif config['needs_text']:
                    outputs = model(batch['vitals_sequence'], batch['text_embedding'])
                else:
                    outputs = model(batch['vitals_sequence'])
                
                all_preds.extend(outputs['risk_score'].cpu().numpy())
                all_labels.extend(batch['label'].cpu().numpy())
        
        # Calculate metrics
        auroc = roc_auc_score(all_labels, all_preds)
        auprc = average_precision_score(all_labels, all_preds)
        
        results[config['name']] = {
            'auroc': float(auroc),
            'auprc': float(auprc),
            'improvement_over_base': float(auroc - results.get('Config 1: Base LSTM Only', {}).get('auroc', auroc))
        }
        
        print(f"  AUROC: {auroc:.4f}")
        print(f"  AUPRC: {auprc:.4f}")
    
    # Save results
    with open(f'{save_dir}/ablation_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "=" * 70)
    print("ABLATION STUDY COMPLETE")
    print("=" * 70)
    print("\n📊 Component Contributions:")
    
    base_auroc = results['Config 1: Base LSTM Only']['auroc']
    for config_name, metrics in results.items():
        improvement = ((metrics['auroc'] - base_auroc) / base_auroc) * 100
        print(f"\n{config_name}:")
        print(f"  AUROC: {metrics['auroc']:.4f} (+{improvement:.1f}%)")
    
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
    
    # Run ablation study
    results = run_ablation_study(train_samples, val_samples, test_samples, epochs=20)

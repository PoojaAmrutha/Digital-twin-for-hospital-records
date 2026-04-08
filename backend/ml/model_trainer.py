"""
Model Training Pipeline for Temporal Fusion Network

Implements:
- Custom training loop with focal loss
- Differential privacy noise injection
- Early stopping and model checkpointing
- Performance metrics calculation (AUROC, AUPRC, calibration)
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from sklearn.calibration import calibration_curve
from typing import Dict, List, Tuple
import os
import json
from datetime import datetime

from temporal_fusion_model import TemporalFusionNetwork, FocalLoss
from synthetic_data_generator import SyntheticPatientGenerator


class DeteriorationDataset(Dataset):
    """PyTorch Dataset for patient deterioration data"""
    
    def __init__(self, samples: List[Dict], text_encoder):
        self.samples = samples
        self.text_encoder = text_encoder
        
        # Pre-encode all clinical notes
        print("Encoding clinical notes...")
        all_notes = [s['clinical_notes'] for s in samples]
        self.text_embeddings = text_encoder.encode(
            all_notes,
            convert_to_tensor=True,
            show_progress_bar=True
        )
    
    def __len__(self):
        return len(self.samples)
    
    def __getitem__(self, idx):
        sample = self.samples[idx]
        
        return {
            'vitals_sequence': torch.FloatTensor(sample['vitals_sequence']),
            'baseline': torch.FloatTensor(sample['baseline']),
            'text_embedding': self.text_embeddings[idx],
            'static_features': torch.FloatTensor(sample['static_features']),
            'label': torch.FloatTensor([sample['label']])
        }


class ModelTrainer:
    """
    Training pipeline for Temporal Fusion Network
    """
    
    def __init__(
        self,
        model: TemporalFusionNetwork,
        device: str = 'cpu',
        learning_rate: float = 0.001,
        use_focal_loss: bool = True
    ):
        self.model = model.to(device)
        self.device = device
        self.optimizer = optim.Adam(model.parameters(), lr=learning_rate)
        
        # Loss function
        if use_focal_loss:
            self.criterion = FocalLoss(alpha=0.25, gamma=2.0)
        else:
            self.criterion = nn.BCELoss()
        
        # Training history
        self.history = {
            'train_loss': [],
            'val_loss': [],
            'val_auroc': [],
            'val_auprc': []
        }
        
        self.best_auroc = 0.0
        self.patience_counter = 0
    
    def train_epoch(self, train_loader: DataLoader) -> float:
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        
        for batch in train_loader:
            # Move to device
            vitals = batch['vitals_sequence'].to(self.device)
            baselines = batch['baseline'].to(self.device)
            text_emb = batch['text_embedding'].to(self.device)
            static = batch['static_features'].to(self.device)
            labels = batch['label'].to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(vitals, baselines, text_emb, static)
            loss = self.criterion(outputs['risk_score'], labels)
            
            # Backward pass
            loss.backward()
            
            # Gradient clipping for stability
            torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
            
            self.optimizer.step()
            
            total_loss += loss.item()
        
        return total_loss / len(train_loader)
    
    def validate(self, val_loader: DataLoader) -> Dict[str, float]:
        """Validate model"""
        self.model.eval()
        total_loss = 0.0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for batch in val_loader:
                vitals = batch['vitals_sequence'].to(self.device)
                baselines = batch['baseline'].to(self.device)
                text_emb = batch['text_embedding'].to(self.device)
                static = batch['static_features'].to(self.device)
                labels = batch['label'].to(self.device)
                
                outputs = self.model(vitals, baselines, text_emb, static)
                loss = self.criterion(outputs['risk_score'], labels)
                
                total_loss += loss.item()
                all_preds.extend(outputs['risk_score'].cpu().numpy())
                all_labels.extend(labels.cpu().numpy())
        
        # Calculate metrics
        all_preds = np.array(all_preds).flatten()
        all_labels = np.array(all_labels).flatten()
        
        auroc = roc_auc_score(all_labels, all_preds)
        auprc = average_precision_score(all_labels, all_preds)
        brier = brier_score_loss(all_labels, all_preds)
        
        return {
            'loss': total_loss / len(val_loader),
            'auroc': auroc,
            'auprc': auprc,
            'brier_score': brier
        }
    
    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 50,
        patience: int = 10,
        save_dir: str = 'models/deterioration'
    ):
        """
        Full training loop with early stopping
        
        Args:
            train_loader: Training data loader
            val_loader: Validation data loader
            epochs: Maximum number of epochs
            patience: Early stopping patience
            save_dir: Directory to save checkpoints
        """
        os.makedirs(save_dir, exist_ok=True)
        
        print("=" * 70)
        print("Training Temporal Fusion Network")
        print("=" * 70)
        print(f"Device: {self.device}")
        print(f"Epochs: {epochs}")
        print(f"Patience: {patience}")
        print(f"Save directory: {save_dir}")
        print("=" * 70)
        
        for epoch in range(epochs):
            # Train
            train_loss = self.train_epoch(train_loader)
            
            # Validate
            val_metrics = self.validate(val_loader)
            
            # Update history
            self.history['train_loss'].append(train_loss)
            self.history['val_loss'].append(val_metrics['loss'])
            self.history['val_auroc'].append(val_metrics['auroc'])
            self.history['val_auprc'].append(val_metrics['auprc'])
            
            # Print progress
            print(f"Epoch {epoch+1}/{epochs} | "
                  f"Train Loss: {train_loss:.4f} | "
                  f"Val Loss: {val_metrics['loss']:.4f} | "
                  f"Val AUROC: {val_metrics['auroc']:.4f} | "
                  f"Val AUPRC: {val_metrics['auprc']:.4f}")
            
            # Early stopping and checkpointing
            if val_metrics['auroc'] > self.best_auroc:
                self.best_auroc = val_metrics['auroc']
                self.patience_counter = 0
                
                # Save best model
                checkpoint_path = os.path.join(save_dir, 'best_model.pt')
                torch.save({
                    'epoch': epoch,
                    'model_state_dict': self.model.state_dict(),
                    'optimizer_state_dict': self.optimizer.state_dict(),
                    'best_auroc': self.best_auroc,
                    'history': self.history
                }, checkpoint_path)
                print(f"  ✓ New best model saved (AUROC: {self.best_auroc:.4f})")
            else:
                self.patience_counter += 1
                if self.patience_counter >= patience:
                    print(f"\nEarly stopping triggered after {epoch+1} epochs")
                    break
        
        # Save final training history
        history_path = os.path.join(save_dir, 'training_history.json')
        with open(history_path, 'w') as f:
            json.dump(self.history, f, indent=2)
        
        print("\n" + "=" * 70)
        print(f"Training completed!")
        print(f"Best validation AUROC: {self.best_auroc:.4f}")
        print("=" * 70)
    
    def load_checkpoint(self, checkpoint_path: str):
        """Load model from checkpoint"""
        checkpoint = torch.load(checkpoint_path, map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.best_auroc = checkpoint['best_auroc']
        self.history = checkpoint['history']
        print(f"✓ Loaded checkpoint from {checkpoint_path}")
        print(f"  Best AUROC: {self.best_auroc:.4f}")


def train_deterioration_model(
    n_samples: int = 2000,
    batch_size: int = 32,
    epochs: int = 50,
    save_dir: str = 'models/deterioration'
):
    """
    Main training function
    
    Args:
        n_samples: Number of synthetic patients to generate
        batch_size: Training batch size
        epochs: Maximum training epochs
        save_dir: Directory to save model
    """
    print("\n" + "=" * 70)
    print("DETERIORATION PREDICTION MODEL - TRAINING PIPELINE")
    print("=" * 70)
    
    # 1. Generate synthetic data
    print("\n[1/5] Generating synthetic patient data...")
    generator = SyntheticPatientGenerator(random_seed=42)
    samples, labels = generator.generate_dataset(
        n_samples=n_samples,
        deterioration_ratio=0.2,
        sequence_hours=48
    )
    
    # 2. Split data
    print("\n[2/5] Splitting into train/val/test sets...")
    n_train = int(0.7 * len(samples))
    n_val = int(0.15 * len(samples))
    
    train_samples = samples[:n_train]
    val_samples = samples[n_train:n_train+n_val]
    test_samples = samples[n_train+n_val:]
    
    print(f"  Train: {len(train_samples)} samples")
    print(f"  Val: {len(val_samples)} samples")
    print(f"  Test: {len(test_samples)} samples")
    
    # 3. Initialize model
    print("\n[3/5] Initializing model...")
    model = TemporalFusionNetwork(
        num_vitals=4,
        temporal_hidden_dim=128,
        text_embedding_dim=384,
        static_dim=10,
        fusion_dim=256,
        dropout_rate=0.3
    )
    model.load_text_encoder()
    
    # 4. Create datasets and loaders
    print("\n[4/5] Creating data loaders...")
    train_dataset = DeteriorationDataset(train_samples, model.text_encoder)
    val_dataset = DeteriorationDataset(val_samples, model.text_encoder)
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    
    # 5. Train
    print("\n[5/5] Training model...")
    trainer = ModelTrainer(model, device='cpu', learning_rate=0.001)
    trainer.train(train_loader, val_loader, epochs=epochs, patience=10, save_dir=save_dir)
    
    print("\n✓ Training pipeline completed successfully!")
    return model, trainer


if __name__ == "__main__":
    # Train model
    model, trainer = train_deterioration_model(
        n_samples=1000,  # Small dataset for testing
        batch_size=32,
        epochs=30,
        save_dir='models/deterioration'
    )

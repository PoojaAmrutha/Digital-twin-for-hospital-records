"""
Multi-Modal Temporal Fusion Network for Health Deterioration Prediction

This module implements a novel deep learning architecture that predicts patient
health deterioration 24-72 hours in advance by combining:
1. Temporal attention over vital sign sequences
2. Clinical text embeddings from symptom descriptions
3. Personalized baseline calibration
4. Uncertainty quantification via Monte Carlo Dropout

Author: HealthWatch AI Research Team
Novel Contribution: IEEE Q1 Journal Publication
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
from typing import Dict, List, Tuple, Optional

import warnings
warnings.filterwarnings('ignore')


class TemporalAttention(nn.Module):
    """
    Temporal Attention Mechanism
    
    Learns to assign importance weights to different time steps in the
    vital signs sequence, allowing the model to focus on critical periods
    (e.g., sudden spikes 6 hours ago vs stable readings 24 hours ago)
    """
    
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.attention = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.Tanh(),
            nn.Linear(hidden_dim // 2, 1)
        )
    
    def forward(self, lstm_outputs: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Args:
            lstm_outputs: (batch_size, seq_len, hidden_dim)
        
        Returns:
            context_vector: (batch_size, hidden_dim) - weighted sum of outputs
            attention_weights: (batch_size, seq_len) - importance of each timestep
        """
        # Calculate attention scores
        attention_scores = self.attention(lstm_outputs)  # (batch, seq_len, 1)
        attention_weights = F.softmax(attention_scores.squeeze(-1), dim=1)  # (batch, seq_len)
        
        # Compute weighted context vector
        context_vector = torch.bmm(
            attention_weights.unsqueeze(1),  # (batch, 1, seq_len)
            lstm_outputs  # (batch, seq_len, hidden_dim)
        ).squeeze(1)  # (batch, hidden_dim)
        
        return context_vector, attention_weights


class PersonalizedCalibration(nn.Module):
    """
    Personalized Baseline Calibration Layer
    
    Normalizes vital signs by patient-specific baselines rather than
    population averages. For example, an athlete's resting HR of 50 bpm
    is normal, but would be concerning for most patients.
    """
    
    def __init__(self, num_vitals: int):
        super().__init__()
        self.num_vitals = num_vitals
        # Learnable calibration parameters per vital
        self.baseline_adjustment = nn.Parameter(torch.zeros(num_vitals))
        self.scale_adjustment = nn.Parameter(torch.ones(num_vitals))
    
    def forward(self, vitals: torch.Tensor, patient_baselines: torch.Tensor) -> torch.Tensor:
        """
        Args:
            vitals: (batch, seq_len, num_vitals) - raw vital signs
            patient_baselines: (batch, num_vitals) - patient-specific means
        
        Returns:
            calibrated_vitals: (batch, seq_len, num_vitals) - normalized vitals
        """
        # Expand baselines to match sequence dimension
        baselines_expanded = patient_baselines.unsqueeze(1)  # (batch, 1, num_vitals)
        
        # Normalize by patient baseline
        deviation = vitals - baselines_expanded
        
        # Apply learnable calibration
        calibrated = deviation * self.scale_adjustment + self.baseline_adjustment
        
        return calibrated


class MultiModalFusionLayer(nn.Module):
    """
    Multi-Modal Fusion Layer
    
    Combines three modalities with learned attention weights:
    1. Temporal features (from LSTM + attention)
    2. Text features (from clinical notes)
    3. Static features (demographics, conditions)
    """
    
    def __init__(self, temporal_dim: int, text_dim: int, static_dim: int, output_dim: int):
        super().__init__()
        
        # Project each modality to common dimension
        self.temporal_proj = nn.Linear(temporal_dim, output_dim)
        self.text_proj = nn.Linear(text_dim, output_dim)
        self.static_proj = nn.Linear(static_dim, output_dim)
        
        # Learnable fusion weights (gating mechanism)
        self.fusion_gate = nn.Sequential(
            nn.Linear(output_dim * 3, output_dim),
            nn.ReLU(),
            nn.Linear(output_dim, 3),
            nn.Softmax(dim=1)
        )
    
    def forward(self, temporal_feat: torch.Tensor, text_feat: torch.Tensor, 
                static_feat: torch.Tensor) -> torch.Tensor:
        """
        Args:
            temporal_feat: (batch, temporal_dim)
            text_feat: (batch, text_dim)
            static_feat: (batch, static_dim)
        
        Returns:
            fused_features: (batch, output_dim)
        """
        # Project to common space
        temp_proj = self.temporal_proj(temporal_feat)
        text_proj = self.text_proj(text_feat)
        stat_proj = self.static_proj(static_feat)
        
        # Stack for gating
        stacked = torch.cat([temp_proj, text_proj, stat_proj], dim=1)
        
        # Compute fusion weights
        fusion_weights = self.fusion_gate(stacked)  # (batch, 3)
        
        # Weighted combination
        fused = (fusion_weights[:, 0:1] * temp_proj + 
                 fusion_weights[:, 1:2] * text_proj + 
                 fusion_weights[:, 2:3] * stat_proj)
        
        return fused


class TemporalFusionNetwork(nn.Module):
    """
    Multi-Modal Temporal Fusion Network
    
    Complete architecture for health deterioration prediction combining
    all components: temporal encoding, text encoding, personalized calibration,
    multi-modal fusion, and uncertainty-aware prediction.
    """
    
    def __init__(
        self,
        num_vitals: int = 4,  # HR, SpO2, Temp, Stress
        temporal_hidden_dim: int = 128,
        text_embedding_dim: int = 384,  # Sentence-BERT default
        static_dim: int = 10,  # Age, gender, conditions, etc.
        fusion_dim: int = 256,
        dropout_rate: float = 0.3
    ):
        super().__init__()
        
        self.num_vitals = num_vitals
        self.dropout_rate = dropout_rate
        
        # 1. Personalized Calibration
        self.calibration = PersonalizedCalibration(num_vitals)
        
        # 2. Temporal Encoder (Bidirectional LSTM)
        self.temporal_lstm = nn.LSTM(
            input_size=num_vitals,
            hidden_size=temporal_hidden_dim,
            num_layers=2,
            batch_first=True,
            bidirectional=True,
            dropout=dropout_rate
        )
        
        # 3. Temporal Attention
        self.temporal_attention = TemporalAttention(temporal_hidden_dim * 2)  # *2 for bidirectional
        
        # 4. Multi-Modal Fusion
        self.fusion = MultiModalFusionLayer(
            temporal_dim=temporal_hidden_dim * 2,
            text_dim=text_embedding_dim,
            static_dim=static_dim,
            output_dim=fusion_dim
        )
        
        # 5. Prediction Head with Uncertainty
        self.prediction_head = nn.Sequential(
            nn.Linear(fusion_dim, 128),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(64, 1),
            nn.Sigmoid()
        )
        
        # Text encoder (loaded separately)
        self.text_encoder = None
    
    def load_text_encoder(self, model_name: str = 'all-MiniLM-L6-v2'):
        """Load sentence transformer for clinical text encoding"""
        from sentence_transformers import SentenceTransformer
        self.text_encoder = SentenceTransformer(model_name)
        # Freeze text encoder (pre-trained)
        for param in self.text_encoder.parameters():
            param.requires_grad = False
    
    def encode_text(self, clinical_notes: List[str]) -> torch.Tensor:
        """
        Encode clinical notes to embeddings
        
        Args:
            clinical_notes: List of symptom descriptions
        
        Returns:
            embeddings: (batch, text_embedding_dim)
        """
        if self.text_encoder is None:
            self.load_text_encoder()
        
        embeddings = self.text_encoder.encode(
            clinical_notes, 
            convert_to_tensor=True,
            show_progress_bar=False
        )
        return embeddings
    
    def forward(
        self,
        vitals_sequence: torch.Tensor,
        patient_baselines: torch.Tensor,
        text_embeddings: torch.Tensor,
        static_features: torch.Tensor,
        return_attention: bool = False
    ) -> Dict[str, torch.Tensor]:
        """
        Forward pass through the network
        
        Args:
            vitals_sequence: (batch, seq_len, num_vitals) - time series vitals
            patient_baselines: (batch, num_vitals) - patient-specific baselines
            text_embeddings: (batch, text_dim) - encoded clinical notes
            static_features: (batch, static_dim) - demographics, conditions
            return_attention: whether to return attention weights
        
        Returns:
            Dictionary containing:
                - risk_score: (batch, 1) - deterioration probability
                - attention_weights: (batch, seq_len) - temporal attention (if requested)
        """
        # 1. Personalized calibration
        calibrated_vitals = self.calibration(vitals_sequence, patient_baselines)
        
        # 2. Temporal encoding
        lstm_out, _ = self.temporal_lstm(calibrated_vitals)  # (batch, seq_len, hidden*2)
        
        # 3. Temporal attention
        temporal_context, attention_weights = self.temporal_attention(lstm_out)
        
        # 4. Multi-modal fusion
        fused_features = self.fusion(temporal_context, text_embeddings, static_features)
        
        # 5. Prediction
        risk_score = self.prediction_head(fused_features)
        
        output = {'risk_score': risk_score}
        if return_attention:
            output['attention_weights'] = attention_weights
        
        return output
    
    def predict_with_uncertainty(
        self,
        vitals_sequence: torch.Tensor,
        patient_baselines: torch.Tensor,
        text_embeddings: torch.Tensor,
        static_features: torch.Tensor,
        n_samples: int = 50
    ) -> Dict[str, torch.Tensor]:
        """
        Predict with uncertainty quantification using Monte Carlo Dropout
        
        Args:
            Same as forward, plus:
            n_samples: Number of MC dropout samples
        
        Returns:
            Dictionary containing:
                - mean_risk: (batch, 1) - mean prediction
                - std_risk: (batch, 1) - prediction uncertainty
                - lower_bound: (batch, 1) - 95% CI lower
                - upper_bound: (batch, 1) - 95% CI upper
        """
        self.train()  # Enable dropout during inference
        
        predictions = []
        for _ in range(n_samples):
            with torch.no_grad():
                output = self.forward(
                    vitals_sequence, patient_baselines,
                    text_embeddings, static_features,
                    return_attention=False
                )
                predictions.append(output['risk_score'])
        
        self.eval()  # Restore eval mode
        
        # Stack predictions
        predictions = torch.stack(predictions, dim=0)  # (n_samples, batch, 1)
        
        # Calculate statistics
        mean_risk = predictions.mean(dim=0)
        std_risk = predictions.std(dim=0)
        
        # 95% confidence interval (1.96 * std)
        lower_bound = torch.clamp(mean_risk - 1.96 * std_risk, 0, 1)
        upper_bound = torch.clamp(mean_risk + 1.96 * std_risk, 0, 1)
        
        return {
            'mean_risk': mean_risk,
            'std_risk': std_risk,
            'lower_bound': lower_bound,
            'upper_bound': upper_bound
        }


class FocalLoss(nn.Module):
    """
    Focal Loss for handling class imbalance
    
    Focuses training on hard-to-classify examples (deteriorating patients)
    rather than easy negatives (stable patients).
    
    Reference: Lin et al. "Focal Loss for Dense Object Detection" (2017)
    """
    
    def __init__(self, alpha: float = 0.25, gamma: float = 2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
    
    def forward(self, predictions: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        """
        Args:
            predictions: (batch, 1) - predicted probabilities
            targets: (batch, 1) - ground truth labels (0 or 1)
        
        Returns:
            loss: scalar
        """
        bce_loss = F.binary_cross_entropy(predictions, targets, reduction='none')
        
        # Focal weight: (1 - p_t)^gamma
        p_t = predictions * targets + (1 - predictions) * (1 - targets)
        focal_weight = (1 - p_t) ** self.gamma
        
        # Alpha weighting for class balance
        alpha_weight = self.alpha * targets + (1 - self.alpha) * (1 - targets)
        
        loss = alpha_weight * focal_weight * bce_loss
        
        return loss.mean()


def count_parameters(model: nn.Module) -> int:
    """Count trainable parameters in model"""
    return sum(p.numel() for p in model.parameters() if p.requires_grad)


# Example usage and testing
if __name__ == "__main__":
    print("=" * 70)
    print("Multi-Modal Temporal Fusion Network - Architecture Test")
    print("=" * 70)
    
    # Initialize model
    model = TemporalFusionNetwork(
        num_vitals=4,
        temporal_hidden_dim=128,
        text_embedding_dim=384,
        static_dim=10,
        fusion_dim=256,
        dropout_rate=0.3
    )
    
    print(f"\n✓ Model initialized")
    print(f"  Total parameters: {count_parameters(model):,}")
    
    # Create dummy data
    batch_size = 8
    seq_len = 24  # 24 hours of hourly readings
    
    vitals_seq = torch.randn(batch_size, seq_len, 4)  # HR, SpO2, Temp, Stress
    baselines = torch.randn(batch_size, 4)
    text_emb = torch.randn(batch_size, 384)
    static_feat = torch.randn(batch_size, 10)
    
    print(f"\n✓ Created dummy data")
    print(f"  Batch size: {batch_size}")
    print(f"  Sequence length: {seq_len} hours")
    
    # Forward pass
    model.eval()
    with torch.no_grad():
        output = model(vitals_seq, baselines, text_emb, static_feat, return_attention=True)
    
    print(f"\n✓ Forward pass successful")
    print(f"  Risk scores shape: {output['risk_score'].shape}")
    print(f"  Attention weights shape: {output['attention_weights'].shape}")
    print(f"  Sample risk score: {output['risk_score'][0].item():.3f}")
    
    # Uncertainty quantification
    print(f"\n⏳ Testing uncertainty quantification (50 MC samples)...")
    uncertainty_output = model.predict_with_uncertainty(
        vitals_seq, baselines, text_emb, static_feat, n_samples=50
    )
    
    print(f"\n✓ Uncertainty estimation successful")
    print(f"  Mean risk: {uncertainty_output['mean_risk'][0].item():.3f}")
    print(f"  Std risk: {uncertainty_output['std_risk'][0].item():.3f}")
    print(f"  95% CI: [{uncertainty_output['lower_bound'][0].item():.3f}, "
          f"{uncertainty_output['upper_bound'][0].item():.3f}]")
    
    # Test focal loss
    focal_loss = FocalLoss(alpha=0.25, gamma=2.0)
    targets = torch.randint(0, 2, (batch_size, 1)).float()
    loss = focal_loss(output['risk_score'], targets)
    
    print(f"\n✓ Focal loss computed: {loss.item():.4f}")
    
    print("\n" + "=" * 70)
    print("All architecture tests passed! ✓")
    print("=" * 70)

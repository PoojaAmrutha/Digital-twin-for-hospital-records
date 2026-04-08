"""
Synthetic Data Generator for Health Deterioration Prediction

Generates realistic patient trajectories with both stable and deteriorating patterns
for training the temporal fusion network.

Features:
- Realistic vital sign correlations (e.g., fever → elevated HR)
- Gradual and sudden deterioration patterns
- Corresponding clinical notes with symptoms
- Patient-specific baselines
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import random


class SyntheticPatientGenerator:
    """
    Generates synthetic patient data with realistic deterioration patterns
    """
    
    def __init__(self, random_seed: int = 42):
        np.random.seed(random_seed)
        random.seed(random_seed)
        
        # Symptom templates for clinical notes
        self.stable_symptoms = [
            "Patient reports feeling well",
            "No significant complaints",
            "Routine checkup, vitals stable",
            "Patient ambulatory and alert",
            "No acute distress noted"
        ]
        
        self.mild_symptoms = [
            "Patient reports mild fatigue",
            "Slight headache reported",
            "Minor discomfort, no acute issues",
            "Patient reports feeling slightly unwell",
            "Mild nausea reported"
        ]
        
        self.moderate_symptoms = [
            "Patient reports persistent cough and fatigue",
            "Moderate chest discomfort reported",
            "Patient experiencing shortness of breath",
            "Fever and body aches reported",
            "Significant fatigue and weakness"
        ]
        
        self.severe_symptoms = [
            "Patient reports severe chest pain and difficulty breathing",
            "Acute respiratory distress, patient struggling to breathe",
            "Severe confusion and disorientation",
            "Patient reports crushing chest pain radiating to arm",
            "Critical: patient unresponsive, emergency intervention needed"
        ]
    
    def generate_patient_baseline(self) -> Dict[str, float]:
        """
        Generate patient-specific baseline vitals
        
        Returns:
            Dictionary with baseline values for each vital
        """
        # Age affects baseline (older = slightly different norms)
        age = np.random.randint(18, 90)
        
        # Baseline heart rate (varies by age and fitness)
        if age < 40:
            baseline_hr = np.random.uniform(60, 80)
        elif age < 65:
            baseline_hr = np.random.uniform(65, 85)
        else:
            baseline_hr = np.random.uniform(70, 90)
        
        # Baseline SpO2 (healthy range)
        baseline_spo2 = np.random.uniform(96, 99)
        
        # Baseline temperature
        baseline_temp = np.random.uniform(36.5, 37.2)
        
        # Baseline stress level
        baseline_stress = np.random.uniform(1.0, 2.5)
        
        return {
            'age': age,
            'heart_rate': baseline_hr,
            'spo2': baseline_spo2,
            'temperature': baseline_temp,
            'stress_level': baseline_stress
        }
    
    def generate_stable_trajectory(
        self, 
        baseline: Dict[str, float], 
        hours: int = 48
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Generate stable vital signs trajectory (no deterioration)
        
        Args:
            baseline: Patient baseline vitals
            hours: Number of hours to simulate
        
        Returns:
            vitals_sequence: (hours, 4) array of [HR, SpO2, Temp, Stress]
            clinical_notes: List of symptom descriptions
        """
        vitals = []
        notes = []
        
        for hour in range(hours):
            # Add small random fluctuations around baseline
            hr = baseline['heart_rate'] + np.random.normal(0, 5)
            spo2 = baseline['spo2'] + np.random.normal(0, 1)
            temp = baseline['temperature'] + np.random.normal(0, 0.2)
            stress = baseline['stress_level'] + np.random.normal(0, 0.3)
            
            # Clamp to realistic ranges
            hr = np.clip(hr, 50, 100)
            spo2 = np.clip(spo2, 94, 100)
            temp = np.clip(temp, 36, 37.5)
            stress = np.clip(stress, 0, 3)
            
            vitals.append([hr, spo2, temp, stress])
            
            # Add clinical note every 8 hours
            if hour % 8 == 0:
                notes.append(random.choice(self.stable_symptoms))
        
        return np.array(vitals), notes
    
    def generate_gradual_deterioration(
        self, 
        baseline: Dict[str, float], 
        hours: int = 48,
        deterioration_start: int = 12
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Generate gradual deterioration pattern (e.g., developing infection)
        
        Args:
            baseline: Patient baseline vitals
            hours: Total hours to simulate
            deterioration_start: Hour when deterioration begins
        
        Returns:
            vitals_sequence: (hours, 4) array
            clinical_notes: List of symptom descriptions
        """
        vitals = []
        notes = []
        
        for hour in range(hours):
            if hour < deterioration_start:
                # Stable phase
                hr = baseline['heart_rate'] + np.random.normal(0, 5)
                spo2 = baseline['spo2'] + np.random.normal(0, 1)
                temp = baseline['temperature'] + np.random.normal(0, 0.2)
                stress = baseline['stress_level'] + np.random.normal(0, 0.3)
            else:
                # Gradual deterioration
                progress = (hour - deterioration_start) / (hours - deterioration_start)
                
                # Heart rate increases
                hr = baseline['heart_rate'] + progress * 40 + np.random.normal(0, 8)
                
                # SpO2 decreases
                spo2 = baseline['spo2'] - progress * 10 + np.random.normal(0, 2)
                
                # Temperature increases (fever)
                temp = baseline['temperature'] + progress * 2.5 + np.random.normal(0, 0.3)
                
                # Stress increases
                stress = baseline['stress_level'] + progress * 2.5 + np.random.normal(0, 0.5)
            
            # Clamp to realistic ranges
            hr = np.clip(hr, 40, 160)
            spo2 = np.clip(spo2, 80, 100)
            temp = np.clip(temp, 36, 40)
            stress = np.clip(stress, 0, 5)
            
            vitals.append([hr, spo2, temp, stress])
            
            # Add clinical notes
            if hour % 8 == 0:
                if hour < deterioration_start:
                    notes.append(random.choice(self.stable_symptoms))
                elif hour < deterioration_start + (hours - deterioration_start) * 0.4:
                    notes.append(random.choice(self.mild_symptoms))
                elif hour < deterioration_start + (hours - deterioration_start) * 0.7:
                    notes.append(random.choice(self.moderate_symptoms))
                else:
                    notes.append(random.choice(self.severe_symptoms))
        
        return np.array(vitals), notes
    
    def generate_sudden_deterioration(
        self, 
        baseline: Dict[str, float], 
        hours: int = 48,
        event_hour: int = 30
    ) -> Tuple[np.ndarray, List[str]]:
        """
        Generate sudden deterioration pattern (e.g., cardiac event, stroke)
        
        Args:
            baseline: Patient baseline vitals
            hours: Total hours to simulate
            event_hour: Hour when sudden event occurs
        
        Returns:
            vitals_sequence: (hours, 4) array
            clinical_notes: List of symptom descriptions
        """
        vitals = []
        notes = []
        
        for hour in range(hours):
            if hour < event_hour:
                # Stable or mildly concerning
                hr = baseline['heart_rate'] + np.random.normal(0, 7)
                spo2 = baseline['spo2'] + np.random.normal(0, 1.5)
                temp = baseline['temperature'] + np.random.normal(0, 0.2)
                stress = baseline['stress_level'] + np.random.normal(0, 0.4)
            else:
                # Sudden critical change
                hr = baseline['heart_rate'] + 50 + np.random.normal(0, 10)
                spo2 = baseline['spo2'] - 15 + np.random.normal(0, 3)
                temp = baseline['temperature'] + np.random.normal(0, 0.5)
                stress = 4.5 + np.random.normal(0, 0.3)
            
            # Clamp to realistic ranges
            hr = np.clip(hr, 40, 180)
            spo2 = np.clip(spo2, 75, 100)
            temp = np.clip(temp, 35, 40)
            stress = np.clip(stress, 0, 5)
            
            vitals.append([hr, spo2, temp, stress])
            
            # Add clinical notes
            if hour % 8 == 0:
                if hour < event_hour:
                    notes.append(random.choice(self.stable_symptoms + self.mild_symptoms))
                else:
                    notes.append(random.choice(self.severe_symptoms))
        
        return np.array(vitals), notes
    
    def generate_dataset(
        self, 
        n_samples: int = 1000,
        deterioration_ratio: float = 0.2,
        sequence_hours: int = 48
    ) -> Tuple[List[Dict], np.ndarray]:
        """
        Generate complete training dataset
        
        Args:
            n_samples: Total number of patient trajectories
            deterioration_ratio: Fraction of deteriorating cases (0.2 = 20%)
            sequence_hours: Hours of data per patient
        
        Returns:
            samples: List of dictionaries with all patient data
            labels: (n_samples,) array of binary labels (0=stable, 1=deterioration)
        """
        samples = []
        labels = []
        
        n_deteriorating = int(n_samples * deterioration_ratio)
        n_stable = n_samples - n_deteriorating
        
        print(f"Generating {n_samples} patient trajectories...")
        print(f"  - Stable: {n_stable}")
        print(f"  - Deteriorating: {n_deteriorating}")
        
        # Generate stable cases
        for i in range(n_stable):
            baseline = self.generate_patient_baseline()
            vitals, notes = self.generate_stable_trajectory(baseline, sequence_hours)
            
            samples.append({
                'patient_id': f'stable_{i}',
                'vitals_sequence': vitals,
                'baseline': np.array([
                    baseline['heart_rate'],
                    baseline['spo2'],
                    baseline['temperature'],
                    baseline['stress_level']
                ]),
                'clinical_notes': ' | '.join(notes),
                'static_features': self._generate_static_features(baseline['age']),
                'label': 0
            })
            labels.append(0)
        
        # Generate deteriorating cases (mix of gradual and sudden)
        for i in range(n_deteriorating):
            baseline = self.generate_patient_baseline()
            
            # 70% gradual, 30% sudden
            if random.random() < 0.7:
                deterioration_start = random.randint(8, 24)
                vitals, notes = self.generate_gradual_deterioration(
                    baseline, sequence_hours, deterioration_start
                )
            else:
                event_hour = random.randint(20, 36)
                vitals, notes = self.generate_sudden_deterioration(
                    baseline, sequence_hours, event_hour
                )
            
            samples.append({
                'patient_id': f'deteriorating_{i}',
                'vitals_sequence': vitals,
                'baseline': np.array([
                    baseline['heart_rate'],
                    baseline['spo2'],
                    baseline['temperature'],
                    baseline['stress_level']
                ]),
                'clinical_notes': ' | '.join(notes),
                'static_features': self._generate_static_features(baseline['age']),
                'label': 1
            })
            labels.append(1)
        
        # Shuffle
        combined = list(zip(samples, labels))
        random.shuffle(combined)
        samples, labels = zip(*combined)
        
        print(f"✓ Dataset generated successfully!")
        
        return list(samples), np.array(labels)
    
    def _generate_static_features(self, age: int) -> np.ndarray:
        """
        Generate static patient features (demographics, conditions)
        
        Returns:
            (10,) array: [age_norm, gender, has_diabetes, has_hypertension, 
                         has_heart_disease, bmi, smoker, ...]
        """
        age_norm = age / 100.0  # Normalize age
        gender = random.randint(0, 1)  # 0=female, 1=male
        has_diabetes = 1 if random.random() < 0.15 else 0
        has_hypertension = 1 if random.random() < 0.25 else 0
        has_heart_disease = 1 if random.random() < 0.10 else 0
        bmi = np.random.normal(26, 5)  # BMI
        bmi_norm = np.clip(bmi / 50.0, 0, 1)
        smoker = 1 if random.random() < 0.20 else 0
        
        # Padding to make 10 features
        return np.array([
            age_norm, gender, has_diabetes, has_hypertension,
            has_heart_disease, bmi_norm, smoker, 0, 0, 0
        ])


# Example usage
if __name__ == "__main__":
    print("=" * 70)
    print("Synthetic Patient Data Generator - Test")
    print("=" * 70)
    
    generator = SyntheticPatientGenerator(random_seed=42)
    
    # Generate small test dataset
    samples, labels = generator.generate_dataset(
        n_samples=100,
        deterioration_ratio=0.2,
        sequence_hours=48
    )
    
    print(f"\n✓ Generated {len(samples)} samples")
    print(f"  Label distribution: {np.bincount(labels)}")
    
    # Show example
    print("\n" + "=" * 70)
    print("Example Patient (Deteriorating):")
    print("=" * 70)
    
    # Find a deteriorating case
    deteriorating_idx = np.where(labels == 1)[0][0]
    example = samples[deteriorating_idx]
    
    print(f"Patient ID: {example['patient_id']}")
    print(f"Baseline vitals: {example['baseline']}")
    print(f"Sequence shape: {example['vitals_sequence'].shape}")
    print(f"Clinical notes: {example['clinical_notes'][:200]}...")
    print(f"Static features: {example['static_features']}")
    print(f"Label: {example['label']} (deterioration)")
    
    # Show vital trends
    vitals = example['vitals_sequence']
    print(f"\nVital Trends:")
    print(f"  Hour 0:  HR={vitals[0,0]:.1f}, SpO2={vitals[0,1]:.1f}, "
          f"Temp={vitals[0,2]:.1f}, Stress={vitals[0,3]:.1f}")
    print(f"  Hour 24: HR={vitals[24,0]:.1f}, SpO2={vitals[24,1]:.1f}, "
          f"Temp={vitals[24,2]:.1f}, Stress={vitals[24,3]:.1f}")
    print(f"  Hour 47: HR={vitals[47,0]:.1f}, SpO2={vitals[47,1]:.1f}, "
          f"Temp={vitals[47,2]:.1f}, Stress={vitals[47,3]:.1f}")
    
    print("\n" + "=" * 70)
    print("Data generation test passed! ✓")
    print("=" * 70)

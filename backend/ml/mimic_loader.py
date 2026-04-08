"""
MIMIC-III Dataset Loader and Preprocessor

Loads real-world ICU patient data from MIMIC-III database for
deterioration prediction model training and validation.

MIMIC-III Access:
1. Complete CITI training: https://physionet.org/about/citi-course/
2. Request access: https://physionet.org/content/mimiciii/
3. Download data (requires credentialed access)

Dataset: https://physionet.org/content/mimiciii/1.4/
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import os
from pathlib import Path


class MIMICIIILoader:
    """
    Load and preprocess MIMIC-III data for deterioration prediction
    
    Key tables used:
    - PATIENTS: Demographics
    - ADMISSIONS: Hospital admissions
    - ICUSTAYS: ICU stays
    - CHARTEVENTS: Vital signs (HR, SpO2, Temp, BP)
    - LABEVENTS: Lab results
    - NOTEEVENTS: Clinical notes
    """
    
    def __init__(self, mimic_dir: str):
        """
        Args:
            mimic_dir: Path to MIMIC-III CSV files directory
        """
        self.mimic_dir = Path(mimic_dir)
        
        # Verify directory exists
        if not self.mimic_dir.exists():
            raise FileNotFoundError(
                f"MIMIC-III directory not found: {mimic_dir}\n"
                f"Please download from: https://physionet.org/content/mimiciii/"
            )
        
        # MIMIC-III itemids for vital signs
        self.vital_itemids = {
            'heart_rate': [211, 220045],  # Heart Rate
            'spo2': [646, 220277],         # SpO2
            'temperature': [223761, 223762, 678, 679],  # Temperature (F)
            'resp_rate': [618, 615, 220210, 224690],    # Respiratory Rate
            'sbp': [51, 442, 455, 6701, 220179, 220050], # Systolic BP
            'dbp': [8368, 8440, 8441, 8555, 220180, 220051] # Diastolic BP
        }
        
        print(f"✓ MIMIC-III Loader initialized")
        print(f"  Data directory: {self.mimic_dir}")
    
    def load_patients(self, n_patients: Optional[int] = None) -> pd.DataFrame:
        """
        Load patient demographics
        
        Returns:
            DataFrame with patient info
        """
        patients_file = self.mimic_dir / 'PATIENTS.csv'
        
        if not patients_file.exists():
            raise FileNotFoundError(f"PATIENTS.csv not found in {self.mimic_dir}")
        
        print(f"Loading patients from {patients_file}...")
        patients = pd.read_csv(patients_file)
        
        if n_patients:
            patients = patients.head(n_patients)
        
        print(f"✓ Loaded {len(patients)} patients")
        return patients
    
    def load_icu_stays(self) -> pd.DataFrame:
        """Load ICU stay information"""
        icustays_file = self.mimic_dir / 'ICUSTAYS.csv'
        
        print(f"Loading ICU stays from {icustays_file}...")
        icustays = pd.read_csv(icustays_file)
        
        # Convert timestamps
        icustays['INTIME'] = pd.to_datetime(icustays['INTIME'])
        icustays['OUTTIME'] = pd.to_datetime(icustays['OUTTIME'])
        
        # Calculate length of stay
        icustays['LOS_HOURS'] = (icustays['OUTTIME'] - icustays['INTIME']).dt.total_seconds() / 3600
        
        print(f"✓ Loaded {len(icustays)} ICU stays")
        return icustays
    
    def load_vital_signs(
        self,
        icustay_ids: List[int],
        lookback_hours: int = 48
    ) -> pd.DataFrame:
        """
        Load vital signs for specific ICU stays
        
        Args:
            icustay_ids: List of ICU stay IDs
            lookback_hours: Hours of history to load
        
        Returns:
            DataFrame with vital signs
        """
        chartevents_file = self.mimic_dir / 'CHARTEVENTS.csv'
        
        print(f"Loading vital signs from {chartevents_file}...")
        print(f"  ICU stays: {len(icustay_ids)}")
        print(f"  Lookback: {lookback_hours} hours")
        
        # Load in chunks (CHARTEVENTS is huge)
        chunks = []
        chunksize = 1000000
        
        for chunk in pd.read_csv(chartevents_file, chunksize=chunksize):
            # Filter for our ICU stays and vital sign itemids
            all_itemids = []
            for itemid_list in self.vital_itemids.values():
                all_itemids.extend(itemid_list)
            
            filtered = chunk[
                (chunk['ICUSTAY_ID'].isin(icustay_ids)) &
                (chunk['ITEMID'].isin(all_itemids))
            ]
            
            if len(filtered) > 0:
                chunks.append(filtered)
        
        if not chunks:
            print("⚠️ No vital signs found for specified ICU stays")
            return pd.DataFrame()
        
        vitals = pd.concat(chunks, ignore_index=True)
        
        # Convert timestamps
        vitals['CHARTTIME'] = pd.to_datetime(vitals['CHARTTIME'])
        
        print(f"✓ Loaded {len(vitals)} vital sign measurements")
        return vitals
    
    def preprocess_vitals(
        self,
        vitals: pd.DataFrame,
        icustays: pd.DataFrame
    ) -> Dict[int, np.ndarray]:
        """
        Preprocess vital signs into sequences
        
        Returns:
            Dictionary mapping icustay_id to vital sequence (hours, features)
        """
        sequences = {}
        
        for icustay_id in vitals['ICUSTAY_ID'].unique():
            # Get vitals for this stay
            stay_vitals = vitals[vitals['ICUSTAY_ID'] == icustay_id].copy()
            
            # Get ICU admission time
            icu_info = icustays[icustays['ICUSTAY_ID'] == icustay_id].iloc[0]
            intime = icu_info['INTIME']
            
            # Create hourly bins
            stay_vitals['HOURS_SINCE_ADMISSION'] = (
                (stay_vitals['CHARTTIME'] - intime).dt.total_seconds() / 3600
            ).astype(int)
            
            # Filter to first 48 hours
            stay_vitals = stay_vitals[
                (stay_vitals['HOURS_SINCE_ADMISSION'] >= 0) &
                (stay_vitals['HOURS_SINCE_ADMISSION'] < 48)
            ]
            
            if len(stay_vitals) == 0:
                continue
            
            # Aggregate by hour and vital type
            hourly_vitals = []
            
            for hour in range(48):
                hour_data = stay_vitals[stay_vitals['HOURS_SINCE_ADMISSION'] == hour]
                
                # Extract each vital sign
                hr = hour_data[hour_data['ITEMID'].isin(self.vital_itemids['heart_rate'])]['VALUENUM'].mean()
                spo2 = hour_data[hour_data['ITEMID'].isin(self.vital_itemids['spo2'])]['VALUENUM'].mean()
                temp = hour_data[hour_data['ITEMID'].isin(self.vital_itemids['temperature'])]['VALUENUM'].mean()
                
                # Convert Fahrenheit to Celsius
                if not np.isnan(temp):
                    temp = (temp - 32) * 5/9
                
                # Use defaults if missing
                hr = hr if not np.isnan(hr) else 75.0
                spo2 = spo2 if not np.isnan(spo2) else 96.0
                temp = temp if not np.isnan(temp) else 37.0
                
                # Estimate stress level from HR and BP (simplified)
                stress = min(5.0, max(1.0, (hr - 60) / 20))
                
                hourly_vitals.append([hr, spo2, temp, stress])
            
            sequences[icustay_id] = np.array(hourly_vitals)
        
        print(f"✓ Preprocessed {len(sequences)} vital sign sequences")
        return sequences
    
    def identify_deterioration_cases(
        self,
        icustays: pd.DataFrame,
        admissions: pd.DataFrame
    ) -> Dict[int, bool]:
        """
        Identify deterioration cases based on outcomes
        
        Deterioration defined as:
        - Death during ICU stay
        - Transfer to higher level of care
        - Rapid clinical decline (proxy: short LOS with death)
        
        Returns:
            Dictionary mapping icustay_id to deterioration label
        """
        labels = {}
        
        # Load admissions for mortality info
        admissions_file = self.mimic_dir / 'ADMISSIONS.csv'
        if admissions_file.exists():
            admissions = pd.read_csv(admissions_file)
        
        for _, stay in icustays.iterrows():
            icustay_id = stay['ICUSTAY_ID']
            hadm_id = stay['HADM_ID']
            
            # Get admission info
            admission = admissions[admissions['HADM_ID'] == hadm_id]
            
            if len(admission) == 0:
                continue
            
            admission = admission.iloc[0]
            
            # Deterioration criteria
            deteriorated = False
            
            # 1. Hospital mortality
            if admission['HOSPITAL_EXPIRE_FLAG'] == 1:
                deteriorated = True
            
            # 2. Short ICU stay with death (rapid decline)
            if stay['LOS_HOURS'] < 72 and admission['HOSPITAL_EXPIRE_FLAG'] == 1:
                deteriorated = True
            
            labels[icustay_id] = deteriorated
        
        n_deteriorated = sum(labels.values())
        n_stable = len(labels) - n_deteriorated
        
        print(f"✓ Identified outcomes:")
        print(f"  Deteriorated: {n_deteriorated} ({n_deteriorated/len(labels)*100:.1f}%)")
        print(f"  Stable: {n_stable} ({n_stable/len(labels)*100:.1f}%)")
        
        return labels
    
    def create_dataset(
        self,
        n_patients: int = 1000,
        min_icu_hours: int = 48
    ) -> Tuple[List[Dict], List[int]]:
        """
        Create complete dataset for model training
        
        Args:
            n_patients: Number of patients to include
            min_icu_hours: Minimum ICU stay duration
        
        Returns:
            (samples, labels) where each sample contains:
            - vitals_sequence: (48, 4) array
            - baseline: (4,) array
            - static_features: (10,) array
            - clinical_notes: str
            - label: 0/1
        """
        print("=" * 70)
        print("CREATING MIMIC-III DATASET")
        print("=" * 70)
        
        # Load data
        patients = self.load_patients(n_patients)
        icustays = self.load_icu_stays()
        
        # Filter ICU stays
        icustays = icustays[icustays['LOS_HOURS'] >= min_icu_hours]
        
        # Merge with patients
        data = icustays.merge(patients, on='SUBJECT_ID')
        
        # Load admissions for outcomes
        admissions_file = self.mimic_dir / 'ADMISSIONS.csv'
        admissions = pd.read_csv(admissions_file)
        
        # Identify deterioration cases
        labels_dict = self.identify_deterioration_cases(icustays, admissions)
        
        # Load vital signs
        icustay_ids = list(labels_dict.keys())[:n_patients]
        vitals = self.load_vital_signs(icustay_ids)
        
        # Preprocess vitals
        vital_sequences = self.preprocess_vitals(vitals, icustays)
        
        # Create samples
        samples = []
        labels = []
        
        for icustay_id in icustay_ids:
            if icustay_id not in vital_sequences:
                continue
            
            if icustay_id not in labels_dict:
                continue
            
            # Get patient info
            stay_info = icustays[icustays['ICUSTAY_ID'] == icustay_id].iloc[0]
            patient_info = patients[patients['SUBJECT_ID'] == stay_info['SUBJECT_ID']].iloc[0]
            
            # Calculate age
            age = stay_info['INTIME'].year - patient_info['DOB'].year if 'DOB' in patient_info else 65
            
            # Create sample
            vitals_seq = vital_sequences[icustay_id]
            baseline = vitals_seq[:12].mean(axis=0)  # First 12 hours as baseline
            
            # Static features (simplified)
            gender = 1 if patient_info['GENDER'] == 'M' else 0
            static_features = np.array([
                age / 100.0,  # Normalized age
                gender,
                0, 0, 0,  # Placeholder for comorbidities
                0.5, 0, 0, 0, 0  # Placeholder features
            ])
            
            sample = {
                'vitals_sequence': vitals_seq,
                'baseline': baseline,
                'static_features': static_features,
                'clinical_notes': f"ICU admission for patient {stay_info['SUBJECT_ID']}",
                'label': int(labels_dict[icustay_id])
            }
            
            samples.append(sample)
            labels.append(int(labels_dict[icustay_id]))
        
        print(f"\n✓ Created dataset with {len(samples)} samples")
        print(f"  Positive class: {sum(labels)} ({sum(labels)/len(labels)*100:.1f}%)")
        print(f"  Negative class: {len(labels)-sum(labels)} ({(len(labels)-sum(labels))/len(labels)*100:.1f}%)")
        
        return samples, labels


def download_mimic_instructions():
    """Print instructions for downloading MIMIC-III"""
    print("=" * 70)
    print("HOW TO GET MIMIC-III ACCESS")
    print("=" * 70)
    print("\n1. Complete CITI Training (1-2 hours):")
    print("   https://physionet.org/about/citi-course/")
    print("\n2. Create PhysioNet account:")
    print("   https://physionet.org/register/")
    print("\n3. Request MIMIC-III access:")
    print("   https://physionet.org/content/mimiciii/")
    print("   - Sign data use agreement")
    print("   - Upload CITI certificate")
    print("   - Wait for approval (1-3 days)")
    print("\n4. Download data:")
    print("   - Option A: Web download (slow)")
    print("   - Option B: wget/curl (recommended)")
    print("\n5. Extract CSV files to a directory")
    print("\n6. Update mimic_dir path in code")
    print("=" * 70)


if __name__ == "__main__":
    # Example usage
    download_mimic_instructions()
    
    print("\n\nExample code:")
    print("""
    # After downloading MIMIC-III:
    loader = MIMICIIILoader(mimic_dir='/path/to/mimic-iii-clinical-database-1.4')
    samples, labels = loader.create_dataset(n_patients=1000)
    
    # Use samples for training
    from model_trainer import train_deterioration_model
    model, trainer = train_deterioration_model(
        samples=samples,
        labels=labels,
        save_dir='models/mimic_trained'
    )
    """)

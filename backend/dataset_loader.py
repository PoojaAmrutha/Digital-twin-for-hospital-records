# ============================================================================
# FILE: backend/dataset_loader.py
# Dataset Loading and Processing Utilities
# ============================================================================

import pandas as pd
import numpy as np
import os
from typing import Optional


class DatasetLoader:
    """
    Utility class for loading and processing health monitoring datasets
    Supports WESAD, Apple Watch, and Fitbit datasets
    """
    
    @staticmethod
    def load_wesad_dataset(filepath: str) -> pd.DataFrame:
        """
        Load WESAD (Wearable Stress and Affect Detection) dataset
        
        Args:
            filepath: Path to WESAD CSV file
            
        Returns:
            DataFrame with processed WESAD data
        """
        print(f"📂 Loading WESAD dataset from: {filepath}")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"WESAD dataset not found: {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            
            # Expected columns in WESAD dataset
            expected_columns = ['heart_rate', 'temperature', 'stress_level']
            
            # Map WESAD columns to our schema
            processed = pd.DataFrame()
            
            # Heart Rate
            if 'HR' in df.columns:
                processed['heart_rate'] = df['HR']
            elif 'heart_rate' in df.columns:
                processed['heart_rate'] = df['heart_rate']
            else:
                processed['heart_rate'] = 72  # Default
            
            # Temperature
            if 'TEMP' in df.columns:
                processed['temperature'] = df['TEMP']
            elif 'temperature' in df.columns:
                processed['temperature'] = df['temperature']
            else:
                processed['temperature'] = 36.8  # Default
            
            # Stress Level (from labels)
            if 'stress_label' in df.columns:
                # Map stress labels: 0=baseline(1.0), 1=stress(3.5), 2=amusement(1.5)
                stress_mapping = {0: 1.0, 1: 3.5, 2: 1.5}
                processed['stress_level'] = df['stress_label'].map(stress_mapping)
            elif 'stress_level' in df.columns:
                processed['stress_level'] = df['stress_level']
            else:
                processed['stress_level'] = 2.0  # Default
            
            # SpO2 (not in WESAD, use default)
            processed['spo2'] = 98.0
            
            # Activity data (defaults)
            processed['steps'] = 0
            processed['calories'] = 0
            processed['sleep_hours'] = 7.5
            
            # Timestamp
            if 'timestamp' in df.columns:
                processed['timestamp'] = pd.to_datetime(df['timestamp'])
            
            print(f"✅ WESAD dataset loaded: {len(processed)} records")
            print(f"   Columns: {list(processed.columns)}")
            
            return processed
            
        except Exception as e:
            print(f"❌ Error loading WESAD dataset: {e}")
            raise
    
    @staticmethod
    def load_apple_watch_dataset(filepath: str) -> pd.DataFrame:
        """
        Load Apple Watch Health dataset
        
        Args:
            filepath: Path to Apple Watch CSV file
            
        Returns:
            DataFrame with processed Apple Watch data
        """
        print(f"📂 Loading Apple Watch dataset from: {filepath}")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Apple Watch dataset not found: {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            
            processed = pd.DataFrame()
            
            # Heart Rate
            processed['heart_rate'] = df.get('heart_rate', 72)
            
            # SpO2
            processed['spo2'] = df.get('spo2', 98)
            
            # Temperature (may not be in Apple Watch data)
            processed['temperature'] = 36.8
            
            # Stress Level (estimated from HRV if available)
            if 'hrv' in df.columns:
                # Lower HRV = Higher stress (inverse relationship)
                # Normalize HRV to stress scale (0-5)
                hrv = df['hrv']
                processed['stress_level'] = 5 - ((hrv - hrv.min()) / (hrv.max() - hrv.min()) * 5)
            else:
                processed['stress_level'] = 2.0
            
            # Activity data
            processed['steps'] = df.get('steps', df.get('total_steps', 0))
            processed['calories'] = df.get('calories', 0)
            processed['sleep_hours'] = 7.5
            
            # Timestamp
            if 'timestamp' in df.columns:
                processed['timestamp'] = pd.to_datetime(df['timestamp'])
            
            print(f"✅ Apple Watch dataset loaded: {len(processed)} records")
            print(f"   Columns: {list(processed.columns)}")
            
            return processed
            
        except Exception as e:
            print(f"❌ Error loading Apple Watch dataset: {e}")
            raise
    
    @staticmethod
    def load_fitbit_dataset(filepath: str) -> pd.DataFrame:
        """
        Load Fitbit Activity + Sleep dataset
        
        Args:
            filepath: Path to Fitbit CSV file
            
        Returns:
            DataFrame with processed Fitbit data
        """
        print(f"📂 Loading Fitbit dataset from: {filepath}")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Fitbit dataset not found: {filepath}")
        
        try:
            df = pd.read_csv(filepath)
            
            processed = pd.DataFrame()
            
            # Heart Rate (use resting or average)
            if 'resting_heart_rate' in df.columns:
                processed['heart_rate'] = df['resting_heart_rate']
            elif 'avg_heart_rate' in df.columns:
                processed['heart_rate'] = df['avg_heart_rate']
            else:
                processed['heart_rate'] = 72
            
            # SpO2 (not typically in Fitbit data)
            processed['spo2'] = 98
            
            # Temperature (not in Fitbit data)
            processed['temperature'] = 36.8
            
            # Stress Level (estimated from activity and sleep)
            if 'total_sleep_hours' in df.columns and 'active_minutes' in df.columns:
                sleep = df['total_sleep_hours']
                activity = df['active_minutes']
                # Poor sleep or low activity = higher stress
                stress = 2.5 - (sleep - 7) * 0.2 + (60 - activity) * 0.01
                processed['stress_level'] = np.clip(stress, 0, 5)
            else:
                processed['stress_level'] = 2.0
            
            # Activity data
            processed['steps'] = df.get('steps', 0)
            processed['calories'] = df.get('calories', 0)
            processed['sleep_hours'] = df.get('total_sleep_hours', 7.5)
            
            # Date/Timestamp
            if 'date' in df.columns:
                processed['timestamp'] = pd.to_datetime(df['date'])
            
            print(f"✅ Fitbit dataset loaded: {len(processed)} records")
            print(f"   Columns: {list(processed.columns)}")
            
            return processed
            
        except Exception as e:
            print(f"❌ Error loading Fitbit dataset: {e}")
            raise
    
    @staticmethod
    def create_sample_dataset(num_samples: int = 1000, seed: int = 42) -> pd.DataFrame:
        """
        Create a synthetic sample dataset for testing
        
        Args:
            num_samples: Number of samples to generate
            seed: Random seed for reproducibility
            
        Returns:
            DataFrame with synthetic health data
        """
        print(f"🔧 Creating sample dataset with {num_samples} samples...")
        
        np.random.seed(seed)
        
        data = {
            'heart_rate': np.random.normal(75, 12, num_samples),
            'spo2': np.random.normal(98, 1.5, num_samples),
            'temperature': np.random.normal(36.8, 0.3, num_samples),
            'stress_level': np.random.normal(2.5, 1.0, num_samples),
            'steps': np.random.randint(0, 15000, num_samples),
            'calories': np.random.randint(0, 3000, num_samples),
            'sleep_hours': np.random.normal(7.5, 1.5, num_samples)
        }
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Clip values to realistic ranges
        df['heart_rate'] = np.clip(df['heart_rate'], 40, 180)
        df['spo2'] = np.clip(df['spo2'], 85, 100)
        df['temperature'] = np.clip(df['temperature'], 35, 40)
        df['stress_level'] = np.clip(df['stress_level'], 0, 5)
        df['sleep_hours'] = np.clip(df['sleep_hours'], 0, 12)
        
        # Add some anomalies (5%)
        num_anomalies = int(num_samples * 0.05)
        anomaly_indices = np.random.choice(num_samples, num_anomalies, replace=False)
        
        for idx in anomaly_indices:
            anomaly_type = np.random.choice(['hr_high', 'hr_low', 'spo2_low', 'temp_high'])
            
            if anomaly_type == 'hr_high':
                df.loc[idx, 'heart_rate'] = np.random.uniform(140, 180)
            elif anomaly_type == 'hr_low':
                df.loc[idx, 'heart_rate'] = np.random.uniform(35, 45)
            elif anomaly_type == 'spo2_low':
                df.loc[idx, 'spo2'] = np.random.uniform(80, 88)
            elif anomaly_type == 'temp_high':
                df.loc[idx, 'temperature'] = np.random.uniform(38.5, 40)
        
        print(f"✅ Sample dataset created: {len(df)} records")
        print(f"   Anomalies injected: {num_anomalies}")
        
        return df
    
    @staticmethod
    def preprocess_for_ml(df: pd.DataFrame) -> np.ndarray:
        """
        Preprocess dataset for machine learning
        
        Args:
            df: DataFrame with health data
            
        Returns:
            NumPy array ready for ML models
        """
        print("🔧 Preprocessing data for ML...")
        
        # Select features for ML
        feature_columns = ['heart_rate', 'spo2', 'temperature', 'stress_level']
        
        # Extract features
        features = df[feature_columns].values
        
        # Handle missing values
        features = np.nan_to_num(features, nan=0.0)
        
        print(f"✅ Preprocessed data shape: {features.shape}")
        
        return features
    
    @staticmethod
    def load_any_dataset(filepath: str) -> pd.DataFrame:
        """
        Auto-detect and load any supported dataset
        
        Args:
            filepath: Path to dataset file
            
        Returns:
            Processed DataFrame
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Dataset not found: {filepath}")
        
        # Detect dataset type from path
        if 'wesad' in filepath.lower():
            return DatasetLoader.load_wesad_dataset(filepath)
        elif 'apple' in filepath.lower() or 'watch' in filepath.lower():
            return DatasetLoader.load_apple_watch_dataset(filepath)
        elif 'fitbit' in filepath.lower():
            return DatasetLoader.load_fitbit_dataset(filepath)
        else:
            print("⚠️  Unknown dataset type, loading as generic CSV")
            df = pd.read_csv(filepath)
            return df
    
    @staticmethod
    def get_dataset_info(df: pd.DataFrame) -> dict:
        """
        Get information about a dataset
        
        Args:
            df: DataFrame to analyze
            
        Returns:
            Dictionary with dataset statistics
        """
        info = {
            'num_records': len(df),
            'num_features': len(df.columns),
            'columns': list(df.columns),
            'missing_values': df.isnull().sum().to_dict(),
            'statistics': df.describe().to_dict()
        }
        
        return info


# Test function
if __name__ == "__main__":
    print("=" * 60)
    print("DATASET LOADER TEST")
    print("=" * 60)
    print()
    
    # Test sample dataset creation
    print("Testing sample dataset creation...")
    sample_df = DatasetLoader.create_sample_dataset(100)
    print()
    
    # Display sample data
    print("Sample data (first 5 rows):")
    print(sample_df.head())
    print()
    
    # Dataset info
    info = DatasetLoader.get_dataset_info(sample_df)
    print(f"Dataset info:")
    print(f"  Records: {info['num_records']}")
    print(f"  Features: {info['num_features']}")
    print(f"  Columns: {info['columns']}")
    print()
    
    # Preprocess for ML
    ml_data = DatasetLoader.preprocess_for_ml(sample_df)
    print(f"ML-ready data shape: {ml_data.shape}")
    print()
    
    print("✅ Dataset loader test completed!")
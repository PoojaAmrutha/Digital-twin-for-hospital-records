
# ============================================================================
# 1. data_simulator.py - Simulates Smartwatch Data Streaming
# ============================================================================
"""
This script simulates real-time data from a smartwatch by reading
datasets and streaming data to the API every 5 seconds.
"""

import requests
import time
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class SmartWatchSimulator:
    """Simulates smartwatch data streaming"""
    
    def __init__(self, api_url="http://localhost:8000", user_id=1):
        self.api_url = api_url
        self.user_id = user_id
        self.base_vitals = {
            'heart_rate': 72,
            'spo2': 98,
            'temperature': 36.8,
            'stress_level': 2.0,
            'steps': 0,
            'calories': 0,
            'sleep_hours': 7.5
        }
    
    def generate_realistic_vitals(self, hour_of_day):
        """Generate realistic vitals based on time of day"""
        vitals = self.base_vitals.copy()
        
        # Heart rate varies by activity and time
        if 6 <= hour_of_day <= 22:  # Awake hours
            vitals['heart_rate'] = np.random.normal(75, 10)
            if random.random() < 0.1:  # 10% chance of exercise
                vitals['heart_rate'] = np.random.normal(120, 15)
        else:  # Sleeping hours
            vitals['heart_rate'] = np.random.normal(60, 5)
        
        # SpO2 is generally stable
        vitals['spo2'] = np.random.normal(98, 1.5)
        vitals['spo2'] = np.clip(vitals['spo2'], 90, 100)
        
        # Temperature slight variations
        vitals['temperature'] = np.random.normal(36.8, 0.3)
        
        # Stress varies during day
        if 9 <= hour_of_day <= 17:  # Work hours
            vitals['stress_level'] = np.random.normal(3.0, 0.8)
        elif 18 <= hour_of_day <= 22:  # Evening
            vitals['stress_level'] = np.random.normal(2.0, 0.5)
        else:  # Night/early morning
            vitals['stress_level'] = np.random.normal(1.0, 0.3)
        
        vitals['stress_level'] = np.clip(vitals['stress_level'], 0, 5)
        
        # Steps accumulate during day
        if 6 <= hour_of_day <= 22:
            vitals['steps'] += random.randint(50, 200)
        
        # Calories based on steps
        vitals['calories'] = int(vitals['steps'] * 0.04)
        
        return vitals
    
    def simulate_anomaly(self, vitals, anomaly_type='cardiac'):
        """Inject anomalies for testing alert system"""
        if anomaly_type == 'cardiac':
            vitals['heart_rate'] = random.choice([140, 35])  # Too high or low
        elif anomaly_type == 'respiratory':
            vitals['spo2'] = random.randint(85, 90)  # Low oxygen
        elif anomaly_type == 'fever':
            vitals['temperature'] = random.uniform(38.5, 39.5)  # High fever
        elif anomaly_type == 'stress':
            vitals['stress_level'] = random.uniform(4.5, 5.0)  # Extreme stress
        
        return vitals
    
    def stream_data(self, duration_minutes=60, interval_seconds=5):
        """Stream data to API for specified duration"""
        print(f"🚀 Starting smartwatch simulation for user {self.user_id}")
        print(f"📡 Streaming to: {self.api_url}")
        print(f"⏱️  Duration: {duration_minutes} minutes")
        print(f"🔄 Interval: {interval_seconds} seconds")
        print("-" * 60)
        
        iterations = (duration_minutes * 60) // interval_seconds
        
        for i in range(iterations):
            # Current time
            current_time = datetime.now()
            hour = current_time.hour
            
            # Generate vitals
            vitals = self.generate_realistic_vitals(hour)
            
            # Occasionally inject anomalies for testing (5% chance)
            if random.random() < 0.05:
                anomaly_type = random.choice(['cardiac', 'respiratory', 'fever', 'stress'])
                vitals = self.simulate_anomaly(vitals, anomaly_type)
                print(f"⚠️  Injected {anomaly_type} anomaly")
            
            # Prepare payload
            payload = {
                'user_id': self.user_id,
                'heart_rate': round(vitals['heart_rate'], 1),
                'spo2': round(vitals['spo2'], 1),
                'temperature': round(vitals['temperature'], 2),
                'stress_level': round(vitals['stress_level'], 2),
                'steps': int(vitals['steps']),
                'calories': int(vitals['calories']),
                'sleep_hours': round(vitals['sleep_hours'], 1)
            }
            
            # Send to API
            try:
                response = requests.post(
                    f"{self.api_url}/vitals/",
                    json=payload
                )
                
                if response.status_code == 200:
                    print(f"✅ [{i+1}/{iterations}] {current_time.strftime('%H:%M:%S')} | "
                          f"HR: {payload['heart_rate']} | SpO2: {payload['spo2']}% | "
                          f"Temp: {payload['temperature']}°C")
                else:
                    print(f"❌ Error: {response.status_code}")
            
            except Exception as e:
                print(f"❌ Connection error: {e}")
            
            # Wait before next reading
            time.sleep(interval_seconds)
        
        print("-" * 60)
        print("✅ Simulation completed!")


# ============================================================================
# 2. dataset_loader.py - Load Real Datasets
# ============================================================================
"""
Load and prepare real smartwatch datasets for simulation
Supports WESAD, Apple Watch, and Fitbit datasets
"""

class DatasetLoader:
    """Load and process health monitoring datasets"""
    
    @staticmethod
    def load_wesad_dataset(filepath):
        """
        Load WESAD (Wearable Stress and Affect Detection) dataset
        Contains: HR, EDA, Temperature, Respiration
        """
        df = pd.read_csv(filepath)
        
        # Map WESAD columns to our schema
        processed = pd.DataFrame({
            'heart_rate': df['HR'] if 'HR' in df.columns else df.get('heart_rate', 72),
            'temperature': df['TEMP'] if 'TEMP' in df.columns else df.get('temperature', 36.8),
            'stress_level': df['label'].map({0: 1.0, 1: 2.5, 2: 4.0}) if 'label' in df.columns else 2.0,
            'spo2': 98,  # Not in WESAD, use default
            'steps': 0,
            'calories': 0,
            'sleep_hours': 7.5
        })
        
        return processed
    
    @staticmethod
    def load_apple_watch_dataset(filepath):
        """
        Load Apple Watch Health dataset
        Contains: HR, HRV, Sleep, Steps, VO2
        """
        df = pd.read_csv(filepath)
        
        processed = pd.DataFrame({
            'heart_rate': df['heart_rate'] if 'heart_rate' in df.columns else 72,
            'spo2': df['spo2'] if 'spo2' in df.columns else 98,
            'temperature': 36.8,
            'stress_level': 2.0,
            'steps': df['steps'] if 'steps' in df.columns else 0,
            'calories': df['calories'] if 'calories' in df.columns else 0,
            'sleep_hours': df['sleep_hours'] if 'sleep_hours' in df.columns else 7.5
        })
        
        return processed
    
    @staticmethod
    def load_fitbit_dataset(filepath):
        """
        Load Fitbit Activity + Sleep dataset
        Contains: Steps, Calories, Sleep stages, HR
        """
        df = pd.read_csv(filepath)
        
        processed = pd.DataFrame({
            'heart_rate': df['heart_rate'] if 'heart_rate' in df.columns else 72,
            'spo2': 98,
            'temperature': 36.8,
            'stress_level': 2.0,
            'steps': df['steps'] if 'steps' in df.columns else 0,
            'calories': df['calories'] if 'calories' in df.columns else 0,
            'sleep_hours': df['total_sleep_hours'] if 'total_sleep_hours' in df.columns else 7.5
        })
        
        return processed
    
    @staticmethod
    def create_sample_dataset(num_samples=1000):
        """Create a sample dataset for testing"""
        np.random.seed(42)
        
        data = {
            'heart_rate': np.random.normal(75, 12, num_samples),
            'spo2': np.random.normal(98, 1.5, num_samples),
            'temperature': np.random.normal(36.8, 0.3, num_samples),
            'stress_level': np.random.normal(2.5, 1.0, num_samples),
            'steps': np.random.randint(0, 15000, num_samples),
            'calories': np.random.randint(0, 3000, num_samples),
            'sleep_hours': np.random.normal(7.5, 1.5, num_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Add some anomalies (5%)
        anomaly_indices = np.random.choice(num_samples, int(num_samples * 0.05), replace=False)
        df.loc[anomaly_indices, 'heart_rate'] = np.random.choice([140, 40], len(anomaly_indices))
        
        return df


# ============================================================================
# 3. init_db.py - Database Initialization Script
# ============================================================================
"""
Initialize database with tables and sample data
"""

from sqlalchemy import create_engine, text
from database import Base, engine
from models import User, VitalReading, Alert, HealthScore
import random

def init_database():
    """Create all tables"""
    print("🗄️  Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")


def seed_sample_data():
    """Add sample users and data"""
    from sqlalchemy.orm import Session
    
    session = Session(bind=engine)
    
    print("🌱 Seeding sample data...")
    
    # Create sample users
    users = [
        User(name="John Doe", email="john@example.com", age=45, gender="M", user_type="patient"),
        User(name="Jane Smith", email="jane@example.com", age=62, gender="F", user_type="patient"),
        User(name="Bob Johnson", email="bob@example.com", age=38, gender="M", user_type="patient"),
        User(name="Alice Brown", email="alice@example.com", age=71, gender="F", user_type="patient"),
        User(name="Charlie Davis", email="charlie@example.com", age=29, gender="M", user_type="patient"),
        User(name="Dr. Sarah Wilson", email="sarah@hospital.com", age=42, gender="F", user_type="doctor"),
    ]
    
    for user in users:
        session.add(user)
    
    session.commit()
    print(f"✅ Created {len(users)} sample users")
    
    # Create sample vital readings for each patient
    for user in users[:5]:  # Only patients
        for i in range(20):
            vital = VitalReading(
                user_id=user.id,
                heart_rate=random.uniform(60, 100),
                spo2=random.uniform(95, 100),
                temperature=random.uniform(36.5, 37.2),
                stress_level=random.uniform(1, 3),
                steps=random.randint(0, 10000),
                calories=random.randint(0, 2500),
                sleep_hours=random.uniform(6, 9)
            )
            session.add(vital)
    
    session.commit()
    print("✅ Created sample vital readings")
    
    session.close()
    print("🎉 Database seeding completed!")


def reset_database():
    """Drop and recreate all tables"""
    print("⚠️  Resetting database...")
    Base.metadata.drop_all(bind=engine)
    init_database()
    print("✅ Database reset completed!")


# ============================================================================
# 4. train_models.py - Train ML Models
# ============================================================================
"""
Train and save machine learning models
"""

from ml_models import AnomalyDetector
import numpy as np

def train_anomaly_detector():
    """Train the anomaly detection model with sample data"""
    print("🤖 Training anomaly detection model...")
    
    # Generate training data (normal vitals)
    normal_data = []
    for _ in range(1000):
        normal_data.append([
            np.random.normal(75, 10),   # heart_rate
            np.random.normal(98, 1),    # spo2
            np.random.normal(36.8, 0.2), # temperature
            np.random.normal(2, 0.5)     # stress
        ])
    
    normal_data = np.array(normal_data)
    
    # Train model
    detector = AnomalyDetector()
    detector.train(normal_data)
    
    # Save model
    detector.save('models/anomaly_detector.pkl')
    print("✅ Anomaly detector trained and saved!")
    
    return detector


# ============================================================================
# 5. run_simulation.py - Main Simulation Script
# ============================================================================
"""
Main script to run the complete simulation
"""

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='HealthWatch AI Data Simulator')
    parser.add_argument('--mode', choices=['init', 'simulate', 'train', 'reset'], 
                       required=True, help='Operation mode')
    parser.add_argument('--user_id', type=int, default=1, help='User ID for simulation')
    parser.add_argument('--duration', type=int, default=60, help='Duration in minutes')
    parser.add_argument('--interval', type=int, default=5, help='Interval in seconds')
    parser.add_argument('--api_url', default='http://localhost:8000', help='API URL')
    
    args = parser.parse_args()
    
    if args.mode == 'init':
        print("=" * 60)
        print("DATABASE INITIALIZATION")
        print("=" * 60)
        init_database()
        seed_sample_data()
    
    elif args.mode == 'reset':
        print("=" * 60)
        print("DATABASE RESET")
        print("=" * 60)
        reset_database()
        seed_sample_data()
    
    elif args.mode == 'train':
        print("=" * 60)
        print("MODEL TRAINING")
        print("=" * 60)
        import os
        os.makedirs('models', exist_ok=True)
        train_anomaly_detector()
    
    elif args.mode == 'simulate':
        print("=" * 60)
        print("SMARTWATCH DATA SIMULATION")
        print("=" * 60)
        simulator = SmartWatchSimulator(
            api_url=args.api_url,
            user_id=args.user_id
        )
        simulator.stream_data(
            duration_minutes=args.duration,
            interval_seconds=args.interval
        )


# ============================================================================
# USAGE EXAMPLES:
# ============================================================================

"""
# 1. Initialize database
python run_simulation.py --mode init

# 2. Train ML models
python run_simulation.py --mode train

# 3. Run simulation for user 1 for 30 minutes
python run_simulation.py --mode simulate --user_id 1 --duration 30

# 4. Run simulation with custom interval (every 3 seconds)
python run_simulation.py --mode simulate --user_id 1 --duration 60 --interval 3

# 5. Reset database (careful!)
python run_simulation.py --mode reset
"""
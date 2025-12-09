# ============================================================================
# FILE: backend/run_simulation.py
# Main Simulation and Management Script
# ============================================================================

import argparse
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Base, engine, SessionLocal, init_db, reset_db
from models import User, VitalReading, HealthScore
from data_similator import SmartWatchSimulator
from dataset_loader import DatasetLoader
from ml_models import AnomalyDetector
import numpy as np


def init_database():
    """Initialize database with tables and sample data"""
    print("=" * 60)
    print("DATABASE INITIALIZATION")
    print("=" * 60)
    print()
    
    print("🗄️  Creating database tables...")
    init_db()
    print("✅ Tables created successfully!")
    print()
    
    # Create sample users
    print("👥 Creating sample users...")
    session = SessionLocal()
    
    try:
        # Check if users already exist
        existing_users = session.query(User).count()
        
        if existing_users == 0:
            sample_users = [
                User(name="John Doe", email="john@example.com", age=45, gender="M", user_type="patient"),
                User(name="Jane Smith", email="jane@example.com", age=62, gender="F", user_type="patient"),
                User(name="Bob Johnson", email="bob@example.com", age=38, gender="M", user_type="patient"),
                User(name="Alice Brown", email="alice@example.com", age=71, gender="F", user_type="patient"),
                User(name="Charlie Davis", email="charlie@example.com", age=29, gender="M", user_type="patient"),
                User(name="Dr. Sarah Wilson", email="sarah@hospital.com", age=42, gender="F", user_type="doctor"),
            ]
            
            for user in sample_users:
                session.add(user)
            
            session.commit()
            print(f"✅ Created {len(sample_users)} sample users")
        else:
            print(f"ℹ️  Database already has {existing_users} users")
        
    except Exception as e:
        print(f"❌ Error creating users: {e}")
        session.rollback()
    finally:
        session.close()
    
    print()
    print("=" * 60)
    print("DATABASE INITIALIZATION COMPLETED!")
    print("=" * 60)


def reset_database():
    """Reset database (WARNING: Deletes all data!)"""
    print("=" * 60)
    print("DATABASE RESET")
    print("=" * 60)
    print()
    
    print("⚠️  WARNING: This will delete ALL data!")
    confirm = input("Type 'YES' to confirm: ")
    
    if confirm == "YES":
        print()
        print("🗑️  Dropping all tables...")
        reset_db()
        print("✅ Database reset completed!")
        print()
        
        # Re-initialize
        init_database()
    else:
        print("❌ Reset cancelled")


def train_models():
    """Train machine learning models"""
    print("=" * 60)
    print("MACHINE LEARNING MODEL TRAINING")
    print("=" * 60)
    print()
    
    # Create models directory
    os.makedirs('models', exist_ok=True)
    
    print("🤖 Training anomaly detection model...")
    print()
    
    # Generate training data
    print("📊 Generating training data...")
    df = DatasetLoader.create_sample_dataset(num_samples=1000, seed=42)
    training_data = DatasetLoader.preprocess_for_ml(df)
    
    print(f"   Training samples: {len(training_data)}")
    print(f"   Features: {training_data.shape[1]}")
    print()
    
    # Train anomaly detector
    print("🔧 Training Isolation Forest model...")
    detector = AnomalyDetector()
    detector.train(training_data)
    
    # Save model
    model_path = 'models/anomaly_detector.pkl'
    detector.save(model_path)
    print(f"💾 Model saved to: {model_path}")
    print()
    
    # Test the model
    print("🧪 Testing model...")
    
    # Test with normal vitals
    normal_vitals = {
        'heart_rate': 75,
        'spo2': 98,
        'temperature': 36.8,
        'stress_level': 2.0
    }
    
    is_anomaly = detector.predict(normal_vitals)
    print(f"   Normal vitals → Anomaly: {is_anomaly}")
    
    # Test with abnormal vitals
    abnormal_vitals = {
        'heart_rate': 150,
        'spo2': 85,
        'temperature': 39.5,
        'stress_level': 4.8
    }
    
    is_anomaly = detector.predict(abnormal_vitals)
    print(f"   Abnormal vitals → Anomaly: {is_anomaly}")
    print()
    
    print("=" * 60)
    print("MODEL TRAINING COMPLETED!")
    print("=" * 60)


def run_simulation(user_id: int = 1, duration: int = 60, interval: int = 5, api_url: str = "http://localhost:8000"):
    """Run smartwatch data simulation"""
    print("=" * 60)
    print("SMARTWATCH DATA SIMULATION")
    print("=" * 60)
    print()
    
    print(f"📱 Configuration:")
    print(f"   User ID: {user_id}")
    print(f"   Duration: {duration} minutes")
    print(f"   Interval: {interval} seconds")
    print(f"   API URL: {api_url}")
    print()
    
    # Check if API is accessible
    try:
        import requests
        response = requests.get(api_url, timeout=5)
        if response.status_code == 200:
            print("✅ API connection successful")
        else:
            print(f"⚠️  API returned status code: {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("   Please ensure the backend is running:")
        print("   uvicorn main:app --reload")
        return
    
    print()
    
    # Start simulation
    simulator = SmartWatchSimulator(api_url=api_url, user_id=user_id)
    simulator.stream_data(duration_minutes=duration, interval_seconds=interval)


def show_stats():
    """Show database statistics"""
    print("=" * 60)
    print("DATABASE STATISTICS")
    print("=" * 60)
    print()
    
    session = SessionLocal()
    
    try:
        # User stats
        total_users = session.query(User).count()
        patients = session.query(User).filter(User.user_type == "patient").count()
        doctors = session.query(User).filter(User.user_type == "doctor").count()
        
        print(f"👥 Users:")
        print(f"   Total: {total_users}")
        print(f"   Patients: {patients}")
        print(f"   Doctors: {doctors}")
        print()
        
        # Vitals stats
        total_vitals = session.query(VitalReading).count()
        print(f"💓 Vital Readings: {total_vitals}")
        print()
        
        # Health scores
        total_scores = session.query(HealthScore).count()
        print(f"📊 Health Scores: {total_scores}")
        print()
        
        # Recent data
        if total_vitals > 0:
            recent = session.query(VitalReading).order_by(VitalReading.timestamp.desc()).first()
            print(f"📅 Most Recent Reading:")
            print(f"   User ID: {recent.user_id}")
            print(f"   Heart Rate: {recent.heart_rate:.1f} bpm")
            print(f"   SpO2: {recent.spo2:.1f}%")
            print(f"   Temperature: {recent.temperature:.1f}°C")
            print(f"   Timestamp: {recent.timestamp}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        session.close()
    
    print()
    print("=" * 60)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='HealthWatch AI - Simulation and Management Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Initialize database
  python run_simulation.py --mode init
  
  # Train ML models
  python run_simulation.py --mode train
  
  # Run simulation for user 1 for 60 minutes
  python run_simulation.py --mode simulate --user_id 1 --duration 60
  
  # Show database statistics
  python run_simulation.py --mode stats
  
  # Reset database (WARNING: deletes all data!)
  python run_simulation.py --mode reset
        """
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        required=True,
        choices=['init', 'reset', 'train', 'simulate', 'stats'],
        help='Operation mode'
    )
    
    parser.add_argument(
        '--user_id',
        type=int,
        default=1,
        help='User ID for simulation (default: 1)'
    )
    
    parser.add_argument(
        '--duration',
        type=int,
        default=60,
        help='Simulation duration in minutes (default: 60)'
    )
    
    parser.add_argument(
        '--interval',
        type=int,
        default=5,
        help='Data streaming interval in seconds (default: 5)'
    )
    
    parser.add_argument(
        '--api_url',
        type=str,
        default='http://localhost:8000',
        help='API URL (default: http://localhost:8000)'
    )
    
    args = parser.parse_args()
    
    # Execute based on mode
    if args.mode == 'init':
        init_database()
    
    elif args.mode == 'reset':
        reset_database()
    
    elif args.mode == 'train':
        train_models()
    
    elif args.mode == 'simulate':
        run_simulation(
            user_id=args.user_id,
            duration=args.duration,
            interval=args.interval,
            api_url=args.api_url
        )
    
    elif args.mode == 'stats':
        show_stats()


if __name__ == "__main__":
    main()
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder
import joblib
import os

# Create models directory
os.makedirs('models', exist_ok=True)

def generate_synthetic_data(n_samples=5000):
    """Generate synthetic patient data for training"""
    np.random.seed(42)
    
    data = {
        'age': np.random.randint(18, 95, n_samples),
        'gender': np.random.choice(['M', 'F'], n_samples),
        'bmi': np.random.normal(25, 5, n_samples),
        'systolic_bp': np.random.normal(120, 15, n_samples),
        'diastolic_bp': np.random.normal(80, 10, n_samples),
        'heart_rate': np.random.normal(75, 12, n_samples),
        'spo2': np.random.normal(97, 2, n_samples),
        'has_diabetes': np.random.choice([0, 1], n_samples, p=[0.85, 0.15]),
        'has_hypertension': np.random.choice([0, 1], n_samples, p=[0.75, 0.25]),
        'recent_admissions': np.random.poisson(0.3, n_samples),
        'treatment_type': np.random.choice(['Medication A', 'Medication B', 'Surgery', 'Therapy'], n_samples)
    }
    
    df = pd.DataFrame(data)
    
    # Logic for Readmission Target
    readmission_prob = (
        (df['age'] > 70) * 0.3 + 
        (df['recent_admissions'] > 1) * 0.4 + 
        (df['has_diabetes'] | df['has_hypertension']) * 0.2 +
        (df['systolic_bp'] > 140) * 0.1
    )
    readmission_prob += np.random.normal(0, 0.1, n_samples)
    df['readmission_risk'] = (readmission_prob > 0.5).astype(int)
    
    # Logic for Treatment Success Target
    success_prob = 0.7  # Base rate
    success_prob -= (df['age'] > 80) * 0.2
    success_prob -= (df['bmi'] > 35) * 0.15
    mask_surgery_old = (df['treatment_type'] == 'Surgery') & (df['age'] > 75)
    success_prob[mask_surgery_old] -= 0.3
    success_prob += np.random.normal(0, 0.1, n_samples)
    df['treatment_success'] = (success_prob > 0.5).astype(int)
    
    return df

def train_readmission_model(df):
    print("Training Readmission Risk Model...")
    features = ['age', 'systolic_bp', 'diastolic_bp', 'heart_rate', 'spo2', 
                'has_diabetes', 'has_hypertension', 'recent_admissions']
    target = 'readmission_risk'
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
    model.fit(X_train_scaled, y_train)
    print(f"Readmission Model Accuracy: {model.score(X_test_scaled, y_test):.2f}")
    
    joblib.dump({'model': model, 'scaler': scaler, 'features': features}, 'models/readmission_model.pkl')
    print("Saved models/readmission_model.pkl")

def train_treatment_model(df):
    print("Training Treatment Response Model...")
    le = LabelEncoder()
    df['treatment_type_encoded'] = le.fit_transform(df['treatment_type'])
    features = ['age', 'bmi', 'treatment_type_encoded', 'has_diabetes', 'has_hypertension']
    target = 'treatment_success'
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42)
    model.fit(X_train, y_train)
    print(f"Treatment Model Accuracy: {model.score(X_test, y_test):.2f}")
    
    joblib.dump({'model': model, 'label_encoder': le, 'features': features}, 'models/treatment_model.pkl')
    print("Saved models/treatment_model.pkl")

if __name__ == "__main__":
    print("Generating Synthetic Data...")
    df = generate_synthetic_data()
    train_readmission_model(df)
    train_treatment_model(df)
    print("✅ Training Complete!")

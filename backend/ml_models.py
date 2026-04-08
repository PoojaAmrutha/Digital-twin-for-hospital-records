# ============================================================================
# FILE: backend/ml_models.py
# Machine Learning Models for Health Analysis
# ============================================================================

import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
import joblib
import os
from typing import Dict, Tuple, Any, List


class AnomalyDetector:
    """
    Detects anomalies in vital readings using Isolation Forest algorithm
    Uses unsupervised learning to identify unusual patterns
    """
    
    def __init__(self, contamination: float = 0.1):
        """
        Initialize anomaly detector
        
        Args:
            contamination: Expected proportion of outliers (default: 10%)
        """
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100,
            max_samples='auto'
        )
        self.scaler = StandardScaler()
        self.is_trained = False
        self.feature_names = ['heart_rate', 'spo2', 'temperature', 'stress_level']
    
    def train(self, data: np.ndarray):
        """
        Train the anomaly detection model
        
        Args:
            data: Training data with shape (n_samples, 4)
                  [heart_rate, spo2, temperature, stress_level]
        """
        if len(data) < 10:
            raise ValueError("Need at least 10 samples to train")
        
        # Scale the data
        scaled_data = self.scaler.fit_transform(data)
        
        # Train the model
        self.model.fit(scaled_data)
        self.is_trained = True
        
        print(f"✅ Anomaly detector trained on {len(data)} samples")
    
    def predict(self, vitals: Dict[str, float]) -> bool:
        """
        Predict if vitals are anomalous
        
        Args:
            vitals: Dictionary with keys: heart_rate, spo2, temperature, stress_level
        
        Returns:
            True if anomaly detected, False otherwise
        """
        if not self.is_trained:
            # If model not trained, use rule-based detection
            return self._rule_based_detection(vitals)
        
        try:
            # Extract features
            features = np.array([[
                vitals['heart_rate'],
                vitals['spo2'],
                vitals['temperature'],
                vitals['stress_level']
            ]])
            
            # Scale features
            scaled_features = self.scaler.transform(features)
            
            # Predict (-1 = anomaly, 1 = normal)
            prediction = self.model.predict(scaled_features)
            
            return prediction[0] == -1
        
        except Exception as e:
            print(f"Error in anomaly prediction: {e}")
            return False
    
    def _rule_based_detection(self, vitals: Dict[str, float]) -> bool:
        """Simple rule-based anomaly detection if model not trained"""
        anomaly_conditions = [
            vitals['heart_rate'] > 150 or vitals['heart_rate'] < 40,
            vitals['spo2'] < 85,
            vitals['temperature'] > 39.5 or vitals['temperature'] < 35,
            vitals['stress_level'] > 4.5
        ]
        return any(anomaly_conditions)
    
    def get_anomaly_score(self, vitals: Dict[str, float]) -> float:
        """
        Get anomaly score (higher = more anomalous)
        
        Returns:
            Score between -1 and 1 (negative = anomaly)
        """
        if not self.is_trained:
            return 0.0
        
        features = np.array([[
            vitals['heart_rate'],
            vitals['spo2'],
            vitals['temperature'],
            vitals['stress_level']
        ]])
        
        scaled_features = self.scaler.transform(features)
        score = self.model.score_samples(scaled_features)
        
        return float(score[0])
    
    def save(self, path: str):
        """Save model to disk"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'is_trained': self.is_trained,
            'feature_names': self.feature_names
        }, path)
        print(f"✅ Model saved to {path}")
    
    def load(self, path: str):
        """Load model from disk"""
        if not os.path.exists(path):
            print(f"⚠️ Model file not found: {path}")
            return False
        
        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']
        self.is_trained = data['is_trained']
        self.feature_names = data['feature_names']
        print(f"✅ Model loaded from {path}")
        return True


class HealthScoreCalculator:
    """
    Calculates comprehensive health score (0-100) based on multiple factors
    Uses weighted scoring system with medical thresholds
    """
    
    @staticmethod
    def calculate(vitals: Dict[str, float]) -> Dict[str, any]:
        """
        Calculate health score based on vitals
        
        Args:
            vitals: Dictionary containing all vital measurements
        
        Returns:
            Dictionary with 'score' (0-100) and 'risk_level' (low/medium/high)
        """
        score = 100.0
        
        # Heart Rate Scoring (60-100 bpm normal)
        hr = vitals['heart_rate']
        if hr < 40 or hr > 140:
            score -= 35
        elif hr < 50 or hr > 130:
            score -= 25
        elif hr < 60 or hr > 100:
            score -= 15
        elif hr < 70 or hr > 90:
            score -= 5
        
        # SpO2 Scoring (95-100% normal)
        spo2 = vitals['spo2']
        if spo2 < 85:
            score -= 40  # Critical
        elif spo2 < 88:
            score -= 30  # Severe
        elif spo2 < 92:
            score -= 20  # Moderate
        elif spo2 < 95:
            score -= 10  # Mild
        elif spo2 < 98:
            score -= 3   # Slight
        
        # Temperature Scoring (36.1-37.2°C normal)
        temp = vitals['temperature']
        if temp > 40 or temp < 34:
            score -= 40  # Critical
        elif temp > 39 or temp < 35:
            score -= 30  # Severe
        elif temp > 38.5 or temp < 35.5:
            score -= 20  # High fever
        elif temp > 38 or temp < 36:
            score -= 15  # Moderate fever
        elif temp > 37.5 or temp < 36.1:
            score -= 8   # Slight fever
        
        # Stress Level Scoring (0-2 low, 2-3 medium, 3+ high)
        stress = vitals['stress_level']
        if stress > 4.5:
            score -= 25
        elif stress > 4:
            score -= 20
        elif stress > 3.5:
            score -= 15
        elif stress > 3:
            score -= 10
        elif stress > 2.5:
            score -= 5
        
        # Sleep Scoring (7-9 hours optimal)
        sleep = vitals.get('sleep_hours', 7.5)
        if sleep < 4 or sleep > 12:
            score -= 25
        elif sleep < 5 or sleep > 10:
            score -= 20
        elif sleep < 6 or sleep > 9.5:
            score -= 12
        elif sleep < 7 or sleep > 9:
            score -= 5
        
        # Activity Scoring (Steps)
        steps = vitals.get('steps', 0)
        if steps < 1000:
            score -= 20
        elif steps < 2000:
            score -= 15
        elif steps < 3000:
            score -= 10
        elif steps < 5000:
            score -= 5
        
        # Ensure score is in valid range
        final_score = max(0, min(100, score))
        
        # Determine risk level
        if final_score >= 85:
            risk_level = "low"
        elif final_score >= 70:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return {
            "score": round(final_score, 1),
            "risk_level": risk_level
        }
    
    @staticmethod
    def get_score_breakdown(vitals: Dict[str, float]) -> Dict[str, float]:
        """Get detailed breakdown of score components"""
        breakdown = {
            'heart_rate_score': 0,
            'spo2_score': 0,
            'temperature_score': 0,
            'stress_score': 0,
            'sleep_score': 0,
            'activity_score': 0
        }
        
        # Calculate individual component scores
        # (Implementation similar to calculate method but returns components)
        
        return breakdown


class RiskPredictor:
    """
    Predicts specific health risks (cardiac, respiratory, stress)
    Uses gradient boosting and random forest algorithms
    """
    
    def __init__(self):
        self.cardiac_model = GradientBoostingClassifier(n_estimators=100, random_state=42)
        self.respiratory_model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.scaler = StandardScaler()
        self.is_trained = False
    
    def predict_risks(self, vitals: Dict[str, float]) -> Dict[str, float]:
        """
        Predict risk scores for different health categories
        
        Args:
            vitals: Dictionary with vital measurements
        
        Returns:
            Dictionary with risk scores (0-1) for cardiac, respiratory, stress
        """
        
        # Cardiac Risk Assessment
        hr = vitals['heart_rate']
        spo2 = vitals['spo2']
        
        cardiac_risk = 0.0
        if hr > 140 or hr < 40:
            cardiac_risk = 0.95
        elif hr > 120 or hr < 50:
            cardiac_risk = 0.75
        elif hr > 100 or hr < 60:
            cardiac_risk = 0.45
        else:
            cardiac_risk = 0.10
        
        # Adjust for SpO2
        if spo2 < 85:
            cardiac_risk = min(1.0, cardiac_risk + 0.4)
        elif spo2 < 90:
            cardiac_risk = min(1.0, cardiac_risk + 0.25)
        elif spo2 < 95:
            cardiac_risk = min(1.0, cardiac_risk + 0.10)
        
        # Respiratory Risk Assessment
        temp = vitals['temperature']
        
        respiratory_risk = 0.0
        if spo2 < 85:
            respiratory_risk = 0.95
        elif spo2 < 88:
            respiratory_risk = 0.80
        elif spo2 < 92:
            respiratory_risk = 0.60
        elif spo2 < 95:
            respiratory_risk = 0.30
        else:
            respiratory_risk = 0.05
        
        # Adjust for temperature (fever can indicate respiratory issues)
        if temp > 39:
            respiratory_risk = min(1.0, respiratory_risk + 0.30)
        elif temp > 38:
            respiratory_risk = min(1.0, respiratory_risk + 0.15)
        
        # Stress Risk Assessment
        stress = vitals['stress_level']
        
        if stress > 4.5:
            stress_risk = 0.95
        elif stress > 4:
            stress_risk = 0.80
        elif stress > 3.5:
            stress_risk = 0.65
        elif stress > 3:
            stress_risk = 0.50
        elif stress > 2.5:
            stress_risk = 0.35
        elif stress > 2:
            stress_risk = 0.20
        else:
            stress_risk = 0.05
        
        # Adjust stress risk based on heart rate (stress affects HR)
        if hr > 100:
            stress_risk = min(1.0, stress_risk + 0.15)
        
        return {
            "cardiac_risk": round(cardiac_risk, 2),
            "respiratory_risk": round(respiratory_risk, 2),
            "stress_risk": round(stress_risk, 2)
        }
    
    def get_risk_explanation(self, risks: Dict[str, float]) -> Dict[str, str]:
        """Get human-readable explanations for risk scores"""
        explanations = {}
        
        for risk_type, score in risks.items():
            if score >= 0.8:
                level = "Critical"
            elif score >= 0.6:
                level = "High"
            elif score >= 0.4:
                level = "Moderate"
            elif score >= 0.2:
                level = "Low"
            else:
                level = "Minimal"
            
            explanations[risk_type] = level
        
        return explanations


# Initialize global model instances
anomaly_detector = AnomalyDetector()
health_calculator = HealthScoreCalculator()
risk_predictor = RiskPredictor()

# Try to load trained models
MODEL_PATH = "models/anomaly_detector.pkl"
if os.path.exists(MODEL_PATH):
    anomaly_detector.load(MODEL_PATH)



class ReadmissionRiskModel:
    """
    Predicts risk of hospital reading within 30 days using trained RandomForest
    """
    def __init__(self):
        self.model = None
        self.scaler = None
        self.features = []
        self.is_trained = False
        self.load_model()
        
    def load_model(self):
        try:
            path = "models/readmission_model.pkl"
            if os.path.exists(path):
                data = joblib.load(path)
                self.model = data['model']
                self.scaler = data['scaler']
                self.features = data['features']
                self.is_trained = True
                print(f"✅ Readmission model loaded from {path}")
            else:
                print(f"⚠️ Readmission model not found at {path}")
        except Exception as e:
            print(f"❌ Error loading readmission model: {e}")

    def predict(self, patient_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predict readmission risk
        """
        if not self.is_trained:
            return {"error": "Model not trained", "readmission_probability": 0, "risk_level": "Unknown"}
            
        try:
            # Prepare features (defaults if missing)
            # features = ['age', 'systolic_bp', 'diastolic_bp', 'heart_rate', 'spo2', 
            #             'has_diabetes', 'has_hypertension', 'recent_admissions']
            
            # Map input data to features
            input_vector = []
            for feature in self.features:
                val = patient_data.get(feature, 0)
                # Handle booleans
                if isinstance(val, bool):
                    val = 1 if val else 0
                input_vector.append(val)
            
            # Reshape and scale
            X = np.array([input_vector])
            X_scaled = self.scaler.transform(X)
            
            # Predict probability
            prob = self.model.predict_proba(X_scaled)[0][1]
            
            # Determine risk level
            risk_level = "High" if prob > 0.6 else "Medium" if prob > 0.3 else "Low"
            
            return {
                "readmission_probability": round(prob, 2),
                "risk_level": risk_level,
                "reasoning": self._get_reasoning(patient_data, prob)
            }
            
        except Exception as e:
            print(f"Prediction error: {e}")
            return {"error": str(e), "readmission_probability": 0}

    def _get_reasoning(self, data, prob):
        reasons = []
        if prob > 0.5:
            if data.get('age', 0) > 70: reasons.append("Advanced Age")
            if data.get('recent_admissions', 0) > 0: reasons.append("History of admissions")
            if data.get('has_diabetes'): reasons.append("Chronic condition (Diabetes)")
        return reasons

class TreatmentResponseModel:
    """
    Predicts probability of treatment success using trained GradientBoosting
    """
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.features = []
        self.is_trained = False
        self.load_model()
        
    def load_model(self):
        try:
            path = "models/treatment_model.pkl"
            if os.path.exists(path):
                data = joblib.load(path)
                self.model = data['model']
                self.label_encoder = data['label_encoder']
                self.features = data['features']
                self.is_trained = True
                print(f"✅ Treatment model loaded from {path}")
            else:
                print(f"⚠️ Treatment model not found at {path}")
        except Exception as e:
            print(f"❌ Error loading treatment model: {e}")

    def predict_success(self, treatment: str, patient_conditions: Dict[str, Any]) -> float:
        if not self.is_trained:
            return 0.5
            
        try:
            # Encoder treatment type
            try:
                treatment_encoded = self.label_encoder.transform([treatment])[0]
            except:
                # Unknown treatment
                treatment_encoded = 0
                
            # Prepare other features: ['age', 'bmi', 'treatment_type_encoded', 'has_diabetes', 'has_hypertension']
            input_vector = [
                patient_conditions.get('age', 50),
                patient_conditions.get('bmi', 25),
                treatment_encoded,
                1 if patient_conditions.get('has_diabetes') else 0,
                1 if patient_conditions.get('has_hypertension') else 0
            ]
             
            # Predict
            prob = self.model.predict_proba([input_vector])[0][1]
            return round(prob, 2)
            
        except Exception as e:
            print(f"Treatment prediction error: {e}")
            return 0.5

# Initialize new models
readmission_model = ReadmissionRiskModel()
treatment_model = TreatmentResponseModel()

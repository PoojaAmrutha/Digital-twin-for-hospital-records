
# FILE: backend/alert_system.py


import os
from datetime import datetime
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()


class AlertSystem:
    """
    Manages health alerts based on vital thresholds
    Generates alerts when vitals exceed safe ranges
    """
    
    def __init__(self):
        """Initialize alert system with configurable thresholds"""
        # Load thresholds from environment or use defaults
        self.thresholds = {
            # Heart Rate thresholds (bpm)
            'hr_critical_low': int(os.getenv('ALERT_THRESHOLD_HR_LOW', 40)),
            'hr_critical_high': int(os.getenv('ALERT_THRESHOLD_HR_HIGH', 130)),
            'hr_warning_low': 50,
            'hr_warning_high': 110,
            
            # SpO2 thresholds (%)
            'spo2_critical': int(os.getenv('ALERT_THRESHOLD_SPO2_LOW', 88)),
            'spo2_danger': 92,
            'spo2_warning': 95,
            
            # Temperature thresholds (°C)
            'temp_critical_high': float(os.getenv('ALERT_THRESHOLD_TEMP_HIGH', 38.5)),
            'temp_critical_low': 35.0,
            'temp_warning_high': 38.0,
            'temp_warning_low': 35.5,
            
            # Stress thresholds (0-5 scale)
            'stress_high': 4.0,
            'stress_warning': 3.0
        }
    
    def check_vitals(self, vitals: Dict[str, float]) -> List[Dict]:
        """
        Check vitals against thresholds and generate alerts
        
        Args:
            vitals: Dictionary containing vital measurements
        
        Returns:
            List of alert dictionaries
        """
        alerts = []
        timestamp = datetime.utcnow().isoformat()
        
        # Check Heart Rate
        hr_alerts = self._check_heart_rate(vitals['heart_rate'], timestamp)
        alerts.extend(hr_alerts)
        
        # Check SpO2
        spo2_alerts = self._check_spo2(vitals['spo2'], timestamp)
        alerts.extend(spo2_alerts)
        
        # Check Temperature
        temp_alerts = self._check_temperature(vitals['temperature'], timestamp)
        alerts.extend(temp_alerts)
        
        # Check Stress Level
        stress_alerts = self._check_stress(vitals['stress_level'], timestamp)
        alerts.extend(stress_alerts)
        
        # Check for compound risks
        compound_alerts = self._check_compound_risks(vitals, timestamp)
        alerts.extend(compound_alerts)
        
        return alerts
    
    def _check_heart_rate(self, hr: float, timestamp: str) -> List[Dict]:
        """Check heart rate and generate alerts"""
        alerts = []
        
        if hr > self.thresholds['hr_critical_high']:
            alerts.append({
                'type': 'critical',
                'title': '🚨 Critical Heart Rate - Too High',
                'message': f"Heart rate dangerously high at {hr:.0f} bpm. Immediate attention required!",
                'vital': 'heart_rate',
                'value': hr,
                'timestamp': timestamp,
                'action': 'Contact emergency services immediately'
            })
        elif hr < self.thresholds['hr_critical_low']:
            alerts.append({
                'type': 'critical',
                'title': '🚨 Critical Heart Rate - Too Low',
                'message': f"Heart rate dangerously low at {hr:.0f} bpm. Immediate attention required!",
                'vital': 'heart_rate',
                'value': hr,
                'timestamp': timestamp,
                'action': 'Contact emergency services immediately'
            })
        elif hr > self.thresholds['hr_warning_high']:
            alerts.append({
                'type': 'danger',
                'title': '⚠️ High Heart Rate',
                'message': f"Heart rate elevated at {hr:.0f} bpm. Monitor closely.",
                'vital': 'heart_rate',
                'value': hr,
                'timestamp': timestamp,
                'action': 'Rest and monitor. Contact doctor if persists.'
            })
        elif hr < self.thresholds['hr_warning_low']:
            alerts.append({
                'type': 'danger',
                'title': '⚠️ Low Heart Rate',
                'message': f"Heart rate below normal at {hr:.0f} bpm.",
                'vital': 'heart_rate',
                'value': hr,
                'timestamp': timestamp,
                'action': 'Monitor closely. Contact doctor if symptomatic.'
            })
        elif hr > 100 or hr < 60:
            alerts.append({
                'type': 'warning',
                'title': 'ℹ️ Abnormal Heart Rate',
                'message': f"Heart rate slightly outside normal range: {hr:.0f} bpm",
                'vital': 'heart_rate',
                'value': hr,
                'timestamp': timestamp,
                'action': 'Monitor and note any symptoms'
            })
        
        return alerts
    
    def _check_spo2(self, spo2: float, timestamp: str) -> List[Dict]:
        """Check blood oxygen levels and generate alerts"""
        alerts = []
        
        if spo2 < self.thresholds['spo2_critical']:
            alerts.append({
                'type': 'critical',
                'title': '🚨 Critical Blood Oxygen Level',
                'message': f"SpO2 critically low at {spo2:.0f}%. Severe hypoxemia detected!",
                'vital': 'spo2',
                'value': spo2,
                'timestamp': timestamp,
                'action': 'EMERGENCY: Call 911 immediately. Administer oxygen if available.'
            })
        elif spo2 < self.thresholds['spo2_danger']:
            alerts.append({
                'type': 'danger',
                'title': '⚠️ Low Blood Oxygen',
                'message': f"SpO2 below safe level at {spo2:.0f}%. Moderate hypoxemia.",
                'vital': 'spo2',
                'value': spo2,
                'timestamp': timestamp,
                'action': 'Seek medical attention immediately'
            })
        elif spo2 < self.thresholds['spo2_warning']:
            alerts.append({
                'type': 'warning',
                'title': 'ℹ️ Reduced Blood Oxygen',
                'message': f"SpO2 below optimal at {spo2:.0f}%. Mild hypoxemia.",
                'vital': 'spo2',
                'value': spo2,
                'timestamp': timestamp,
                'action': 'Deep breathing exercises. Contact doctor if persists.'
            })
        
        return alerts
    
    def _check_temperature(self, temp: float, timestamp: str) -> List[Dict]:
        """Check body temperature and generate alerts"""
        alerts = []
        
        if temp > self.thresholds['temp_critical_high']:
            alerts.append({
                'type': 'danger',
                'title': '🌡️ High Fever Detected',
                'message': f"Body temperature elevated at {temp:.1f}°C. High fever present.",
                'vital': 'temperature',
                'value': temp,
                'timestamp': timestamp,
                'action': 'Take fever reducer. Contact doctor if above 39°C or persists.'
            })
        elif temp < self.thresholds['temp_critical_low']:
            alerts.append({
                'type': 'danger',
                'title': '🌡️ Hypothermia Risk',
                'message': f"Body temperature dangerously low at {temp:.1f}°C.",
                'vital': 'temperature',
                'value': temp,
                'timestamp': timestamp,
                'action': 'Warm up gradually. Seek medical attention.'
            })
        elif temp > self.thresholds['temp_warning_high']:
            alerts.append({
                'type': 'warning',
                'title': '🌡️ Elevated Temperature',
                'message': f"Body temperature slightly elevated at {temp:.1f}°C.",
                'vital': 'temperature',
                'value': temp,
                'timestamp': timestamp,
                'action': 'Monitor temperature. Stay hydrated.'
            })
        elif temp < self.thresholds['temp_warning_low']:
            alerts.append({
                'type': 'warning',
                'title': '🌡️ Low Temperature',
                'message': f"Body temperature below normal at {temp:.1f}°C.",
                'vital': 'temperature',
                'value': temp,
                'timestamp': timestamp,
                'action': 'Warm up and monitor'
            })
        
        return alerts
    
    def _check_stress(self, stress: float, timestamp: str) -> List[Dict]:
        """Check stress levels and generate alerts"""
        alerts = []
        
        if stress > self.thresholds['stress_high']:
            alerts.append({
                'type': 'warning',
                'title': '😰 High Stress Level',
                'message': f"Stress level very high at {stress:.1f}/5. Take action to reduce stress.",
                'vital': 'stress',
                'value': stress,
                'timestamp': timestamp,
                'action': 'Practice deep breathing. Consider meditation or rest.'
            })
        elif stress > self.thresholds['stress_warning']:
            alerts.append({
                'type': 'warning',
                'title': 'ℹ️ Elevated Stress',
                'message': f"Stress level elevated at {stress:.1f}/5.",
                'vital': 'stress',
                'value': stress,
                'timestamp': timestamp,
                'action': 'Take breaks. Practice relaxation techniques.'
            })
        
        return alerts
    
    def _check_compound_risks(self, vitals: Dict[str, float], timestamp: str) -> List[Dict]:
        """Check for multiple concerning vitals at once"""
        alerts = []
        
        # Check for cardiac distress (high HR + low SpO2)
        if vitals['heart_rate'] > 110 and vitals['spo2'] < 94:
            alerts.append({
                'type': 'danger',
                'title': '⚠️ Cardiac Distress Indicators',
                'message': f"Combined high heart rate ({vitals['heart_rate']:.0f} bpm) and low oxygen ({vitals['spo2']:.0f}%).",
                'vital': 'compound',
                'value': None,
                'timestamp': timestamp,
                'action': 'Seek immediate medical evaluation'
            })
        
        # Check for fever with respiratory compromise
        if vitals['temperature'] > 38.0 and vitals['spo2'] < 95:
            alerts.append({
                'type': 'danger',
                'title': '⚠️ Fever with Low Oxygen',
                'message': f"Fever ({vitals['temperature']:.1f}°C) combined with reduced oxygen ({vitals['spo2']:.0f}%).",
                'vital': 'compound',
                'value': None,
                'timestamp': timestamp,
                'action': 'Contact doctor. May indicate respiratory infection.'
            })
        
        # Check for stress-induced tachycardia
        if vitals['stress_level'] > 3.5 and vitals['heart_rate'] > 100:
            alerts.append({
                'type': 'warning',
                'title': 'ℹ️ Stress-Related Heart Rate',
                'message': f"High stress ({vitals['stress_level']:.1f}/5) causing elevated heart rate.",
                'vital': 'compound',
                'value': None,
                'timestamp': timestamp,
                'action': 'Stress reduction recommended. Practice calming techniques.'
            })
        
        return alerts
    
    def get_alert_priority(self, alert_type: str) -> int:
        """Get numeric priority for sorting alerts"""
        priority_map = {
            'critical': 1,
            'danger': 2,
            'warning': 3,
            'info': 4
        }
        return priority_map.get(alert_type, 5)
    
    def summarize_alerts(self, alerts: List[Dict]) -> Dict:
        """Create summary of alerts"""
        if not alerts:
            return {
                'total': 0,
                'critical': 0,
                'danger': 0,
                'warning': 0,
                'message': 'All vitals normal'
            }
        
        summary = {
            'total': len(alerts),
            'critical': sum(1 for a in alerts if a['type'] == 'critical'),
            'danger': sum(1 for a in alerts if a['type'] == 'danger'),
            'warning': sum(1 for a in alerts if a['type'] == 'warning'),
        }
        
        if summary['critical'] > 0:
            summary['message'] = f"{summary['critical']} critical alert(s) - immediate attention required!"
        elif summary['danger'] > 0:
            summary['message'] = f"{summary['danger']} serious alert(s) - medical attention needed"
        else:
            summary['message'] = f"{summary['warning']} warning(s) - monitor closely"
        
        return summary


# Global instance
alert_system = AlertSystem()


# Test function
if __name__ == "__main__":
    # Test with normal vitals
    normal_vitals = {
        'heart_rate': 75,
        'spo2': 98,
        'temperature': 36.8,
        'stress_level': 2.0
    }
    
    print("Testing with normal vitals:")
    alerts = alert_system.check_vitals(normal_vitals)
    print(f"Alerts generated: {len(alerts)}")
    
    # Test with abnormal vitals
    abnormal_vitals = {
        'heart_rate': 145,
        'spo2': 85,
        'temperature': 39.0,
        'stress_level': 4.5
    }
    
    print("\nTesting with abnormal vitals:")
    alerts = alert_system.check_vitals(abnormal_vitals)
    print(f"Alerts generated: {len(alerts)}")
    for alert in alerts:
        print(f"  - {alert['type'].upper()}: {alert['title']}")
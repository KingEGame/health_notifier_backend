from app.extensions import db
from datetime import datetime
import json

class RiskAssessment(db.Model):
    __tablename__ = 'risk_assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    risk_level = db.Column(db.Enum('low', 'medium', 'high', name='risk_level_enum'), nullable=False)
    heat_wave_risk = db.Column(db.Boolean, default=False)
    risk_factors = db.Column(db.Text)
    risk_score = db.Column(db.Integer, default=0)
    weather_data = db.Column(db.Text)
    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_risk_factors(self):
        """Get risk factors as a dictionary"""
        if self.risk_factors:
            try:
                return json.loads(self.risk_factors)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_risk_factors(self, factors):
        """Set risk factors from a dictionary"""
        self.risk_factors = json.dumps(factors) if factors else None
    
    def get_weather_data(self):
        """Get weather data as a dictionary"""
        if self.weather_data:
            try:
                return json.loads(self.weather_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_weather_data(self, weather):
        """Set weather data from a dictionary"""
        self.weather_data = json.dumps(weather) if weather else None
    
    def to_dict(self):
        """Convert risk assessment to dictionary for API responses"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'risk_level': self.risk_level,
            'heat_wave_risk': self.heat_wave_risk,
            'risk_factors': self.get_risk_factors(),
            'risk_score': self.risk_score,
            'weather_data': self.get_weather_data(),
            'assessment_date': self.assessment_date.isoformat() if self.assessment_date else None
        }

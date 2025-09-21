from app.extensions import db
from datetime import datetime
import json

class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    pregnancy_icd10 = db.Column(db.String(20))  # Pregnancy ICD-10
    pregnancy_description = db.Column(db.Text)  # Pregnancy Description
    comorbidity_icd10 = db.Column(db.String(20))  # Comorbidity ICD-10
    comorbidity_description = db.Column(db.Text)  # Comorbidity Description
    weeks_pregnant = db.Column(db.Integer)  # Weeks Pregnant
    address = db.Column(db.Text)  # Address
    zip_code = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.String(20))
    email = db.Column(db.String(100))
    medications = db.Column(db.Text)  # Medications
    medication_notes = db.Column(db.Text)  # Medication Notes
    ndc_codes = db.Column(db.Text)  # NDC Codes
    between_17_35 = db.Column(db.Boolean, default=False)  # Between 17-35 flag
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    risk_assessments = db.relationship('RiskAssessment', backref='patient', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='patient', lazy=True, cascade='all, delete-orphan')
    
    def get_conditions(self):
        """Get all ICD10 conditions as a list (pregnancy + comorbidity)"""
        conditions = []
        if self.pregnancy_icd10:
            conditions.append(self.pregnancy_icd10)
        if self.comorbidity_icd10:
            conditions.append(self.comorbidity_icd10)
        return conditions
    
    def set_conditions(self, conditions):
        """Set ICD10 conditions from a list (for backward compatibility)"""
        if conditions and len(conditions) >= 1:
            self.pregnancy_icd10 = conditions[0] if len(conditions) > 0 else None
            self.comorbidity_icd10 = conditions[1] if len(conditions) > 1 else None
    
    def get_trimester(self):
        """Calculate trimester from weeks pregnant"""
        if self.weeks_pregnant:
            if self.weeks_pregnant <= 12:
                return 1
            elif self.weeks_pregnant <= 24:
                return 2
            else:
                return 3
        return None
    
    def get_risk_level(self):
        """Calculate risk level based on multiple factors using RiskAssessmentService"""
        from app.services.risk_service import RiskAssessmentService
        
        # Use the comprehensive risk assessment service
        risk_assessment = RiskAssessmentService.assess_risk(self)
        return risk_assessment['risk_level']
    
    def needs_emergency_notification(self):
        """Check if patient needs emergency notification"""
        return self.get_risk_level() == 'high'
    
    def set_trimester(self, trimester):
        """Set trimester (for backward compatibility)"""
        # This is a placeholder - in practice, you'd calculate weeks_pregnant
        # based on trimester, but we need more context for accurate conversion
        pass
    
    def get_medications_list(self):
        """Get medications as a list"""
        if self.medications:
            return [med.strip() for med in self.medications.split(';') if med.strip()]
        return []
    
    def get_ndc_codes_list(self):
        """Get NDC codes as a list"""
        if self.ndc_codes:
            return [code.strip() for code in self.ndc_codes.split(';') if code.strip()]
        return []
    
    def is_high_risk_age(self):
        """Check if patient is in high-risk age group (outside 17-35)"""
        return not self.between_17_35
    
    def to_dict(self):
        """Convert patient to dictionary for API responses"""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'pregnancy_icd10': self.pregnancy_icd10,
            'pregnancy_description': self.pregnancy_description,
            'comorbidity_icd10': self.comorbidity_icd10,
            'comorbidity_description': self.comorbidity_description,
            'weeks_pregnant': self.weeks_pregnant,
            'address': self.address,
            'zip_code': self.zip_code,
            'phone_number': self.phone_number,
            'email': self.email,
            'medications': self.medications,
            'medication_notes': self.medication_notes,
            'ndc_codes': self.ndc_codes,
            'between_17_35': self.between_17_35,
            'medications_list': self.get_medications_list(),
            'ndc_codes_list': self.get_ndc_codes_list(),
            'is_high_risk_age': self.is_high_risk_age(),
            'conditions_icd10': self.get_conditions(),  # For backward compatibility
            'trimester': self.get_trimester(),  # Calculated from weeks_pregnant
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

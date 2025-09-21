from app.extensions import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    risk_level = db.Column(db.Enum('low', 'medium', 'high', name='notification_risk_level_enum'), nullable=False)
    notification_type = db.Column(db.Enum('heat_warning', 'general_health', 'appointment_reminder', name='notification_type_enum'), default='general_health')
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    read_status = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.read_status = True
        self.read_at = datetime.utcnow()
    
    def to_dict(self):
        """Convert notification to dictionary for API responses"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'message': self.message,
            'risk_level': self.risk_level,
            'notification_type': self.notification_type,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'read_status': self.read_status,
            'read_at': self.read_at.isoformat() if self.read_at else None
        }

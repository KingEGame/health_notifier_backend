from app.extensions import db
from datetime import datetime

class EmergencyNotification(db.Model):
    __tablename__ = 'emergency_notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    health_facility_id = db.Column(db.Integer, db.ForeignKey('health_facilities.id'), nullable=False)
    risk_level = db.Column(db.Enum('low', 'medium', 'high'), nullable=False)
    notification_type = db.Column(db.Enum('patient_notification', 'doctor_call', 'emergency_alert'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('pending', 'sent', 'delivered', 'failed'), default='pending')
    priority = db.Column(db.Enum('low', 'medium', 'high', 'critical'), default='medium')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    response_received = db.Column(db.Boolean, default=False)
    response_message = db.Column(db.Text)
    response_received_at = db.Column(db.DateTime)
    
    # Relationships
    patient = db.relationship('Patient', backref='emergency_notifications')
    health_facility = db.relationship('HealthFacility', backref='emergency_notifications')
    
    def to_dict(self):
        """Convert emergency notification to dictionary for API responses"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'health_facility_id': self.health_facility_id,
            'risk_level': self.risk_level,
            'notification_type': self.notification_type,
            'message': self.message,
            'status': self.status,
            'priority': self.priority,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'delivered_at': self.delivered_at.isoformat() if self.delivered_at else None,
            'response_received': self.response_received,
            'response_message': self.response_message,
            'response_received_at': self.response_received_at.isoformat() if self.response_received_at else None
        }
    
    def mark_as_sent(self):
        """Mark notification as sent"""
        self.status = 'sent'
        self.sent_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_delivered(self):
        """Mark notification as delivered"""
        self.status = 'delivered'
        self.delivered_at = datetime.utcnow()
        db.session.commit()
    
    def mark_as_failed(self):
        """Mark notification as failed"""
        self.status = 'failed'
        db.session.commit()
    
    def add_response(self, response_message):
        """Add response from health facility"""
        self.response_received = True
        self.response_message = response_message
        self.response_received_at = datetime.utcnow()
        db.session.commit()

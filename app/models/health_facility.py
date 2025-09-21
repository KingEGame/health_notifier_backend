from app.extensions import db
from datetime import datetime

class HealthFacility(db.Model):
    __tablename__ = 'health_facilities'
    
    id = db.Column(db.Integer, primary_key=True)
    facility_id = db.Column(db.String(20), unique=True, nullable=False)
    facility_name = db.Column(db.String(200), nullable=False)
    short_description = db.Column(db.String(50))
    description = db.Column(db.String(200))
    facility_open_date = db.Column(db.Date)
    facility_address_1 = db.Column(db.String(200))
    facility_address_2 = db.Column(db.String(200))
    facility_city = db.Column(db.String(100))
    facility_state = db.Column(db.String(50))
    facility_zip_code = db.Column(db.String(20))
    facility_phone_number = db.Column(db.String(20))
    facility_fax_number = db.Column(db.String(20))
    facility_website = db.Column(db.String(200))
    facility_county_code = db.Column(db.String(10))
    facility_county = db.Column(db.String(100))
    regional_office_id = db.Column(db.String(10))
    regional_office = db.Column(db.String(100))
    main_site_name = db.Column(db.String(200))
    main_site_facility_id = db.Column(db.String(20))
    operating_certificate_number = db.Column(db.String(50))
    operator_name = db.Column(db.String(200))
    operator_address_1 = db.Column(db.String(200))
    operator_address_2 = db.Column(db.String(200))
    operator_city = db.Column(db.String(100))
    operator_state = db.Column(db.String(50))
    operator_zip_code = db.Column(db.String(20))
    cooperator_name = db.Column(db.String(200))
    cooperator_address = db.Column(db.String(200))
    cooperator_address_2 = db.Column(db.String(200))
    cooperator_city = db.Column(db.String(100))
    cooperator_state = db.Column(db.String(50))
    cooperator_zip_code = db.Column(db.String(20))
    ownership_type = db.Column(db.String(100))
    facility_latitude = db.Column(db.Float)
    facility_longitude = db.Column(db.Float)
    facility_location = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    emergency_notifications = db.relationship('EmergencyNotification', backref='health_facility', lazy=True)
    
    def to_dict(self):
        """Convert facility to dictionary for API responses"""
        return {
            'id': self.id,
            'facility_id': self.facility_id,
            'facility_name': self.facility_name,
            'short_description': self.short_description,
            'description': self.description,
            'facility_address_1': self.facility_address_1,
            'facility_city': self.facility_city,
            'facility_state': self.facility_state,
            'facility_zip_code': self.facility_zip_code,
            'facility_phone_number': self.facility_phone_number,
            'facility_website': self.facility_website,
            'facility_county': self.facility_county,
            'regional_office': self.regional_office,
            'operator_name': self.operator_name,
            'ownership_type': self.ownership_type,
            'facility_latitude': self.facility_latitude,
            'facility_longitude': self.facility_longitude,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def get_full_address(self):
        """Get complete address string"""
        address_parts = []
        if self.facility_address_1:
            address_parts.append(self.facility_address_1)
        if self.facility_address_2:
            address_parts.append(self.facility_address_2)
        if self.facility_city:
            address_parts.append(self.facility_city)
        if self.facility_state:
            address_parts.append(self.facility_state)
        if self.facility_zip_code:
            address_parts.append(self.facility_zip_code)
        return ', '.join(address_parts)
    
    def is_hospital(self):
        """Check if facility is a hospital"""
        return self.short_description in ['HOSP', 'HOSP-EC']
    
    def is_nursing_home(self):
        """Check if facility is a nursing home"""
        return self.short_description == 'NH'
    
    def is_clinic(self):
        """Check if facility is a clinic"""
        return self.short_description in ['DTC', 'HOSP-EC']

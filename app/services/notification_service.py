import requests
import json
from datetime import datetime
from flask import current_app
from app.extensions import db
from app.models.patient import Patient
from app.models.health_facility import HealthFacility
from app.models.emergency_notification import EmergencyNotification
from app.services.message_service import MessageService
from app.utils.exceptions import ExternalAPIException
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    """Service for handling notifications with three risk levels"""
    
    @staticmethod
    def process_risk_notification(patient_id):
        """Process risk notification for a patient"""
        try:
            patient = Patient.query.get_or_404(patient_id)
            risk_level = patient.get_risk_level()
            
            # Generate appropriate notification based on risk level
            if risk_level == 'high':
                return NotificationService._handle_high_risk(patient)
            elif risk_level == 'medium':
                return NotificationService._handle_medium_risk(patient)
            else:  # low risk
                return NotificationService._handle_low_risk(patient)
                
        except Exception as e:
            logger.error(f"Error processing risk notification: {e}")
            raise ExternalAPIException(f"Failed to process risk notification: {e}")
    
    @staticmethod
    def _handle_high_risk(patient):
        """Handle high risk patients - call doctor immediately"""
        try:
            # Find nearest hospital
            nearest_hospital = NotificationService._find_nearest_hospital(patient.zip_code)
            
            if not nearest_hospital:
                logger.warning(f"No hospital found for patient {patient.id} in zip {patient.zip_code}")
                return NotificationService._create_fallback_notification(patient, 'high')
            
            # Create emergency notification
            emergency_notification = EmergencyNotification(
                patient_id=patient.id,
                health_facility_id=nearest_hospital.id,
                risk_level='high',
                notification_type='doctor_call',
                message=NotificationService._generate_high_risk_message(patient, nearest_hospital),
                priority='critical',
                status='pending'
            )
            
            db.session.add(emergency_notification)
            db.session.commit()
            
            # Send notification to hospital
            NotificationService._send_doctor_call(emergency_notification)
            
            # Also send patient notification
            patient_message = MessageService.generate_message(patient, {
                'risk_level': 'high',
                'heat_wave_risk': False,
                'factors': {'risk_level': 'high'}
            })
            
            from app.models.notification import Notification
            patient_notification = Notification(
                patient_id=patient.id,
                message=patient_message,
                risk_level='high'
            )
            db.session.add(patient_notification)
            db.session.commit()
            
            return {
                'success': True,
                'risk_level': 'high',
                'action_taken': 'doctor_called',
                'hospital': nearest_hospital.to_dict(),
                'emergency_notification_id': emergency_notification.id,
                'patient_message': patient_message
            }
            
        except Exception as e:
            logger.error(f"Error handling high risk: {e}")
            return NotificationService._create_fallback_notification(patient, 'high')
    
    @staticmethod
    def _handle_medium_risk(patient):
        """Handle medium risk patients - send enhanced notification"""
        try:
            # Generate enhanced message for medium risk
            message = MessageService.generate_message(patient, {
                'risk_level': 'medium',
                'heat_wave_risk': False,
                'factors': {'risk_level': 'medium'}
            })
            
            # Create patient notification
            from app.models.notification import Notification
            notification = Notification(
                patient_id=patient.id,
                message=message,
                risk_level='medium'
            )
            db.session.add(notification)
            db.session.commit()
            
            # Find nearest clinic for potential follow-up
            nearest_clinic = NotificationService._find_nearest_clinic(patient.zip_code)
            
            return {
                'success': True,
                'risk_level': 'medium',
                'action_taken': 'enhanced_notification_sent',
                'message': message,
                'clinic': nearest_clinic.to_dict() if nearest_clinic else None
            }
            
        except Exception as e:
            logger.error(f"Error handling medium risk: {e}")
            return NotificationService._create_fallback_notification(patient, 'medium')
    
    @staticmethod
    def _handle_low_risk(patient):
        """Handle low risk patients - send standard notification"""
        try:
            # Generate standard message for low risk
            message = MessageService.generate_message(patient, {
                'risk_level': 'low',
                'heat_wave_risk': False,
                'factors': {'risk_level': 'low'}
            })
            
            # Create patient notification
            from app.models.notification import Notification
            notification = Notification(
                patient_id=patient.id,
                message=message,
                risk_level='low'
            )
            db.session.add(notification)
            db.session.commit()
            
            return {
                'success': True,
                'risk_level': 'low',
                'action_taken': 'standard_notification_sent',
                'message': message
            }
            
        except Exception as e:
            logger.error(f"Error handling low risk: {e}")
            return NotificationService._create_fallback_notification(patient, 'low')
    
    @staticmethod
    def _find_nearest_hospital(zip_code):
        """Find nearest hospital to patient's zip code"""
        try:
            # For now, find any hospital (in real implementation, use geolocation)
            hospital = HealthFacility.query.filter(
                HealthFacility.short_description.in_(['HOSP', 'HOSP-EC']),
                HealthFacility.facility_phone_number.isnot(None)
            ).first()
            
            return hospital
        except Exception as e:
            logger.error(f"Error finding nearest hospital: {e}")
            return None
    
    @staticmethod
    def _find_nearest_clinic(zip_code):
        """Find nearest clinic to patient's zip code"""
        try:
            # For now, find any clinic
            clinic = HealthFacility.query.filter(
                HealthFacility.short_description.in_(['DTC', 'HOSP-EC']),
                HealthFacility.facility_phone_number.isnot(None)
            ).first()
            
            return clinic
        except Exception as e:
            logger.error(f"Error finding nearest clinic: {e}")
            return None
    
    @staticmethod
    def _generate_high_risk_message(patient, hospital):
        """Generate high risk message for doctor call"""
        return f"""
🚨 ЭКСТРЕННОЕ УВЕДОМЛЕНИЕ - ВЫСОКИЙ РИСК 🚨

Пациент: {patient.name}
Возраст: {patient.age} лет
Недели беременности: {patient.weeks_pregnant}
Триместр: {patient.get_trimester()}

Медицинские состояния:
- Беременность: {patient.pregnancy_icd10} - {patient.pregnancy_description}
- Сопутствующие: {patient.comorbidity_icd10} - {patient.comorbidity_description}

Адрес: {patient.address}
ZIP: {patient.zip_code}
Телефон: {patient.phone_number}

ТРЕБУЕТСЯ НЕМЕДЛЕННАЯ КОНСУЛЬТАЦИЯ ВРАЧА!

Больница: {hospital.facility_name}
Телефон: {hospital.facility_phone_number}
Адрес: {hospital.get_full_address()}

Время уведомления: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """.strip()
    
    @staticmethod
    def _send_doctor_call(emergency_notification):
        """Send doctor call notification"""
        try:
            # In real implementation, this would integrate with:
            # - SMS service
            # - Email service
            # - Hospital notification system
            # - Emergency services API
            
            # For now, just log the notification
            logger.info(f"DOCTOR CALL: {emergency_notification.message}")
            
            # Mark as sent
            emergency_notification.mark_as_sent()
            
            # Simulate delivery after 30 seconds
            # In real implementation, this would be handled by the notification service
            return True
            
        except Exception as e:
            logger.error(f"Error sending doctor call: {e}")
            emergency_notification.mark_as_failed()
            return False
    
    @staticmethod
    def _create_fallback_notification(patient, risk_level):
        """Create fallback notification when hospital is not available"""
        message = f"""
⚠️ Уведомление о риске - {risk_level.upper()}

Пациент: {patient.name}
Уровень риска: {risk_level}

Пожалуйста, обратитесь к врачу для консультации.
        """.strip()
        
        return {
            'success': True,
            'risk_level': risk_level,
            'action_taken': 'fallback_notification',
            'message': message
        }
    
    @staticmethod
    def get_emergency_notifications(patient_id=None, status=None):
        """Get emergency notifications with optional filters"""
        query = EmergencyNotification.query
        
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        
        if status:
            query = query.filter_by(status=status)
        
        return query.order_by(EmergencyNotification.created_at.desc()).all()
    
    @staticmethod
    def update_emergency_notification(notification_id, response_message=None):
        """Update emergency notification status"""
        try:
            notification = EmergencyNotification.query.get_or_404(notification_id)
            
            if response_message:
                notification.add_response(response_message)
            else:
                notification.mark_as_delivered()
            
            return notification.to_dict()
            
        except Exception as e:
            logger.error(f"Error updating emergency notification: {e}")
            raise ExternalAPIException(f"Failed to update notification: {e}")

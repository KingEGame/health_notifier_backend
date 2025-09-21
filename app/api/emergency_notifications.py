from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.emergency_notification import EmergencyNotification
from app.models.patient import Patient
from app.services.notification_service import NotificationService
from app.utils.exceptions import ValidationException
import logging

logger = logging.getLogger(__name__)

emergency_notifications_bp = Blueprint('emergency_notifications', __name__)

@emergency_notifications_bp.route('/emergency-notifications', methods=['POST'])
def create_emergency_notification():
    """Create emergency notification for a patient"""
    try:
        data = request.get_json()
        patient_id = data.get('patient_id')
        
        if not patient_id:
            return jsonify({
                'success': False,
                'error': 'Patient ID is required'
            }), 400
        
        # Process risk notification
        result = NotificationService.process_risk_notification(patient_id)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error creating emergency notification: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create emergency notification'
        }), 500

@emergency_notifications_bp.route('/emergency-notifications', methods=['GET'])
def get_emergency_notifications():
    """Get emergency notifications with optional filtering"""
    try:
        patient_id = request.args.get('patient_id', type=int)
        status = request.args.get('status')
        risk_level = request.args.get('risk_level')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = EmergencyNotification.query
        
        if patient_id:
            query = query.filter_by(patient_id=patient_id)
        
        if status:
            query = query.filter_by(status=status)
        
        if risk_level:
            query = query.filter_by(risk_level=risk_level)
        
        # Pagination
        pagination = query.order_by(EmergencyNotification.created_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        notifications = [notification.to_dict() for notification in pagination.items]
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'total_pages': pagination.pages,
            'current_page': pagination.page,
            'total_items': pagination.total
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting emergency notifications: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get emergency notifications'
        }), 500

@emergency_notifications_bp.route('/emergency-notifications/<int:notification_id>', methods=['GET'])
def get_emergency_notification(notification_id):
    """Get specific emergency notification by ID"""
    try:
        notification = EmergencyNotification.query.get_or_404(notification_id)
        
        return jsonify({
            'success': True,
            'notification': notification.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting emergency notification: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get emergency notification'
        }), 500

@emergency_notifications_bp.route('/emergency-notifications/<int:notification_id>/update', methods=['PUT'])
def update_emergency_notification(notification_id):
    """Update emergency notification status"""
    try:
        data = request.get_json()
        response_message = data.get('response_message')
        
        result = NotificationService.update_emergency_notification(
            notification_id, 
            response_message
        )
        
        return jsonify({
            'success': True,
            'notification': result
        }), 200
        
    except Exception as e:
        logger.error(f"Error updating emergency notification: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update emergency notification'
        }), 500

@emergency_notifications_bp.route('/emergency-notifications/patient/<int:patient_id>/assess', methods=['POST'])
def assess_patient_risk(patient_id):
    """Assess patient risk and create appropriate notifications"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        # Process risk notification
        result = NotificationService.process_risk_notification(patient_id)
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error assessing patient risk: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to assess patient risk'
        }), 500

@emergency_notifications_bp.route('/emergency-notifications/stats', methods=['GET'])
def get_emergency_notification_stats():
    """Get emergency notification statistics"""
    try:
        # Count by status
        status_counts = db.session.query(
            EmergencyNotification.status,
            db.func.count(EmergencyNotification.id)
        ).group_by(EmergencyNotification.status).all()
        
        # Count by risk level
        risk_level_counts = db.session.query(
            EmergencyNotification.risk_level,
            db.func.count(EmergencyNotification.id)
        ).group_by(EmergencyNotification.risk_level).all()
        
        # Count by notification type
        type_counts = db.session.query(
            EmergencyNotification.notification_type,
            db.func.count(EmergencyNotification.id)
        ).group_by(EmergencyNotification.notification_type).all()
        
        # Recent notifications (last 24 hours)
        from datetime import datetime, timedelta
        recent_cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_count = EmergencyNotification.query.filter(
            EmergencyNotification.created_at >= recent_cutoff
        ).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'status_counts': dict(status_counts),
                'risk_level_counts': dict(risk_level_counts),
                'type_counts': dict(type_counts),
                'recent_notifications_24h': recent_count,
                'total_notifications': EmergencyNotification.query.count()
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting emergency notification stats: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get emergency notification stats'
        }), 500

@emergency_notifications_bp.route('/emergency-notifications/pending', methods=['GET'])
def get_pending_notifications():
    """Get all pending emergency notifications"""
    try:
        pending_notifications = EmergencyNotification.query.filter_by(
            status='pending'
        ).order_by(EmergencyNotification.priority.desc(), EmergencyNotification.created_at.asc()).all()
        
        notifications = [notification.to_dict() for notification in pending_notifications]
        
        return jsonify({
            'success': True,
            'notifications': notifications,
            'count': len(notifications)
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting pending notifications: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get pending notifications'
        }), 500

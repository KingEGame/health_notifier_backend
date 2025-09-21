from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Patient, Notification
import logging

logger = logging.getLogger(__name__)

notifications_bp = Blueprint('notifications', __name__)

@notifications_bp.route('/notifications/<int:patient_id>', methods=['GET'])
def get_notifications(patient_id):
    """Get notifications for a patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        unread_only = request.args.get('unread_only', 'false').lower() == 'true'
        
        query = Notification.query.filter_by(patient_id=patient_id)
        
        if unread_only:
            query = query.filter_by(read_status=False)
        
        notifications = query.order_by(Notification.sent_at.desc()).paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'notifications': [notif.to_dict() for notif in notifications.items],
            'total': notifications.total,
            'pages': notifications.pages,
            'current_page': page
        })
        
    except Exception as e:
        logger.error(f"Error getting notifications: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get notifications'
        }), 500

@notifications_bp.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    """Mark a notification as read"""
    try:
        notification = Notification.query.get_or_404(notification_id)
        notification.mark_as_read()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notification marked as read',
            'notification': notification.to_dict()
        })
        
    except Exception as e:
        logger.error(f"Error marking notification as read: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to mark notification as read'
        }), 500

@notifications_bp.route('/notifications/<int:patient_id>/mark-all-read', methods=['POST'])
def mark_all_notifications_read(patient_id):
    """Mark all notifications as read for a patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        notifications = Notification.query.filter_by(
            patient_id=patient_id, 
            read_status=False
        ).all()
        
        for notification in notifications:
            notification.mark_as_read()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': f'Marked {len(notifications)} notifications as read'
        })
        
    except Exception as e:
        logger.error(f"Error marking all notifications as read: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to mark all notifications as read'
        }), 500

@notifications_bp.route('/notifications/unread-count/<int:patient_id>', methods=['GET'])
def get_unread_count(patient_id):
    """Get count of unread notifications for a patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        
        unread_count = Notification.query.filter_by(
            patient_id=patient_id,
            read_status=False
        ).count()
        
        return jsonify({
            'success': True,
            'unread_count': unread_count
        })
        
    except Exception as e:
        logger.error(f"Error getting unread count: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get unread count'
        }), 500

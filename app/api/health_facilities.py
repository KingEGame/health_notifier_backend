from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.health_facility import HealthFacility
from app.utils.exceptions import ValidationException
import logging

logger = logging.getLogger(__name__)

health_facilities_bp = Blueprint('health_facilities', __name__)

@health_facilities_bp.route('/health-facilities', methods=['GET'])
def get_health_facilities():
    """Get all health facilities with optional filtering"""
    try:
        # Query parameters
        facility_type = request.args.get('type')  # HOSP, NH, DTC, etc.
        county = request.args.get('county')
        city = request.args.get('city')
        state = request.args.get('state')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Build query
        query = HealthFacility.query
        
        if facility_type:
            query = query.filter(HealthFacility.short_description == facility_type)
        
        if county:
            query = query.filter(HealthFacility.facility_county.ilike(f'%{county}%'))
        
        if city:
            query = query.filter(HealthFacility.facility_city.ilike(f'%{city}%'))
        
        if state:
            query = query.filter(HealthFacility.facility_state.ilike(f'%{state}%'))
        
        # Pagination
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        facilities = [facility.to_dict() for facility in pagination.items]
        
        return jsonify({
            'success': True,
            'facilities': facilities,
            'total_pages': pagination.pages,
            'current_page': pagination.page,
            'total_items': pagination.total,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting health facilities: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get health facilities'
        }), 500

@health_facilities_bp.route('/health-facilities/<int:facility_id>', methods=['GET'])
def get_health_facility(facility_id):
    """Get specific health facility by ID"""
    try:
        facility = HealthFacility.query.get_or_404(facility_id)
        
        return jsonify({
            'success': True,
            'facility': facility.to_dict()
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting health facility: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get health facility'
        }), 500

@health_facilities_bp.route('/health-facilities/search', methods=['GET'])
def search_health_facilities():
    """Search health facilities by name or description"""
    try:
        search_term = request.args.get('q', '')
        facility_type = request.args.get('type')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if not search_term:
            return jsonify({
                'success': False,
                'error': 'Search term is required'
            }), 400
        
        # Build search query
        query = HealthFacility.query.filter(
            db.or_(
                HealthFacility.facility_name.ilike(f'%{search_term}%'),
                HealthFacility.description.ilike(f'%{search_term}%'),
                HealthFacility.facility_city.ilike(f'%{search_term}%')
            )
        )
        
        if facility_type:
            query = query.filter(HealthFacility.short_description == facility_type)
        
        # Pagination
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        facilities = [facility.to_dict() for facility in pagination.items]
        
        return jsonify({
            'success': True,
            'facilities': facilities,
            'search_term': search_term,
            'total_pages': pagination.pages,
            'current_page': pagination.page,
            'total_items': pagination.total
        }), 200
        
    except Exception as e:
        logger.error(f"Error searching health facilities: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to search health facilities'
        }), 500

@health_facilities_bp.route('/health-facilities/nearest', methods=['GET'])
def get_nearest_health_facilities():
    """Get nearest health facilities to a zip code"""
    try:
        zip_code = request.args.get('zip_code')
        facility_type = request.args.get('type', 'HOSP')  # Default to hospital
        limit = request.args.get('limit', 5, type=int)
        
        if not zip_code:
            return jsonify({
                'success': False,
                'error': 'ZIP code is required'
            }), 400
        
        # For now, return facilities with phone numbers
        # In real implementation, use geolocation to find nearest
        query = HealthFacility.query.filter(
            HealthFacility.short_description == facility_type,
            HealthFacility.facility_phone_number.isnot(None)
        ).limit(limit)
        
        facilities = [facility.to_dict() for facility in query.all()]
        
        return jsonify({
            'success': True,
            'facilities': facilities,
            'zip_code': zip_code,
            'facility_type': facility_type
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting nearest health facilities: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get nearest health facilities'
        }), 500

@health_facilities_bp.route('/health-facilities/types', methods=['GET'])
def get_facility_types():
    """Get available facility types"""
    try:
        types = db.session.query(HealthFacility.short_description).distinct().all()
        facility_types = [t[0] for t in types if t[0]]
        
        return jsonify({
            'success': True,
            'facility_types': facility_types
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting facility types: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get facility types'
        }), 500

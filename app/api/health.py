from flask import Blueprint, jsonify
from app.extensions import db
from app.services import WeatherService
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

health_bp = Blueprint('health', __name__)

@health_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db.session.execute('SELECT 1')
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'version': '1.0.0'
        })
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

@health_bp.route('/health/detailed', methods=['GET'])
def detailed_health_check():
    """Detailed health check with component status"""
    try:
        health_status = {
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'version': '1.0.0',
            'components': {}
        }
        
        # Database check
        try:
            db.session.execute('SELECT 1')
            health_status['components']['database'] = {
                'status': 'healthy',
                'message': 'Database connection successful'
            }
        except Exception as e:
            health_status['components']['database'] = {
                'status': 'unhealthy',
                'message': f'Database connection failed: {str(e)}'
            }
            health_status['status'] = 'unhealthy'
        
        # External APIs check
        try:
            # Test weather API with a sample zip code
            weather_data = WeatherService.get_weather_data('101000')
            health_status['components']['weather_api'] = {
                'status': 'healthy',
                'message': 'Weather API accessible'
            }
        except Exception as e:
            health_status['components']['weather_api'] = {
                'status': 'degraded',
                'message': f'Weather API issue: {str(e)}'
            }
        
        return jsonify(health_status)
        
    except Exception as e:
        logger.error(f"Detailed health check failed: {e}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'timestamp': datetime.utcnow().isoformat(),
            'error': str(e)
        }), 500

@health_bp.route('/weather/<zip_code>', methods=['GET'])
def get_weather(zip_code):
    """Get weather data for a zip code"""
    try:
        weather_data = WeatherService.get_weather_data(zip_code)
        return jsonify({
            'success': True,
            'weather': weather_data
        })
        
    except Exception as e:
        logger.error(f"Error getting weather data: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get weather data'
        }), 500

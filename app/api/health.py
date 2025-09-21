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

@health_bp.route('/environment-metrics', methods=['GET'])
def get_environment_metrics():
    """Get environment condition metrics for all patients"""
    try:
        from app.models import Patient
        from app.services import RiskAssessmentService
        
        # Get all patients
        patients = Patient.query.all()
        
        if not patients:
            return jsonify({
                'success': True,
                'message': 'No patients found',
                'environment_metrics': {
                    'total_patients': 0,
                    'patients_at_risk': 0,
                    'extreme_heat_conditions': 0,
                    'risk_distribution': {},
                    'weather_conditions': {}
                }
            })
        
        # Analyze environment conditions
        patients_at_risk = []
        extreme_heat_count = 0
        risk_distribution = {'low': 0, 'medium': 0, 'high': 0}
        weather_conditions = {}
        
        for patient in patients:
            try:
                # Get weather data for patient's location
                weather_data = WeatherService.get_weather_data(patient.zip_code)
                
                # Check for extreme heat conditions
                is_extreme_heat = weather_data.get('is_heat_wave', False) or weather_data.get('temperature', 0) > 35
                if is_extreme_heat:
                    extreme_heat_count += 1
                
                # Perform risk assessment
                risk_data = RiskAssessmentService.assess_risk(patient)
                risk_level = risk_data['risk_level']
                risk_distribution[risk_level] += 1
                
                # Add to at-risk patients if risk level is medium or high
                if risk_level in ['medium', 'high']:
                    patients_at_risk.append({
                        'patient_id': patient.id,
                        'name': patient.name,
                        'age': patient.age,
                        'zip_code': patient.zip_code,
                        'risk_level': risk_level,
                        'risk_score': risk_data['risk_score'],
                        'heat_wave_risk': risk_data.get('heat_wave_risk', False),
                        'weather_conditions': weather_data,
                        'risk_factors': risk_data.get('factors', {})
                    })
                
                # Aggregate weather conditions by location
                location_key = patient.zip_code
                if location_key not in weather_conditions:
                    weather_conditions[location_key] = {
                        'temperature': weather_data.get('temperature', 0),
                        'feels_like': weather_data.get('feels_like', 0),
                        'humidity': weather_data.get('humidity', 0),
                        'description': weather_data.get('description', 'Unknown'),
                        'is_heat_wave': weather_data.get('is_heat_wave', False),
                        'heat_index': weather_data.get('heat_index', 0),
                        'patient_count': 0
                    }
                weather_conditions[location_key]['patient_count'] += 1
                
            except Exception as e:
                logger.warning(f"Error processing patient {patient.id}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'environment_metrics': {
                'total_patients': len(patients),
                'patients_at_risk': len(patients_at_risk),
                'extreme_heat_conditions': extreme_heat_count,
                'risk_distribution': risk_distribution,
                'weather_conditions': weather_conditions,
                'at_risk_patients': patients_at_risk
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting environment metrics: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get environment metrics'
        }), 500

@health_bp.route('/environment-metrics/<zip_code>', methods=['GET'])
def get_environment_metrics_by_location(zip_code):
    """Get environment condition metrics for a specific location"""
    try:
        from app.models import Patient
        from app.services import RiskAssessmentService
        
        # Get patients in specific location
        patients = Patient.query.filter_by(zip_code=zip_code).all()
        
        if not patients:
            return jsonify({
                'success': True,
                'message': f'No patients found in location {zip_code}',
                'environment_metrics': {
                    'location': zip_code,
                    'total_patients': 0,
                    'patients_at_risk': 0,
                    'extreme_heat_conditions': False,
                    'risk_distribution': {},
                    'weather_conditions': {}
                }
            })
        
        # Get weather data for the location
        weather_data = WeatherService.get_weather_data(zip_code)
        
        # Analyze patients in this location
        patients_at_risk = []
        extreme_heat_conditions = weather_data.get('is_heat_wave', False) or weather_data.get('temperature', 0) > 35
        risk_distribution = {'low': 0, 'medium': 0, 'high': 0}
        
        for patient in patients:
            try:
                # Perform risk assessment
                risk_data = RiskAssessmentService.assess_risk(patient)
                risk_level = risk_data['risk_level']
                risk_distribution[risk_level] += 1
                
                # Add to at-risk patients if risk level is medium or high
                if risk_level in ['medium', 'high']:
                    patients_at_risk.append({
                        'patient_id': patient.id,
                        'name': patient.name,
                        'age': patient.age,
                        'risk_level': risk_level,
                        'risk_score': risk_data['risk_score'],
                        'heat_wave_risk': risk_data.get('heat_wave_risk', False),
                        'risk_factors': risk_data.get('factors', {})
                    })
                
            except Exception as e:
                logger.warning(f"Error processing patient {patient.id}: {e}")
                continue
        
        return jsonify({
            'success': True,
            'environment_metrics': {
                'location': zip_code,
                'total_patients': len(patients),
                'patients_at_risk': len(patients_at_risk),
                'extreme_heat_conditions': extreme_heat_conditions,
                'risk_distribution': risk_distribution,
                'weather_conditions': weather_data,
                'at_risk_patients': patients_at_risk
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting environment metrics for location {zip_code}: {e}")
        return jsonify({
            'success': False,
            'error': f'Failed to get environment metrics for location {zip_code}'
        }), 500

@health_bp.route('/weather-forecast/<zip_code>', methods=['GET'])
def get_weather_forecast(zip_code):
    """Get weather forecast for a zip code"""
    try:
        days = request.args.get('days', 5, type=int)
        forecast_data = WeatherService.get_weather_forecast(zip_code, days)
        return jsonify({
            'success': True,
            'forecast': forecast_data
        })
        
    except Exception as e:
        logger.error(f"Error getting weather forecast: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get weather forecast'
        }), 500

@health_bp.route('/weather-alerts/<zip_code>', methods=['GET'])
def get_weather_alerts(zip_code):
    """Get weather alerts and warnings for a zip code"""
    try:
        alert_data = WeatherService.get_weather_alerts(zip_code)
        return jsonify({
            'success': True,
            'alerts': alert_data
        })
        
    except Exception as e:
        logger.error(f"Error getting weather alerts: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get weather alerts'
        }), 500

@health_bp.route('/weather-ai-analysis/<zip_code>', methods=['GET'])
def get_weather_ai_analysis(zip_code):
    """Get AI-powered weather risk analysis for a zip code"""
    try:
        from app.services import AIService
        from app.models import Patient
        
        # Get weather data
        weather_data = WeatherService.get_weather_data(zip_code)
        
        # Get patient count in this location
        patient_count = Patient.query.filter_by(zip_code=zip_code).count()
        
        # Get AI analysis
        ai_analysis = AIService.get_weather_risk_analysis(weather_data, patient_count)
        
        return jsonify({
            'success': True,
            'weather_data': weather_data,
            'patient_count': patient_count,
            'ai_analysis': ai_analysis,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error getting weather AI analysis: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get weather AI analysis'
        }), 500

@health_bp.route('/weather-onecall/<zip_code>', methods=['GET'])
def get_weather_onecall(zip_code):
    """Get comprehensive weather data using OneCall API"""
    try:
        from app.services.weather_service import WeatherService
        
        weather_data = WeatherService.get_onecall_weather_data(zip_code)
        return jsonify({
            'success': True,
            'weather': weather_data
        })
        
    except Exception as e:
        logger.error(f"Error getting OneCall weather data: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get OneCall weather data'
        }), 500
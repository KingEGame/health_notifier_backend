from flask import Blueprint, request, jsonify, Response, stream_template
from app.extensions import db
from app.models import Patient
from app.schemas import PatientCreateSchema, PatientUpdateSchema, PatientResponseSchema
from marshmallow import ValidationError
from app.utils.exceptions import ValidationException
import logging
import json

logger = logging.getLogger(__name__)

patients_bp = Blueprint('patients', __name__)

@patients_bp.route('/patients', methods=['POST'])
def create_patient():
    """Create a new patient"""
    try:
        schema = PatientCreateSchema()
        data = schema.load(request.json)
        
        # Create patient
        patient = Patient(
            name=data['name'],
            age=data['age'],
            pregnancy_icd10=data.get('pregnancy_icd10'),
            pregnancy_description=data.get('pregnancy_description'),
            comorbidity_icd10=data.get('comorbidity_icd10'),
            comorbidity_description=data.get('comorbidity_description'),
            weeks_pregnant=data.get('weeks_pregnant'),
            address=data.get('address'),
            zip_code=data['zip_code'],
            phone_number=data.get('phone_number'),
            email=data.get('email')
        )
        
        # Set ICD10 conditions if provided (backward compatibility)
        if 'conditions_icd10' in data:
            patient.set_conditions(data['conditions_icd10'])
        
        db.session.add(patient)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Patient created successfully',
            'patient': patient.to_dict()
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation failed',
            'details': e.messages
        }), 400
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to create patient'
        }), 500

@patients_bp.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get patient by ID from CSV data"""
    try:
        from app.models.csv_models import csv_manager
        
        # Get all patients from CSV
        all_patients = csv_manager.get_all_patients()
        
        # Find patient by ID
        patient = None
        for p in all_patients:
            if p.id == patient_id:
                patient = p
                break
        
        if not patient:
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404
        
        # Convert to dict format with additional fields
        patient_dict = patient.to_dict()
        patient_dict.update({
            'trimester': patient._calculate_trimester(),
            'age_group': 'optimal' if 21 <= patient.age <= 30 else 'outside_optimal',
            'is_high_risk_age': patient.age < 21 or patient.age > 35,
            'medications': patient.get_medications_list(),
            'medication_notes': patient.medication_notes,
            'ndc_codes': patient.get_ndc_codes(),
            'conditions': patient.get_conditions(),
            'created_at': patient.created_at.isoformat() if hasattr(patient, 'created_at') and patient.created_at else None,
            'updated_at': patient.updated_at.isoformat() if hasattr(patient, 'updated_at') and patient.updated_at else None
        })
        
        return jsonify({
            'success': True,
            'patient': patient_dict
        })
        
    except Exception as e:
        logger.error(f"Error getting patient: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get patient'
        }), 500

@patients_bp.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update patient information"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        schema = PatientUpdateSchema()
        data = schema.load(request.json)
        
        # Update fields
        for field, value in data.items():
            if hasattr(patient, field):
                if field == 'conditions_icd10':
                    patient.set_conditions(value)
                else:
                    setattr(patient, field, value)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Patient updated successfully',
            'patient': patient.to_dict()
        })
        
    except ValidationError as e:
        return jsonify({
            'success': False,
            'error': 'Validation failed',
            'details': e.messages
        }), 400
    except Exception as e:
        logger.error(f"Error updating patient: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to update patient'
        }), 500

@patients_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete patient"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        db.session.delete(patient)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Patient deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting patient: {e}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Failed to delete patient'
        }), 500

@patients_bp.route('/patients', methods=['GET'])
def get_all_patients():
    """Get all patients with pagination from CSV data"""
    try:
        from app.models.csv_models import csv_manager
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        # Get all patients from CSV
        all_patients = csv_manager.get_all_patients()
        
        # Calculate pagination
        total = len(all_patients)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        patients_page = all_patients[start_idx:end_idx]
        
        # Convert to dict format
        patients_data = []
        for patient in patients_page:
            patient_dict = patient.to_dict()
            # Add additional fields for consistency
            patient_dict.update({
                'trimester': patient._calculate_trimester(),
                'age_group': 'optimal' if 21 <= patient.age <= 30 else 'outside_optimal',
                'is_high_risk_age': patient.age < 21 or patient.age > 35,
                'medications': patient.get_medications_list(),
                'medication_notes': patient.medication_notes,
                'ndc_codes': patient.get_ndc_codes(),
                'conditions': patient.get_conditions(),
                'created_at': patient.created_at.isoformat() if hasattr(patient, 'created_at') and patient.created_at else None,
                'updated_at': patient.updated_at.isoformat() if hasattr(patient, 'updated_at') and patient.updated_at else None
            })
            patients_data.append(patient_dict)
        
        return jsonify({
            'success': True,
            'patients': patients_data,
            'total': total,
            'pages': (total + per_page - 1) // per_page,  # Ceiling division
            'current_page': page,
            'per_page': per_page,
            'has_next': end_idx < total,
            'has_prev': page > 1
        })
        
    except Exception as e:
        logger.error(f"Error getting patients: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get patients'
        }), 500

@patients_bp.route('/patients/with-risks', methods=['GET'])
def get_all_patients_with_risks():
    """Get all patients with comprehensive risk assessments and AI recommendations"""
    try:
        from app.models.csv_models import csv_manager
        from app.services import RiskAssessmentService
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        risk_level = request.args.get('risk_level')  # 'low', 'medium', 'high'
        location = request.args.get('location')  # zip_code
        include_ai_suggestions = request.args.get('include_ai_suggestions', 'true').lower() == 'true'
        include_notifications = request.args.get('include_notifications', 'true').lower() == 'true'
        no_pagination = request.args.get('no_pagination', 'false').lower() == 'true'  # Get all patients without pagination
        
        # Get all patients from CSV
        all_patients = csv_manager.get_all_patients()
        
        # Filter by location if specified
        if location:
            all_patients = [p for p in all_patients if p.zip_code == location]
        
        # Process ALL patients with comprehensive data (no pagination limit)
        patients_data = []
        risk_distribution = {'low': 0, 'medium': 0, 'high': 0}
        patients_at_risk = 0
        
        for patient in all_patients:
            try:
                # Perform comprehensive risk assessment
                risk_data = RiskAssessmentService.assess_risk(patient)
                patient_risk_level = risk_data['risk_level']
                
                # Filter by risk level if specified
                if risk_level and patient_risk_level != risk_level:
                    continue
                
                risk_distribution[patient_risk_level] += 1
                
                if patient_risk_level in ['medium', 'high']:
                    patients_at_risk += 1
                
                # Prepare comprehensive patient data
                patient_info = {
                    # Basic patient information
                    'patient_id': patient.id,
                    'name': patient.name,
                    'age': patient.age,
                    'zip_code': patient.zip_code,
                    'phone_number': patient.phone_number,
                    'email': patient.email,
                    'address': patient.address,
                    
                    # Pregnancy information
                    'pregnancy_weeks': patient.weeks_pregnant,
                    'trimester': patient._calculate_trimester(),
                    'pregnancy_icd10': patient.pregnancy_icd10,
                    'pregnancy_description': patient.pregnancy_description,
                    
                    # Medical conditions
                    'comorbidity_icd10': patient.comorbidity_icd10,
                    'comorbidity_description': patient.comorbidity_description,
                    'conditions': patient.get_conditions(),
                    
                    # Medications
                    'medications': patient.get_medications_list(),
                    'medication_notes': patient.medication_notes,
                    'ndc_codes': patient.get_ndc_codes_list(),
                    
                    # Risk assessment
                    'risk_level': patient_risk_level,
                    'risk_score': risk_data['risk_score'],
                    'heat_wave_risk': risk_data.get('heat_wave_risk', False),
                    'risk_factors': risk_data.get('factors', {}),
                    'weather_conditions': risk_data.get('weather_data', {}),
                    
                    # Additional patient flags
                    'is_high_risk_age': patient.between_17_35,
                    'age_group': 'optimal' if patient.between_17_35 else 'outside_optimal',
                    
                    # Timestamps
                    'created_at': patient.created_at.isoformat() if patient.created_at else None,
                    'updated_at': patient.updated_at.isoformat() if patient.updated_at else None
                }
                
                # Add AI suggestions if requested
                if include_ai_suggestions:
                    try:
                        from app.services.ai_service import AIService
                        ai_suggestions = AIService.get_risk_recommendations(patient, risk_data)
                        patient_info['ai_suggestions'] = ai_suggestions
                    except Exception as e:
                        logger.warning(f"Failed to get AI suggestions for patient {patient.id}: {e}")
                        patient_info['ai_suggestions'] = {
                            'error': 'AI suggestions unavailable',
                            'fallback_recommendations': _get_fallback_recommendations(patient_risk_level, risk_data)
                        }
                
                # Add notifications if requested
                if include_notifications:
                    try:
                        notifications = csv_manager.get_notifications_by_patient(patient.id)
                        patient_info['notifications'] = [n.to_dict() for n in notifications]
                    except Exception as e:
                        logger.warning(f"Failed to get notifications for patient {patient.id}: {e}")
                        patient_info['notifications'] = []
                
                # Add risk assessment history
                try:
                    risk_history = csv_manager.get_risk_assessments_by_patient(patient.id)
                    patient_info['risk_history'] = [ra.to_dict() for ra in risk_history]
                except Exception as e:
                    logger.warning(f"Failed to get risk history for patient {patient.id}: {e}")
                    patient_info['risk_history'] = []
                
                patients_data.append(patient_info)
                
            except Exception as e:
                logger.warning(f"Error processing patient {patient.id}: {e}")
                continue
        
        # Apply pagination to processed data (unless no_pagination is true)
        total_processed = len(patients_data)
        
        if no_pagination:
            # Return all patients without pagination
            return jsonify({
                'success': True,
                'patients': patients_data,
                'pagination': {
                    'total': total_processed,
                    'pages': 1,
                    'current_page': 1,
                    'per_page': total_processed,
                    'has_next': False,
                    'has_prev': False,
                    'no_pagination': True
                },
                'summary': {
                    'total_patients': total_processed,
                    'total_processed_patients': total_processed,
                    'total_available_patients': len(all_patients),
                    'risk_distribution': risk_distribution,
                    'patients_at_risk': patients_at_risk,
                    'filters_applied': {
                        'risk_level': risk_level,
                        'location': location,
                        'include_ai_suggestions': include_ai_suggestions,
                        'include_notifications': include_notifications,
                        'no_pagination': True
                    }
                }
            })
        else:
            # Apply pagination
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            paginated_patients = patients_data[start_idx:end_idx]
            
            return jsonify({
                'success': True,
                'patients': paginated_patients,
                'pagination': {
                    'total': total_processed,
                    'pages': (total_processed + per_page - 1) // per_page,
                    'current_page': page,
                    'per_page': per_page,
                    'has_next': end_idx < total_processed,
                    'has_prev': page > 1,
                    'no_pagination': False
                },
                'summary': {
                    'total_patients': len(paginated_patients),
                    'total_processed_patients': total_processed,
                    'total_available_patients': len(all_patients),
                    'risk_distribution': risk_distribution,
                    'patients_at_risk': patients_at_risk,
                    'filters_applied': {
                        'risk_level': risk_level,
                        'location': location,
                        'include_ai_suggestions': include_ai_suggestions,
                        'include_notifications': include_notifications,
                        'no_pagination': False
                    }
                }
            })
        
    except Exception as e:
        logger.error(f"Error getting patients with risks: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get patients with risks'
        }), 500

def _get_fallback_recommendations(risk_level, risk_data):
    """Get fallback recommendations when AI service is unavailable"""
    recommendations = []
    
    if risk_level == 'high':
        recommendations.extend([
            "Немедленная консультация с врачом рекомендуется",
            "Тщательно следите за жизненными показателями",
            "Избегайте экстремальных погодных условий",
            "Убедитесь, что экстренный контакт доступен"
        ])
    elif risk_level == 'medium':
        recommendations.extend([
            "Рекомендуются регулярные медицинские осмотры",
            "Внимательно следите за симптомами",
            "Соблюдайте предписанный график приема лекарств",
            "Ведите здоровый образ жизни"
        ])
    else:
        recommendations.extend([
            "Продолжайте регулярное дородовое наблюдение",
            "Поддерживайте здоровую диету и физические упражнения",
            "Пейте достаточно воды",
            "Регулярные медицинские осмотры"
        ])
    
    # Add weather-specific recommendations
    if risk_data.get('heat_wave_risk', False):
        recommendations.extend([
            "Оставайтесь в помещении в часы пиковой жары",
            "Обеспечьте адекватную гидратацию",
            "Используйте кондиционер, если доступен",
            "Носите легкую, свободную одежду"
        ])
    
    return recommendations

@patients_bp.route('/patients/statistics', methods=['GET'])
def get_patients_statistics():
    """Get comprehensive statistics for all patients with risks and recommendations"""
    try:
        from app.models.csv_models import csv_manager
        from app.services import RiskAssessmentService
        
        # Get query parameters
        location = request.args.get('location')  # zip_code
        include_detailed_breakdown = request.args.get('include_detailed_breakdown', 'true').lower() == 'true'
        
        # Get all patients from CSV
        all_patients = csv_manager.get_all_patients()
        
        # Filter by location if specified
        if location:
            all_patients = [p for p in all_patients if p.zip_code == location]
        
        if not all_patients:
            return jsonify({
                'success': True,
                'statistics': {
                    'total_patients': 0,
                    'risk_distribution': {'low': 0, 'medium': 0, 'high': 0},
                    'patients_at_risk': 0,
                    'extreme_heat_risk': 0,
                    'average_risk_score': 0,
                    'age_distribution': {},
                    'trimester_distribution': {},
                    'medication_risks': {},
                    'condition_risks': {}
                }
            })
        
        # Initialize statistics
        risk_distribution = {'low': 0, 'medium': 0, 'high': 0}
        patients_at_risk = 0
        extreme_heat_risk = 0
        total_risk_score = 0
        risk_scores = []
        age_groups = {'under_21': 0, '21_30': 0, '31_35': 0, 'over_35': 0}
        trimester_distribution = {'1': 0, '2': 0, '3': 0, 'unknown': 0}
        medication_risks = {}
        condition_risks = {}
        
        # Process each patient
        for patient in all_patients:
            try:
                # Perform risk assessment
                risk_data = RiskAssessmentService.assess_risk(patient)
                risk_level = risk_data['risk_level']
                risk_score = risk_data['risk_score']
                
                # Update statistics
                risk_distribution[risk_level] += 1
                total_risk_score += risk_score
                risk_scores.append(risk_score)
                
                if risk_level in ['medium', 'high']:
                    patients_at_risk += 1
                
                if risk_data.get('heat_wave_risk', False):
                    extreme_heat_risk += 1
                
                # Age distribution
                if patient.age < 21:
                    age_groups['under_21'] += 1
                elif 21 <= patient.age <= 30:
                    age_groups['21_30'] += 1
                elif 31 <= patient.age <= 35:
                    age_groups['31_35'] += 1
                else:
                    age_groups['over_35'] += 1
                
                # Trimester distribution
                trimester = patient._calculate_trimester()
                if trimester:
                    trimester_distribution[str(trimester)] += 1
                else:
                    trimester_distribution['unknown'] += 1
                
                # Medication risks (if detailed breakdown requested)
                if include_detailed_breakdown:
                    medications = patient.get_medications_list()
                    for med in medications:
                        if med not in medication_risks:
                            medication_risks[med] = {'count': 0, 'risk_levels': {'low': 0, 'medium': 0, 'high': 0}}
                        medication_risks[med]['count'] += 1
                        medication_risks[med]['risk_levels'][risk_level] += 1
                
                # Condition risks (if detailed breakdown requested)
                if include_detailed_breakdown:
                    conditions = patient.get_conditions()
                    for condition in conditions:
                        if condition not in condition_risks:
                            condition_risks[condition] = {'count': 0, 'risk_levels': {'low': 0, 'medium': 0, 'high': 0}}
                        condition_risks[condition]['count'] += 1
                        condition_risks[condition]['risk_levels'][risk_level] += 1
                
            except Exception as e:
                logger.warning(f"Error processing patient {patient.id} for statistics: {e}")
                continue
        
        # Calculate averages and percentages
        average_risk_score = total_risk_score / len(all_patients) if all_patients else 0
        
        # Calculate risk percentages
        risk_percentages = {}
        for level, count in risk_distribution.items():
            risk_percentages[level] = round((count / len(all_patients)) * 100, 1) if all_patients else 0
        
        # Calculate age percentages
        age_percentages = {}
        for group, count in age_groups.items():
            age_percentages[group] = round((count / len(all_patients)) * 100, 1) if all_patients else 0
        
        # Calculate trimester percentages
        trimester_percentages = {}
        for trimester, count in trimester_distribution.items():
            trimester_percentages[trimester] = round((count / len(all_patients)) * 100, 1) if all_patients else 0
        
        # Prepare response
        statistics = {
            'total_patients': len(all_patients),
            'risk_distribution': risk_distribution,
            'risk_percentages': risk_percentages,
            'patients_at_risk': patients_at_risk,
            'patients_at_risk_percentage': round((patients_at_risk / len(all_patients)) * 100, 1) if all_patients else 0,
            'extreme_heat_risk': extreme_heat_risk,
            'extreme_heat_risk_percentage': round((extreme_heat_risk / len(all_patients)) * 100, 1) if all_patients else 0,
            'average_risk_score': round(average_risk_score, 2),
            'age_distribution': age_groups,
            'age_percentages': age_percentages,
            'trimester_distribution': trimester_distribution,
            'trimester_percentages': trimester_percentages,
            'filters_applied': {
                'location': location,
                'include_detailed_breakdown': include_detailed_breakdown
            }
        }
        
        # Add detailed breakdowns if requested
        if include_detailed_breakdown:
            statistics['medication_risks'] = medication_risks
            statistics['condition_risks'] = condition_risks
            
            # Top risk medications
            top_medications = sorted(medication_risks.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
            statistics['top_medications'] = top_medications
            
            # Top risk conditions
            top_conditions = sorted(condition_risks.items(), key=lambda x: x[1]['count'], reverse=True)[:10]
            statistics['top_conditions'] = top_conditions
        
        return jsonify({
            'success': True,
            'statistics': statistics
        })
        
    except Exception as e:
        logger.error(f"Error getting patients statistics: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get patients statistics'
        }), 500

@patients_bp.route('/patients/with-risks/stream', methods=['GET'])
def get_all_patients_with_risks_stream():
    """Stream all patients with comprehensive risk assessments and AI recommendations"""
    try:
        from app.models.csv_models import csv_manager
        from app.services import RiskAssessmentService
        
        # Get query parameters
        risk_level = request.args.get('risk_level')  # 'low', 'medium', 'high'
        location = request.args.get('location')  # zip_code
        include_ai_suggestions = request.args.get('include_ai_suggestions', 'true').lower() == 'true'
        include_notifications = request.args.get('include_notifications', 'true').lower() == 'true'
        batch_size = request.args.get('batch_size', 10, type=int)  # Number of patients per batch
        
        def generate_patients():
            try:
                # Get all patients from CSV
                all_patients = csv_manager.get_all_patients()
                
                # Filter by location if specified
                if location:
                    all_patients = [p for p in all_patients if p.zip_code == location]
                
                # Send initial metadata
                yield json.dumps({
                    'type': 'metadata',
                    'total_patients': len(all_patients),
                    'batch_size': batch_size,
                    'filters_applied': {
                        'risk_level': risk_level,
                        'location': location,
                        'include_ai_suggestions': include_ai_suggestions,
                        'include_notifications': include_notifications
                    }
                }) + '\n'
                
                # Process patients in batches
                patients_data = []
                risk_distribution = {'low': 0, 'medium': 0, 'high': 0}
                patients_at_risk = 0
                processed_count = 0
                
                for i, patient in enumerate(all_patients):
                    try:
                        # Perform comprehensive risk assessment
                        risk_data = RiskAssessmentService.assess_risk(patient)
                        patient_risk_level = risk_data['risk_level']
                        
                        # Filter by risk level if specified
                        if risk_level and patient_risk_level != risk_level:
                            continue
                        
                        risk_distribution[patient_risk_level] += 1
                        
                        if patient_risk_level in ['medium', 'high']:
                            patients_at_risk += 1
                        
                        # Prepare comprehensive patient data
                        patient_info = {
                            # Basic patient information
                            'patient_id': patient.id,
                            'name': patient.name,
                            'age': patient.age,
                            'zip_code': patient.zip_code,
                            'phone_number': patient.phone_number,
                            'email': patient.email,
                            'address': patient.address,
                            
                            # Pregnancy information
                            'pregnancy_weeks': patient.weeks_pregnant,
                            'trimester': patient._calculate_trimester(),
                            'pregnancy_icd10': patient.pregnancy_icd10,
                            'pregnancy_description': patient.pregnancy_description,
                            
                            # Medical conditions
                            'comorbidity_icd10': patient.comorbidity_icd10,
                            'comorbidity_description': patient.comorbidity_description,
                            'conditions': patient.get_conditions(),
                            
                            # Medications
                            'medications': patient.get_medications_list(),
                            'medication_notes': patient.medication_notes,
                            'ndc_codes': patient.get_ndc_codes_list(),
                            
                            # Risk assessment
                            'risk_level': patient_risk_level,
                            'risk_score': risk_data['risk_score'],
                            'heat_wave_risk': risk_data.get('heat_wave_risk', False),
                            'risk_factors': risk_data.get('factors', {}),
                            'weather_conditions': risk_data.get('weather_data', {}),
                            
                            # Additional patient flags
                            'is_high_risk_age': patient.between_17_35,
                            'age_group': 'optimal' if patient.between_17_35 else 'outside_optimal',
                            
                            # Timestamps
                            'created_at': patient.created_at.isoformat() if patient.created_at else None,
                            'updated_at': patient.updated_at.isoformat() if patient.updated_at else None
                        }
                        
                        # Add AI suggestions if requested
                        if include_ai_suggestions:
                            try:
                                from app.services.ai_service import AIService
                                ai_suggestions = AIService.get_risk_recommendations(patient, risk_data)
                                patient_info['ai_suggestions'] = ai_suggestions
                            except Exception as e:
                                logger.warning(f"Failed to get AI suggestions for patient {patient.id}: {e}")
                                patient_info['ai_suggestions'] = {
                                    'error': 'AI suggestions unavailable',
                                    'fallback_recommendations': _get_fallback_recommendations(patient_risk_level, risk_data)
                                }
                        
                        # Add notifications if requested
                        if include_notifications:
                            try:
                                notifications = csv_manager.get_notifications_by_patient(patient.id)
                                patient_info['notifications'] = [n.to_dict() for n in notifications]
                            except Exception as e:
                                logger.warning(f"Failed to get notifications for patient {patient.id}: {e}")
                                patient_info['notifications'] = []
                        
                        # Add risk assessment history
                        try:
                            risk_history = csv_manager.get_risk_assessments_by_patient(patient.id)
                            patient_info['risk_history'] = [ra.to_dict() for ra in risk_history]
                        except Exception as e:
                            logger.warning(f"Failed to get risk history for patient {patient.id}: {e}")
                            patient_info['risk_history'] = []
                        
                        patients_data.append(patient_info)
                        processed_count += 1
                        
                        # Send batch when batch_size is reached
                        if len(patients_data) >= batch_size:
                            yield json.dumps({
                                'type': 'batch',
                                'patients': patients_data,
                                'processed_count': processed_count,
                                'total_patients': len(all_patients)
                            }) + '\n'
                            patients_data = []
                        
                    except Exception as e:
                        logger.warning(f"Error processing patient {patient.id}: {e}")
                        continue
                
                # Send remaining patients
                if patients_data:
                    yield json.dumps({
                        'type': 'batch',
                        'patients': patients_data,
                        'processed_count': processed_count,
                        'total_patients': len(all_patients)
                    }) + '\n'
                
                # Send final summary
                yield json.dumps({
                    'type': 'summary',
                    'total_processed': processed_count,
                    'total_available_patients': len(all_patients),
                    'risk_distribution': risk_distribution,
                    'patients_at_risk': patients_at_risk,
                    'filters_applied': {
                        'risk_level': risk_level,
                        'location': location,
                        'include_ai_suggestions': include_ai_suggestions,
                        'include_notifications': include_notifications
                    }
                }) + '\n'
                
            except Exception as e:
                logger.error(f"Error in stream generation: {e}")
                yield json.dumps({
                    'type': 'error',
                    'error': 'Failed to generate patient stream'
                }) + '\n'
        
        return Response(
            generate_patients(),
            mimetype='application/x-ndjson',
            headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no'  # Disable nginx buffering
            }
        )
        
    except Exception as e:
        logger.error(f"Error setting up patient stream: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to setup patient stream'
        }), 500
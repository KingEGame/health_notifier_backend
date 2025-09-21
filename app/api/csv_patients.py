from flask import Blueprint, request, jsonify
from app.models.csv_models import csv_manager
from app.schemas import PatientCreateSchema, PatientUpdateSchema, PatientResponseSchema
from marshmallow import ValidationError
from app.utils.exceptions import ValidationException
import logging

logger = logging.getLogger(__name__)

csv_patients_bp = Blueprint('csv_patients', __name__)

@csv_patients_bp.route('/patients', methods=['POST'])
def create_patient():
    """Create a new patient"""
    try:
        schema = PatientCreateSchema()
        data = schema.load(request.json)
        
        # Create patient using CSV manager
        patient = csv_manager.create_patient(data)
        
        # Serialize response
        response_schema = PatientResponseSchema()
        result = response_schema.dump(patient.to_dict())
        
        logger.info(f"Created patient: {patient.name} (ID: {patient.id})")
        
        return jsonify({
            'success': True,
            'message': 'Patient created successfully',
            'patient': result
        }), 201
        
    except ValidationError as e:
        logger.warning(f"Validation error creating patient: {e.messages}")
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.messages
        }), 400
        
    except Exception as e:
        logger.error(f"Error creating patient: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to create patient'
        }), 500

@csv_patients_bp.route('/patients/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get a patient by ID"""
    try:
        patient = csv_manager.get_patient_by_id(patient_id)
        
        if not patient:
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404
        
        # Serialize response
        response_schema = PatientResponseSchema()
        result = response_schema.dump(patient.to_dict())
        
        return jsonify({
            'success': True,
            'patient': result
        })
        
    except Exception as e:
        logger.error(f"Error getting patient {patient_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get patient'
        }), 500

@csv_patients_bp.route('/patients/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """Update a patient"""
    try:
        schema = PatientUpdateSchema()
        data = schema.load(request.json)
        
        # Update patient using CSV manager
        patient = csv_manager.update_patient(patient_id, data)
        
        if not patient:
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404
        
        # Serialize response
        response_schema = PatientResponseSchema()
        result = response_schema.dump(patient.to_dict())
        
        logger.info(f"Updated patient: {patient.name} (ID: {patient.id})")
        
        return jsonify({
            'success': True,
            'message': 'Patient updated successfully',
            'patient': result
        })
        
    except ValidationError as e:
        logger.warning(f"Validation error updating patient {patient_id}: {e.messages}")
        return jsonify({
            'success': False,
            'error': 'Validation error',
            'details': e.messages
        }), 400
        
    except Exception as e:
        logger.error(f"Error updating patient {patient_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to update patient'
        }), 500

@csv_patients_bp.route('/patients/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete a patient"""
    try:
        success = csv_manager.delete_patient(patient_id)
        
        if not success:
            return jsonify({
                'success': False,
                'error': 'Patient not found'
            }), 404
        
        logger.info(f"Deleted patient ID: {patient_id}")
        
        return jsonify({
            'success': True,
            'message': 'Patient deleted successfully'
        })
        
    except Exception as e:
        logger.error(f"Error deleting patient {patient_id}: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to delete patient'
        }), 500

@csv_patients_bp.route('/csv-patients', methods=['GET'])
def get_all_patients():
    """Get all patients with optional filtering"""
    try:
        # Get query parameters
        zip_code = request.args.get('zip_code')
        age_min = request.args.get('age_min', type=int)
        age_max = request.args.get('age_max', type=int)
        risk_level = request.args.get('risk_level')
        
        # Get all patients
        patients = csv_manager.get_all_patients()
        
        # Apply filters
        filtered_patients = []
        for patient in patients:
            # Filter by zip code
            if zip_code and patient.zip_code != zip_code:
                continue
            
            # Filter by age range
            if age_min and patient.age < age_min:
                continue
            if age_max and patient.age > age_max:
                continue
            
            # Note: Risk level filtering would require risk assessment data
            # For now, we'll skip this filter
            
            filtered_patients.append(patient)
        
        # Serialize response
        response_schema = PatientResponseSchema(many=True)
        result = response_schema.dump([p.to_dict() for p in filtered_patients])
        
        return jsonify({
            'success': True,
            'patients': result,
            'total': len(filtered_patients),
            'filters': {
                'zip_code': zip_code,
                'age_min': age_min,
                'age_max': age_max,
                'risk_level': risk_level
            }
        })
        
    except Exception as e:
        logger.error(f"Error getting patients: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get patients'
        }), 500

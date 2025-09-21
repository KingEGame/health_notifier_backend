from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Patient
from app.schemas import PatientCreateSchema, PatientUpdateSchema, PatientResponseSchema
from marshmallow import ValidationError
from app.utils.exceptions import ValidationException
import logging

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
    """Get patient by ID"""
    try:
        patient = Patient.query.get_or_404(patient_id)
        return jsonify({
            'success': True,
            'patient': patient.to_dict()
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
    """Get all patients with pagination"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        patients = Patient.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'patients': [patient.to_dict() for patient in patients.items],
            'total': patients.total,
            'pages': patients.pages,
            'current_page': page
        })
        
    except Exception as e:
        logger.error(f"Error getting patients: {e}")
        return jsonify({
            'success': False,
            'error': 'Failed to get patients'
        }), 500

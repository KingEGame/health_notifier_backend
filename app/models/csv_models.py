"""
Модели для работы с CSV данными
CSV-based models for data storage
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
from app.services.csv_service import CSVService

class CSVPatient:
    """Модель пациента для работы с CSV"""
    
    def __init__(self, data: Dict):
        self.id = data.get('id')
        self.name = data.get('name', '')
        self.age = data.get('age', 0)
        self.pregnancy_icd10 = data.get('pregnancy_icd10', '')
        self.pregnancy_description = data.get('pregnancy_description', '')
        self.comorbidity_icd10 = data.get('comorbidity_icd10', '')
        self.comorbidity_description = data.get('comorbidity_description', '')
        self.weeks_pregnant = data.get('weeks_pregnant', 0)
        self.address = data.get('address', '')
        self.zip_code = data.get('zip_code', '')
        self.phone_number = data.get('phone_number', '')
        self.email = data.get('email', '')
        self.medications = data.get('medications', '')
        self.medication_notes = data.get('medication_notes', '')
        self.ndc_codes = data.get('ndc_codes', '')
        self.between_17_35 = data.get('between_17_35', False)
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
    
    def get_medications_list(self) -> List[str]:
        """Получает список лекарств"""
        if not self.medications:
            return []
        return [med.strip() for med in self.medications.split(';') if med.strip()]
    
    def get_ndc_codes_list(self) -> List[str]:
        """Получает список NDC кодов"""
        if not self.ndc_codes:
            return []
        return [code.strip() for code in self.ndc_codes.split(';') if code.strip()]
    
    def get_conditions(self) -> List[str]:
        """Получает список состояний"""
        conditions = []
        if self.pregnancy_icd10:
            conditions.append(f"{self.pregnancy_icd10}: {self.pregnancy_description}")
        if self.comorbidity_icd10:
            conditions.append(f"{self.comorbidity_icd10}: {self.comorbidity_description}")
        return conditions
    
    def to_dict(self) -> Dict:
        """Конвертирует в словарь"""
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'pregnancy_icd10': self.pregnancy_icd10,
            'pregnancy_description': self.pregnancy_description,
            'comorbidity_icd10': self.comorbidity_icd10,
            'comorbidity_description': self.comorbidity_description,
            'weeks_pregnant': self.weeks_pregnant,
            'address': self.address,
            'zip_code': self.zip_code,
            'phone_number': self.phone_number,
            'email': self.email,
            'medications': self.medications,
            'medication_notes': self.medication_notes,
            'ndc_codes': self.ndc_codes,
            'between_17_35': self.between_17_35,
            'medications_list': self.get_medications_list(),
            'ndc_codes_list': self.get_ndc_codes_list(),
            'conditions': self.get_conditions(),
            'is_high_risk_age': self.between_17_35,
            'trimester': self._calculate_trimester(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def _calculate_trimester(self) -> Optional[int]:
        """Вычисляет триместр беременности"""
        if not self.weeks_pregnant:
            return None
        
        if self.weeks_pregnant <= 12:
            return 1
        elif self.weeks_pregnant <= 24:
            return 2
        else:
            return 3

class CSVRiskAssessment:
    """Модель оценки риска для работы с CSV"""
    
    def __init__(self, data: Dict):
        self.id = data.get('id')
        self.patient_id = data.get('patient_id')
        self.risk_level = data.get('risk_level', 'low')
        self.risk_score = data.get('risk_score', 0)
        self.heat_wave_risk = data.get('heat_wave_risk', False)
        self.risk_factors = data.get('risk_factors', {})
        self.weather_data = data.get('weather_data', {})
        self.assessment_date = data.get('assessment_date')
        self.created_at = data.get('created_at')
    
    def to_dict(self) -> Dict:
        """Конвертирует в словарь"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'risk_level': self.risk_level,
            'risk_score': self.risk_score,
            'heat_wave_risk': self.heat_wave_risk,
            'risk_factors': self.risk_factors,
            'weather_data': self.weather_data,
            'assessment_date': self.assessment_date.isoformat() if self.assessment_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CSVNotification:
    """Модель уведомления для работы с CSV"""
    
    def __init__(self, data: Dict):
        self.id = data.get('id')
        self.patient_id = data.get('patient_id')
        self.message = data.get('message', '')
        self.notification_type = data.get('notification_type', 'general')
        self.priority = data.get('priority', 'medium')
        self.sent_at = data.get('sent_at')
        self.status = data.get('status', 'pending')
        self.created_at = data.get('created_at')
    
    def to_dict(self) -> Dict:
        """Конвертирует в словарь"""
        return {
            'id': self.id,
            'patient_id': self.patient_id,
            'message': self.message,
            'notification_type': self.notification_type,
            'priority': self.priority,
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class CSVModelManager:
    """Менеджер для работы с CSV моделями"""
    
    def __init__(self):
        self.csv_service = CSVService()
    
    # Методы для работы с пациентами
    def get_all_patients(self) -> List[CSVPatient]:
        """Получает всех пациентов"""
        patients_data = self.csv_service.get_all_patients()
        return [CSVPatient(data) for data in patients_data]
    
    def get_patient_by_id(self, patient_id: int) -> Optional[CSVPatient]:
        """Получает пациента по ID"""
        patient_data = self.csv_service.get_patient_by_id(patient_id)
        if patient_data:
            return CSVPatient(patient_data)
        return None
    
    def create_patient(self, patient_data: Dict) -> CSVPatient:
        """Создает нового пациента"""
        created_data = self.csv_service.create_patient(patient_data)
        return CSVPatient(created_data)
    
    def update_patient(self, patient_id: int, update_data: Dict) -> Optional[CSVPatient]:
        """Обновляет пациента"""
        updated_data = self.csv_service.update_patient(patient_id, update_data)
        if updated_data:
            return CSVPatient(updated_data)
        return None
    
    def delete_patient(self, patient_id: int) -> bool:
        """Удаляет пациента"""
        return self.csv_service.delete_patient(patient_id)
    
    # Методы для работы с оценками риска
    def create_risk_assessment(self, assessment_data: Dict) -> CSVRiskAssessment:
        """Создает новую оценку риска"""
        created_data = self.csv_service.create_risk_assessment(assessment_data)
        return CSVRiskAssessment(created_data)
    
    def get_risk_assessments_by_patient(self, patient_id: int) -> List[CSVRiskAssessment]:
        """Получает оценки риска для пациента"""
        assessments_data = self.csv_service.get_risk_assessments_by_patient(patient_id)
        return [CSVRiskAssessment(data) for data in assessments_data]
    
    # Методы для работы с уведомлениями
    def create_notification(self, notification_data: Dict) -> CSVNotification:
        """Создает новое уведомление"""
        created_data = self.csv_service.create_notification(notification_data)
        return CSVNotification(created_data)
    
    def get_notifications_by_patient(self, patient_id: int) -> List[CSVNotification]:
        """Получает уведомления для пациента"""
        notifications_data = self.csv_service.get_notifications_by_patient(patient_id)
        return [CSVNotification(data) for data in notifications_data]

# Глобальный экземпляр менеджера
csv_manager = CSVModelManager()

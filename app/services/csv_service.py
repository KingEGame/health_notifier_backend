"""
Сервис для работы с CSV файлами
CSV Service for data storage and retrieval
"""

import csv
import os
import json
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class CSVService:
    """Сервис для работы с CSV файлами"""
    
    def __init__(self, instance_dir: str = "instance"):
        self.instance_dir = instance_dir
        self.patients_file = os.path.join(instance_dir, "patients.csv")
        self.risk_assessments_file = os.path.join(instance_dir, "risk_assessments.csv")
        self.notifications_file = os.path.join(instance_dir, "notifications.csv")
        
        # Создаем файлы если их нет
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Создает CSV файлы если их нет"""
        os.makedirs(self.instance_dir, exist_ok=True)
        
        # Создаем файл пациентов если его нет
        if not os.path.exists(self.patients_file):
            self._create_patients_file()
        
        # Создаем файл оценок риска если его нет
        if not os.path.exists(self.risk_assessments_file):
            self._create_risk_assessments_file()
        
        # Создаем файл уведомлений если его нет
        if not os.path.exists(self.notifications_file):
            self._create_notifications_file()
    
    def _create_patients_file(self):
        """Создает файл пациентов с заголовками"""
        headers = [
            'id', 'name', 'age', 'pregnancy_icd10', 'pregnancy_description',
            'comorbidity_icd10', 'comorbidity_description', 'weeks_pregnant',
            'address', 'zip_code', 'phone_number', 'email', 'medications',
            'medication_notes', 'ndc_codes', 'between_17_35', 'created_at', 'updated_at'
        ]
        
        with open(self.patients_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
    
    def _create_risk_assessments_file(self):
        """Создает файл оценок риска с заголовками"""
        headers = [
            'id', 'patient_id', 'risk_level', 'risk_score', 'heat_wave_risk',
            'risk_factors', 'weather_data', 'assessment_date', 'created_at'
        ]
        
        with open(self.risk_assessments_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
    
    def _create_notifications_file(self):
        """Создает файл уведомлений с заголовками"""
        headers = [
            'id', 'patient_id', 'message', 'notification_type', 'priority',
            'sent_at', 'status', 'created_at'
        ]
        
        with open(self.notifications_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
    
    def _get_next_id(self, file_path: str) -> int:
        """Получает следующий ID для записи"""
        if not os.path.exists(file_path):
            return 1
        
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            max_id = 0
            for row in reader:
                if 'id' in row and row['id']:
                    max_id = max(max_id, int(row['id']))
            return max_id + 1
    
    def _read_csv(self, file_path: str) -> List[Dict]:
        """Читает CSV файл и возвращает список словарей"""
        if not os.path.exists(file_path):
            return []
        
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Конвертируем JSON поля
                for key, value in row.items():
                    if value and key in ['risk_factors', 'weather_data']:
                        try:
                            row[key] = json.loads(value)
                        except json.JSONDecodeError:
                            row[key] = {}
                    elif value and key in ['created_at', 'updated_at', 'assessment_date', 'sent_at']:
                        try:
                            row[key] = datetime.fromisoformat(value)
                        except ValueError:
                            pass
                    elif value and key == 'id':
                        try:
                            row[key] = int(value)
                        except ValueError:
                            pass
                    elif value and key in ['age', 'weeks_pregnant', 'risk_score']:
                        try:
                            row[key] = int(value)
                        except ValueError:
                            pass
                    elif value and key in ['between_17_35', 'heat_wave_risk']:
                        try:
                            row[key] = bool(int(value))
                        except ValueError:
                            row[key] = False
                
                data.append(row)
        
        return data
    
    def _write_csv(self, file_path: str, data: List[Dict], headers: List[str]):
        """Записывает данные в CSV файл"""
        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            
            for row in data:
                # Конвертируем сложные типы в строки
                csv_row = {}
                for key, value in row.items():
                    if isinstance(value, dict):
                        csv_row[key] = json.dumps(value)
                    elif isinstance(value, datetime):
                        csv_row[key] = value.isoformat()
                    elif isinstance(value, bool):
                        csv_row[key] = int(value)
                    else:
                        csv_row[key] = value
                
                writer.writerow(csv_row)
    
    # Методы для работы с пациентами
    def get_all_patients(self) -> List[Dict]:
        """Получает всех пациентов"""
        return self._read_csv(self.patients_file)
    
    def get_patient_by_id(self, patient_id: int) -> Optional[Dict]:
        """Получает пациента по ID"""
        patients = self.get_all_patients()
        for patient in patients:
            if patient.get('id') == patient_id:
                return patient
        return None
    
    def create_patient(self, patient_data: Dict) -> Dict:
        """Создает нового пациента"""
        patients = self.get_all_patients()
        
        # Генерируем ID
        patient_id = self._get_next_id(self.patients_file)
        
        # Подготавливаем данные
        now = datetime.utcnow()
        patient = {
            'id': patient_id,
            'name': patient_data.get('name', ''),
            'age': patient_data.get('age', 0),
            'pregnancy_icd10': patient_data.get('pregnancy_icd10', ''),
            'pregnancy_description': patient_data.get('pregnancy_description', ''),
            'comorbidity_icd10': patient_data.get('comorbidity_icd10', ''),
            'comorbidity_description': patient_data.get('comorbidity_description', ''),
            'weeks_pregnant': patient_data.get('weeks_pregnant', 0),
            'address': patient_data.get('address', ''),
            'zip_code': patient_data.get('zip_code', ''),
            'phone_number': patient_data.get('phone_number', ''),
            'email': patient_data.get('email', ''),
            'medications': patient_data.get('medications', ''),
            'medication_notes': patient_data.get('medication_notes', ''),
            'ndc_codes': patient_data.get('ndc_codes', ''),
            'between_17_35': patient_data.get('between_17_35', False),
            'created_at': now,
            'updated_at': now
        }
        
        patients.append(patient)
        
        # Записываем обратно в файл
        headers = [
            'id', 'name', 'age', 'pregnancy_icd10', 'pregnancy_description',
            'comorbidity_icd10', 'comorbidity_description', 'weeks_pregnant',
            'address', 'zip_code', 'phone_number', 'email', 'medications',
            'medication_notes', 'ndc_codes', 'between_17_35', 'created_at', 'updated_at'
        ]
        self._write_csv(self.patients_file, patients, headers)
        
        return patient
    
    def update_patient(self, patient_id: int, update_data: Dict) -> Optional[Dict]:
        """Обновляет пациента"""
        patients = self.get_all_patients()
        
        for i, patient in enumerate(patients):
            if patient.get('id') == patient_id:
                # Обновляем поля
                for key, value in update_data.items():
                    if key in patient and key not in ['id', 'created_at']:
                        patient[key] = value
                
                patient['updated_at'] = datetime.utcnow()
                patients[i] = patient
                
                # Записываем обратно в файл
                headers = [
                    'id', 'name', 'age', 'pregnancy_icd10', 'pregnancy_description',
                    'comorbidity_icd10', 'comorbidity_description', 'weeks_pregnant',
                    'address', 'zip_code', 'phone_number', 'email', 'medications',
                    'medication_notes', 'ndc_codes', 'between_17_35', 'created_at', 'updated_at'
                ]
                self._write_csv(self.patients_file, patients, headers)
                
                return patient
        
        return None
    
    def delete_patient(self, patient_id: int) -> bool:
        """Удаляет пациента"""
        patients = self.get_all_patients()
        
        for i, patient in enumerate(patients):
            if patient.get('id') == patient_id:
                del patients[i]
                
                # Записываем обратно в файл
                headers = [
                    'id', 'name', 'age', 'pregnancy_icd10', 'pregnancy_description',
                    'comorbidity_icd10', 'comorbidity_description', 'weeks_pregnant',
                    'address', 'zip_code', 'phone_number', 'email', 'medications',
                    'medication_notes', 'ndc_codes', 'between_17_35', 'created_at', 'updated_at'
                ]
                self._write_csv(self.patients_file, patients, headers)
                
                return True
        
        return False
    
    # Методы для работы с оценками риска
    def create_risk_assessment(self, assessment_data: Dict) -> Dict:
        """Создает новую оценку риска"""
        assessments = self._read_csv(self.risk_assessments_file)
        
        # Генерируем ID
        assessment_id = self._get_next_id(self.risk_assessments_file)
        
        # Подготавливаем данные
        now = datetime.utcnow()
        assessment = {
            'id': assessment_id,
            'patient_id': assessment_data.get('patient_id'),
            'risk_level': assessment_data.get('risk_level', 'low'),
            'risk_score': assessment_data.get('risk_score', 0),
            'heat_wave_risk': assessment_data.get('heat_wave_risk', False),
            'risk_factors': assessment_data.get('risk_factors', {}),
            'weather_data': assessment_data.get('weather_data', {}),
            'assessment_date': now,
            'created_at': now
        }
        
        assessments.append(assessment)
        
        # Записываем обратно в файл
        headers = [
            'id', 'patient_id', 'risk_level', 'risk_score', 'heat_wave_risk',
            'risk_factors', 'weather_data', 'assessment_date', 'created_at'
        ]
        self._write_csv(self.risk_assessments_file, assessments, headers)
        
        return assessment
    
    def get_risk_assessments_by_patient(self, patient_id: int) -> List[Dict]:
        """Получает оценки риска для пациента"""
        assessments = self._read_csv(self.risk_assessments_file)
        return [a for a in assessments if a.get('patient_id') == patient_id]
    
    # Методы для работы с уведомлениями
    def create_notification(self, notification_data: Dict) -> Dict:
        """Создает новое уведомление"""
        notifications = self._read_csv(self.notifications_file)
        
        # Генерируем ID
        notification_id = self._get_next_id(self.notifications_file)
        
        # Подготавливаем данные
        now = datetime.utcnow()
        notification = {
            'id': notification_id,
            'patient_id': notification_data.get('patient_id'),
            'message': notification_data.get('message', ''),
            'notification_type': notification_data.get('notification_type', 'general'),
            'priority': notification_data.get('priority', 'medium'),
            'sent_at': notification_data.get('sent_at', now),
            'status': notification_data.get('status', 'pending'),
            'created_at': now
        }
        
        notifications.append(notification)
        
        # Записываем обратно в файл
        headers = [
            'id', 'patient_id', 'message', 'notification_type', 'priority',
            'sent_at', 'status', 'created_at'
        ]
        self._write_csv(self.notifications_file, notifications, headers)
        
        return notification
    
    def get_notifications_by_patient(self, patient_id: int) -> List[Dict]:
        """Получает уведомления для пациента"""
        notifications = self._read_csv(self.notifications_file)
        return [n for n in notifications if n.get('patient_id') == patient_id]

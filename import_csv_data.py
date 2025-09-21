#!/usr/bin/env python3
"""
Скрипт для импорта данных из существующего CSV файла
Import script for existing CSV data
"""

import os
import sys
import csv
from datetime import datetime

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.csv_service import CSVService

def import_patients_from_csv():
    """Импортирует пациентов из существующего CSV файла"""
    print("📥 Импорт пациентов из CSV файла...")
    
    csv_service = CSVService()
    source_file = "instance/synthetic_pregnant_patients_1000_with_meds_ndc.csv"
    
    if not os.path.exists(source_file):
        print(f"❌ Файл {source_file} не найден!")
        return False
    
    imported_count = 0
    
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Преобразуем данные из исходного формата
                patient_data = {
                    'name': row.get('Name', ''),
                    'age': int(row.get('Age', 0)) if row.get('Age') else 0,
                    'pregnancy_icd10': row.get('Pregnancy ICD-10', ''),
                    'pregnancy_description': row.get('Pregnancy Description', ''),
                    'comorbidity_icd10': row.get('Comorbidity ICD-10', ''),
                    'comorbidity_description': row.get('Comorbidity Description', ''),
                    'weeks_pregnant': int(row.get('Weeks Pregnant', 0)) if row.get('Weeks Pregnant') else 0,
                    'address': row.get('Address', ''),
                    'zip_code': row.get('ZIP Code', ''),
                    'medications': row.get('Medications', ''),
                    'medication_notes': row.get('Medication Notes', ''),
                    'ndc_codes': row.get('NDC Codes', ''),
                    'between_17_35': bool(int(row.get('Between 17-35', 0))) if row.get('Between 17-35') else False
                }
                
                # Создаем пациента
                csv_service.create_patient(patient_data)
                imported_count += 1
                
                if imported_count % 100 == 0:
                    print(f"📊 Импортировано {imported_count} пациентов...")
        
        print(f"✅ Успешно импортировано {imported_count} пациентов!")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при импорте: {e}")
        return False

def main():
    """Главная функция"""
    print("🏥 Импорт данных в систему уведомлений о здоровье")
    print("=" * 60)
    
    success = import_patients_from_csv()
    
    if success:
        print("\n🎉 Импорт завершен успешно!")
        print("Теперь можно тестировать API с реальными данными.")
    else:
        print("\n❌ Импорт завершился с ошибками.")

if __name__ == '__main__':
    main()

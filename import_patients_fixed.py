#!/usr/bin/env python3
"""
Исправленный скрипт для импорта данных из существующего CSV файла
Fixed import script for existing CSV data
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
    
    # Удаляем существующий файл если он есть
    patients_file = "instance/patients.csv"
    if os.path.exists(patients_file):
        os.remove(patients_file)
        print("🗑️ Удален существующий файл patients.csv")
    
    csv_service = CSVService()
    source_file = "instance/synthetic_pregnant_patients_1000_with_meds_ndc.csv"
    
    if not os.path.exists(source_file):
        print(f"❌ Файл {source_file} не найден!")
        return False
    
    imported_count = 0
    error_count = 0
    
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row_num, row in enumerate(reader, 1):
                try:
                    # Преобразуем данные из исходного формата
                    patient_data = {
                        'name': row.get('Name', '').strip(),
                        'age': int(row.get('Age', 0)) if row.get('Age') and row.get('Age').strip() else 0,
                        'pregnancy_icd10': row.get('Pregnancy ICD-10', '').strip(),
                        'pregnancy_description': row.get('Pregnancy Description', '').strip(),
                        'comorbidity_icd10': row.get('Comorbidity ICD-10', '').strip(),
                        'comorbidity_description': row.get('Comorbidity Description', '').strip(),
                        'weeks_pregnant': int(row.get('Weeks Pregnant', 0)) if row.get('Weeks Pregnant') and row.get('Weeks Pregnant').strip() else 0,
                        'address': row.get('Address', '').strip(),
                        'zip_code': row.get('ZIP Code', '').strip(),
                        'medications': row.get('Medications', '').strip(),
                        'medication_notes': row.get('Medication Notes', '').strip(),
                        'ndc_codes': row.get('NDC Codes', '').strip(),
                        'between_17_35': bool(int(row.get('Between 17-35', 0))) if row.get('Between 17-35') and row.get('Between 17-35').strip() else False
                    }
                    
                    # Проверяем обязательные поля
                    if not patient_data['name'] or not patient_data['zip_code']:
                        print(f"⚠️ Пропущена строка {row_num}: отсутствуют обязательные поля")
                        error_count += 1
                        continue
                    
                    # Создаем пациента
                    csv_service.create_patient(patient_data)
                    imported_count += 1
                    
                    if imported_count % 100 == 0:
                        print(f"📊 Импортировано {imported_count} пациентов...")
                        
                except (ValueError, TypeError) as e:
                    print(f"⚠️ Ошибка в строке {row_num}: {e}")
                    error_count += 1
                    continue
                except Exception as e:
                    print(f"❌ Неожиданная ошибка в строке {row_num}: {e}")
                    error_count += 1
                    continue
        
        print(f"✅ Успешно импортировано {imported_count} пациентов!")
        if error_count > 0:
            print(f"⚠️ Пропущено {error_count} строк из-за ошибок")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка при импорте: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Главная функция"""
    print("🏥 Импорт данных в систему уведомлений о здоровье")
    print("=" * 60)
    
    success = import_patients_from_csv()
    
    if success:
        print("\n🎉 Импорт завершен успешно!")
        print("Теперь можно тестировать API с реальными данными.")
        
        # Показываем статистику
        try:
            csv_service = CSVService()
            patients = csv_service.get_all_patients()
            print(f"📊 Всего пациентов в системе: {len(patients)}")
        except Exception as e:
            print(f"⚠️ Не удалось получить статистику: {e}")
    else:
        print("\n❌ Импорт завершился с ошибками.")

if __name__ == '__main__':
    main()

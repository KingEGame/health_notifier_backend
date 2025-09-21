#!/usr/bin/env python3
"""
Скрипт для тестирования создания пациента
"""

import os
import sys

# Добавляем путь к проекту
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем переменную окружения для SQLite
os.environ['USE_SQLITE'] = 'true'

from app import create_app, db
from app.models import Patient

def test_create_patient():
    """Тестирование создания пациента"""
    print("🧪 Тестирование создания пациента...")
    
    app = create_app()
    
    with app.app_context():
        try:
            # Создаем пациента
            patient_data = {
                'name': 'Test Patient',
                'age': 25,
                'zip_code': '101000',
                'phone_number': '+1234567890',
                'email': 'test@example.com'
            }
            
            patient = Patient(**patient_data)
            db.session.add(patient)
            db.session.commit()
            
            print(f"✅ Пациент создан успешно! ID: {patient.id}")
            print(f"📋 Данные пациента: {patient.name}, {patient.age} лет, {patient.zip_code}")
            
            # Проверяем, что пациент сохранен
            saved_patient = Patient.query.get(patient.id)
            if saved_patient:
                print(f"✅ Пациент найден в базе данных: {saved_patient.name}")
            else:
                print("❌ Пациент не найден в базе данных")
                
        except Exception as e:
            print(f"❌ Ошибка при создании пациента: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    test_create_patient()

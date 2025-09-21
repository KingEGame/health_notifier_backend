#!/usr/bin/env python3
"""
Простой тест API для системы уведомлений о здоровье
"""

import requests
import json

# URL API
BASE_URL = "http://localhost:5000/api"

def test_health():
    """Тест проверки здоровья системы"""
    print("🔍 Тестирование системы...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Статус: {response.status_code}")
        print(f"📊 Ответ: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return True
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

def test_create_patient():
    """Тест создания пациента"""
    print("\n👤 Создание тестового пациента...")
    
    patient_data = {
        "name": "Анна Петрова",
        "age": 28,
        "geo_location": "Moscow",
        "zip_code": "101000",
        "conditions_icd10": ["O24.4"],
        "trimester": 2,
        "phone_number": "+7-999-123-45-67",
        "email": "anna@example.com"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/patients", json=patient_data)
        print(f"✅ Статус: {response.status_code}")
        
        if response.status_code == 201:
            patient = response.json()['patient']
            print(f"👤 Пациент создан: {patient['name']} (ID: {patient['id']})")
            return patient['id']
        else:
            print(f"❌ Ошибка создания: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return None

def test_assess_risk(patient_id):
    """Тест оценки риска"""
    if not patient_id:
        print("❌ Нет ID пациента для оценки риска")
        return
    
    print(f"\n⚠️ Оценка риска для пациента {patient_id}...")
    
    try:
        response = requests.post(f"{BASE_URL}/assess-risk/{patient_id}")
        print(f"✅ Статус: {response.status_code}")
        
        if response.status_code == 200:
            risk_data = response.json()
            print(f"📊 Уровень риска: {risk_data['risk_level']}")
            print(f"🌡️ Температура: {risk_data['weather_data']['temperature']}°C")
            print(f"🔥 Тепловая волна: {'Да' if risk_data['heat_wave_risk'] else 'Нет'}")
        else:
            print(f"❌ Ошибка оценки: {response.json()}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def test_notifications(patient_id):
    """Тест уведомлений"""
    if not patient_id:
        print("❌ Нет ID пациента для уведомлений")
        return
    
    print(f"\n📬 Получение уведомлений для пациента {patient_id}...")
    
    try:
        response = requests.get(f"{BASE_URL}/notifications/{patient_id}")
        print(f"✅ Статус: {response.status_code}")
        
        if response.status_code == 200:
            notifications = response.json()['notifications']
            print(f"📬 Найдено уведомлений: {len(notifications)}")
            
            for i, notif in enumerate(notifications[:2], 1):  # Показываем первые 2
                print(f"  {i}. {notif['message'][:100]}...")
        else:
            print(f"❌ Ошибка получения уведомлений: {response.json()}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

def main():
    """Главная функция тестирования"""
    print("🏥 Тестирование системы уведомлений о здоровье")
    print("=" * 50)
    
    # Проверяем, что сервер запущен
    if not test_health():
        print("\n❌ Сервер не запущен!")
        print("Запустите сервер командой: python main.py")
        return
    
    # Создаем пациента
    patient_id = test_create_patient()
    
    if patient_id:
        # Оцениваем риск
        test_assess_risk(patient_id)
        
        # Получаем уведомления
        test_notifications(patient_id)
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    main()

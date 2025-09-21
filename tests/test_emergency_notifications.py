#!/usr/bin/env python3
"""
Тест для системы экстренных уведомлений с тремя уровнями риска
Test for emergency notification system with three risk levels
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_health_facilities():
    """Тест API медицинских учреждений"""
    print("\n--- Testing Health Facilities API ---")
    
    # Получение всех учреждений
    response = requests.get(f"{BASE_URL}/health-facilities")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ Health facilities API passed!")

def test_create_high_risk_patient():
    """Создание пациента с высоким риском"""
    print("\n--- Testing High Risk Patient Creation ---")
    
    patient_data = {
        "name": "Высокий Риск Пациентка",
        "age": 18,  # Молодой возраст = высокий риск
        "pregnancy_icd10": "O24.4",
        "pregnancy_description": "Gestational diabetes mellitus",
        "comorbidity_icd10": "I10",
        "comorbidity_description": "Essential hypertension",
        "weeks_pregnant": 35,  # 3 триместр = высокий риск
        "address": "123 High Risk Street, Risk City",
        "zip_code": "10001",
        "phone_number": "+7-999-111-11-11",
        "email": "highrisk@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/patients", json=patient_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201
    assert response.json()['success'] == True
    
    patient = response.json()['patient']
    assert patient['name'] == "Высокий Риск Пациентка"
    assert patient['age'] == 18
    assert patient['weeks_pregnant'] == 35
    
    print("✅ High risk patient creation passed!")
    return patient['id']

def test_create_medium_risk_patient():
    """Создание пациента со средним риском"""
    print("\n--- Testing Medium Risk Patient Creation ---")
    
    patient_data = {
        "name": "Средний Риск Пациентка",
        "age": 25,  # Средний возраст
        "pregnancy_icd10": "O26.9",
        "pregnancy_description": "Pregnancy-related condition, unspecified",
        "comorbidity_icd10": "E03.9",
        "comorbidity_description": "Hypothyroidism, unspecified",
        "weeks_pregnant": 20,  # 2 триместр
        "address": "456 Medium Risk Avenue, Medium City",
        "zip_code": "10002",
        "phone_number": "+7-999-222-22-22",
        "email": "mediumrisk@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/patients", json=patient_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201
    assert response.json()['success'] == True
    
    patient = response.json()['patient']
    assert patient['name'] == "Средний Риск Пациентка"
    
    print("✅ Medium risk patient creation passed!")
    return patient['id']

def test_create_low_risk_patient():
    """Создание пациента с низким риском"""
    print("\n--- Testing Low Risk Patient Creation ---")
    
    patient_data = {
        "name": "Низкий Риск Пациентка",
        "age": 28,  # Оптимальный возраст
        "pregnancy_icd10": "O26.9",
        "pregnancy_description": "Pregnancy-related condition, unspecified",
        "weeks_pregnant": 18,  # 2 триместр
        "address": "789 Low Risk Boulevard, Low City",
        "zip_code": "10003",
        "phone_number": "+7-999-333-33-33",
        "email": "lowrisk@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/patients", json=patient_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201
    assert response.json()['success'] == True
    
    patient = response.json()['patient']
    assert patient['name'] == "Низкий Риск Пациентка"
    
    print("✅ Low risk patient creation passed!")
    return patient['id']

def test_emergency_notification_high_risk(patient_id):
    """Тест экстренного уведомления для высокого риска"""
    print(f"\n--- Testing Emergency Notification for High Risk (ID: {patient_id}) ---")
    
    response = requests.post(f"{BASE_URL}/emergency-notifications/patient/{patient_id}/assess")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    assert response.json()['risk_level'] == 'high'
    assert response.json()['action_taken'] == 'doctor_called'
    assert 'hospital' in response.json()
    
    print("✅ High risk emergency notification passed!")

def test_emergency_notification_medium_risk(patient_id):
    """Тест уведомления для среднего риска"""
    print(f"\n--- Testing Emergency Notification for Medium Risk (ID: {patient_id}) ---")
    
    response = requests.post(f"{BASE_URL}/emergency-notifications/patient/{patient_id}/assess")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    assert response.json()['risk_level'] == 'medium'
    assert response.json()['action_taken'] == 'enhanced_notification_sent'
    
    print("✅ Medium risk emergency notification passed!")

def test_emergency_notification_low_risk(patient_id):
    """Тест уведомления для низкого риска"""
    print(f"\n--- Testing Emergency Notification for Low Risk (ID: {patient_id}) ---")
    
    response = requests.post(f"{BASE_URL}/emergency-notifications/patient/{patient_id}/assess")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    assert response.json()['risk_level'] == 'low'
    assert response.json()['action_taken'] == 'standard_notification_sent'
    
    print("✅ Low risk emergency notification passed!")

def test_get_emergency_notifications():
    """Тест получения экстренных уведомлений"""
    print("\n--- Testing Get Emergency Notifications ---")
    
    response = requests.get(f"{BASE_URL}/emergency-notifications")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    assert 'notifications' in response.json()
    
    print("✅ Get emergency notifications passed!")

def test_get_emergency_notification_stats():
    """Тест получения статистики уведомлений"""
    print("\n--- Testing Emergency Notification Stats ---")
    
    response = requests.get(f"{BASE_URL}/emergency-notifications/stats")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    assert 'stats' in response.json()
    
    print("✅ Emergency notification stats passed!")

def test_get_pending_notifications():
    """Тест получения ожидающих уведомлений"""
    print("\n--- Testing Get Pending Notifications ---")
    
    response = requests.get(f"{BASE_URL}/emergency-notifications/pending")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    assert 'notifications' in response.json()
    
    print("✅ Get pending notifications passed!")

def main():
    """Главная функция тестирования"""
    print("🚨 Тестирование системы экстренных уведомлений с тремя уровнями риска")
    print("=" * 70)
    
    try:
        # Тест API медицинских учреждений
        test_health_facilities()
        
        # Создание пациентов с разными уровнями риска
        high_risk_patient_id = test_create_high_risk_patient()
        medium_risk_patient_id = test_create_medium_risk_patient()
        low_risk_patient_id = test_create_low_risk_patient()
        
        # Тест экстренных уведомлений
        test_emergency_notification_high_risk(high_risk_patient_id)
        test_emergency_notification_medium_risk(medium_risk_patient_id)
        test_emergency_notification_low_risk(low_risk_patient_id)
        
        # Тест получения уведомлений
        test_get_emergency_notifications()
        test_get_emergency_notification_stats()
        test_get_pending_notifications()
        
        print("\n🎉 Все тесты системы экстренных уведомлений прошли успешно!")
        print("\n📋 Резюме:")
        print("   ✅ Высокий риск: Автоматический звонок врачу")
        print("   ✅ Средний риск: Расширенное уведомление")
        print("   ✅ Низкий риск: Стандартное уведомление")
        print("   ✅ Интеграция с медицинскими учреждениями")
        print("   ✅ Статистика и мониторинг")
        
    except Exception as e:
        print(f"\n❌ Тест не прошел: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Тест для новых полей пациентов
Test for new patient fields
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_create_patient_with_new_fields():
    """Тест создания пациента с новыми полями"""
    print("\n--- Testing Create Patient with New Fields ---")
    
    patient_data = {
        "name": "Тестовая Пациентка",
        "age": 28,
        "pregnancy_icd10": "O24.4",
        "pregnancy_description": "Gestational diabetes mellitus",
        "comorbidity_icd10": "I10",
        "comorbidity_description": "Essential hypertension",
        "weeks_pregnant": 20,
        "address": "123 Test Street, Test City",
        "zip_code": "12345",
        "phone_number": "+7-999-123-45-67",
        "email": "test@example.com"
    }
    
    response = requests.post(f"{BASE_URL}/patients", json=patient_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201
    assert response.json()['success'] == True
    
    patient = response.json()['patient']
    assert patient['name'] == "Тестовая Пациентка"
    assert patient['pregnancy_icd10'] == "O24.4"
    assert patient['comorbidity_icd10'] == "I10"
    assert patient['weeks_pregnant'] == 20
    assert patient['trimester'] == 2  # 20 недель = 2 триместр
    
    print("✅ Create patient with new fields passed!")
    return patient['id']

def test_get_patient_with_new_fields(patient_id):
    """Тест получения пациента с новыми полями"""
    print(f"\n--- Testing Get Patient with New Fields (ID: {patient_id}) ---")
    
    response = requests.get(f"{BASE_URL}/patients/{patient_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    
    patient = response.json()['patient']
    assert 'pregnancy_icd10' in patient
    assert 'comorbidity_icd10' in patient
    assert 'weeks_pregnant' in patient
    assert 'address' in patient
    assert 'trimester' in patient  # Должен быть рассчитан автоматически
    
    print("✅ Get patient with new fields passed!")

def test_update_patient_with_new_fields(patient_id):
    """Тест обновления пациента с новыми полями"""
    print(f"\n--- Testing Update Patient with New Fields (ID: {patient_id}) ---")
    
    update_data = {
        "weeks_pregnant": 25,
        "comorbidity_description": "Updated hypertension description"
    }
    
    response = requests.put(f"{BASE_URL}/patients/{patient_id}", json=update_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    
    patient = response.json()['patient']
    assert patient['weeks_pregnant'] == 25
    assert patient['trimester'] == 3  # 25 недель = 3 триместр
    
    print("✅ Update patient with new fields passed!")

def test_backward_compatibility():
    """Тест обратной совместимости со старыми полями"""
    print("\n--- Testing Backward Compatibility ---")
    
    patient_data = {
        "name": "Старая Пациентка",
        "age": 25,
        "zip_code": "54321",
        "conditions_icd10": ["O24.4", "I10"],
        "trimester": 2
    }
    
    response = requests.post(f"{BASE_URL}/patients", json=patient_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 201
    assert response.json()['success'] == True
    
    patient = response.json()['patient']
    assert patient['name'] == "Старая Пациентка"
    assert 'conditions_icd10' in patient
    assert 'trimester' in patient
    
    print("✅ Backward compatibility passed!")
    return patient['id']

def test_risk_assessment_with_new_fields(patient_id):
    """Тест оценки риска с новыми полями"""
    print(f"\n--- Testing Risk Assessment with New Fields (ID: {patient_id}) ---")
    
    response = requests.post(f"{BASE_URL}/assess-risk/{patient_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    assert 'risk_level' in response.json()
    
    print("✅ Risk assessment with new fields passed!")

def main():
    """Главная функция тестирования"""
    print("🧪 Тестирование новых полей пациентов")
    print("=" * 50)
    
    try:
        # Тест создания пациента с новыми полями
        patient_id = test_create_patient_with_new_fields()
        
        # Тест получения пациента
        test_get_patient_with_new_fields(patient_id)
        
        # Тест обновления пациента
        test_update_patient_with_new_fields(patient_id)
        
        # Тест обратной совместимости
        old_patient_id = test_backward_compatibility()
        
        # Тест оценки риска
        test_risk_assessment_with_new_fields(patient_id)
        test_risk_assessment_with_new_fields(old_patient_id)
        
        print("\n🎉 Все тесты прошли успешно!")
        
    except Exception as e:
        print(f"\n❌ Тест не прошел: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()

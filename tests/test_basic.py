import pytest
import json
from app import create_app
from app.extensions import db

@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['status'] == 'healthy'

def test_create_patient(client):
    patient_data = {
        "name": "Test Patient",
        "age": 25,
        "geo_location": "Test City",
        "zip_code": "12345",
        "conditions_icd10": ["O24.4"],
        "trimester": 2
    }
    
    response = client.post('/api/patients', 
                          json=patient_data,
                          content_type='application/json')
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['success'] == True
    assert data['patient']['name'] == "Test Patient"

def test_validation_error(client):
    invalid_data = {
        "name": "",
        "age": 40
    }
    
    response = client.post('/api/patients',
                          json=invalid_data,
                          content_type='application/json')
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

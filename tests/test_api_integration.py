import pytest
import json
from unittest.mock import patch, Mock
from app import create_app


class TestWeatherAPIIntegration:
    """Integration tests for weather API endpoints"""
    
    def setup_method(self):
        """Setup test environment"""
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.app.config['WEATHER_API_KEY'] = 'test_weather_key_12345'
        self.app.config['GEMINI_API_KEY'] = 'test_gemini_key_67890'
        self.client = self.app.test_client()
    
    @patch('app.services.weather_service.WeatherService.get_weather_data')
    def test_weather_endpoint_integration(self, mock_get_weather):
        """Test weather endpoint with real service integration"""
        # Mock weather data response
        mock_weather_data = {
            'temperature': 25.5,
            'feels_like': 27.2,
            'humidity': 75,
            'pressure': 1013,
            'description': 'partly cloudy',
            'is_heat_wave': False,
            'heat_index': 28.1,
            'uv_index': 6.5,
            'wind_speed': 3.2,
            'wind_deg': 180,
            'wind_gust': 5.1,
            'visibility': 10000,
            'cloudiness': 45,
            'dew_point': 18.5,
            'sunrise': 1758456226,
            'sunset': 1758500074,
            'timestamp': 1758460450,
            'timezone': 'America/New_York',
            'timezone_offset': -18000,
            'location': {
                'name': 'New York',
                'country': 'US',
                'coordinates': {
                    'lat': 40.7128,
                    'lon': -74.0060
                }
            },
            'minutely_precipitation': []
        }
        mock_get_weather.return_value = mock_weather_data
        
        # Test the endpoint
        response = self.client.get('/api/weather/10001')
        
        # Verify response
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['weather']['temperature'] == 25.5
        assert data['weather']['humidity'] == 75
        assert data['weather']['description'] == 'partly cloudy'
        assert data['weather']['is_heat_wave'] == False
        assert data['weather']['location']['name'] == 'New York'
        
        # Verify service was called
        mock_get_weather.assert_called_once_with('10001')
    
    @patch('app.services.weather_service.WeatherService.get_onecall_weather_data')
    def test_weather_onecall_endpoint_integration(self, mock_get_onecall):
        """Test OneCall weather endpoint with real service integration"""
        # Mock OneCall weather data response
        mock_weather_data = {
            'temperature': 30.2,
            'feels_like': 33.8,
            'humidity': 85,
            'pressure': 1008,
            'description': 'hot and humid',
            'is_heat_wave': True,
            'heat_index': 38.5,
            'uv_index': 9.2,
            'wind_speed': 1.5,
            'wind_deg': 225,
            'wind_gust': 2.8,
            'visibility': 8000,
            'cloudiness': 20,
            'dew_point': 26.1,
            'sunrise': 1758456226,
            'sunset': 1758500074,
            'timestamp': 1758460450,
            'timezone': 'America/Chicago',
            'timezone_offset': -18000,
            'location': {
                'name': 'Unknown',
                'country': 'Unknown',
                'coordinates': {
                    'lat': 33.44,
                    'lon': -94.04
                }
            },
            'minutely_precipitation': [
                {'datetime': 1758460500, 'precipitation': 0},
                {'datetime': 1758460560, 'precipitation': 0}
            ]
        }
        mock_get_onecall.return_value = mock_weather_data
        
        # Test the endpoint
        response = self.client.get('/api/weather-onecall/75201')
        
        # Verify response
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['weather']['temperature'] == 30.2
        assert data['weather']['is_heat_wave'] == True
        assert data['weather']['heat_index'] == 38.5
        assert data['weather']['uv_index'] == 9.2
        assert data['weather']['timezone'] == 'America/Chicago'
        assert len(data['weather']['minutely_precipitation']) == 2
        
        # Verify service was called
        mock_get_onecall.assert_called_once_with('75201')
    
    @patch('app.services.weather_service.WeatherService.get_weather_forecast')
    def test_weather_forecast_endpoint_integration(self, mock_get_forecast):
        """Test weather forecast endpoint with real service integration"""
        # Mock forecast data response
        mock_forecast_data = {
            'forecasts': [
                {
                    'datetime': 1758460800,
                    'temperature': 28.5,
                    'feels_like': 31.2,
                    'humidity': 80,
                    'pressure': 1010,
                    'description': 'hot and sunny',
                    'is_heat_wave': True,
                    'heat_index': 35.8,
                    'precipitation_probability': 5.0,
                    'wind_speed': 2.1
                },
                {
                    'datetime': 1758464400,
                    'temperature': 26.8,
                    'feels_like': 29.5,
                    'humidity': 75,
                    'pressure': 1012,
                    'description': 'warm and partly cloudy',
                    'is_heat_wave': False,
                    'heat_index': 32.1,
                    'precipitation_probability': 15.0,
                    'wind_speed': 3.5
                }
            ],
            'location': {
                'name': 'Miami',
                'country': 'US'
            }
        }
        mock_get_forecast.return_value = mock_forecast_data
        
        # Test the endpoint
        response = self.client.get('/api/weather-forecast/33101?days=2')
        
        # Verify response
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert len(data['forecast']['forecasts']) == 2
        assert data['forecast']['forecasts'][0]['temperature'] == 28.5
        assert data['forecast']['forecasts'][0]['is_heat_wave'] == True
        assert data['forecast']['forecasts'][1]['temperature'] == 26.8
        assert data['forecast']['forecasts'][1]['is_heat_wave'] == False
        assert data['forecast']['location']['name'] == 'Miami'
        
        # Verify service was called
        mock_get_forecast.assert_called_once_with('33101', 2)
    
    @patch('app.services.weather_service.WeatherService.get_weather_alerts')
    def test_weather_alerts_endpoint_integration(self, mock_get_alerts):
        """Test weather alerts endpoint with real service integration"""
        # Mock alerts data response
        mock_alerts_data = {
            'alerts': [
                {
                    'sender_name': 'National Weather Service',
                    'event': 'Excessive Heat Warning',
                    'start': 1758460450,
                    'end': 1758500000,
                    'description': 'Dangerously hot conditions with temperatures up to 105°F expected.',
                    'tags': ['Extreme temperature value', 'Heat']
                },
                {
                    'sender_name': 'National Weather Service',
                    'event': 'Heat Advisory',
                    'start': 1758500000,
                    'end': 1758540000,
                    'description': 'Heat index values up to 108°F expected.',
                    'tags': ['Heat']
                }
            ],
            'has_alerts': True,
            'alert_count': 2
        }
        mock_get_alerts.return_value = mock_alerts_data
        
        # Test the endpoint
        response = self.client.get('/api/weather-alerts/85001')
        
        # Verify response
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['alerts']['has_alerts'] == True
        assert data['alerts']['alert_count'] == 2
        assert len(data['alerts']['alerts']) == 2
        assert data['alerts']['alerts'][0]['event'] == 'Excessive Heat Warning'
        assert data['alerts']['alerts'][1]['event'] == 'Heat Advisory'
        
        # Verify service was called
        mock_get_alerts.assert_called_once_with('85001')
    
    @patch('app.services.weather_service.WeatherService.get_weather_data')
    @patch('app.services.ai_service.AIService.get_weather_risk_analysis')
    @patch('app.models.patient.Patient.query')
    def test_weather_ai_analysis_endpoint_integration(self, mock_patient_query, mock_ai_analysis, mock_get_weather):
        """Test weather AI analysis endpoint with real service integration"""
        # Mock weather data
        mock_weather_data = {
            'temperature': 38.5,
            'feels_like': 42.1,
            'humidity': 90,
            'pressure': 1005,
            'description': 'extremely hot and humid',
            'is_heat_wave': True,
            'heat_index': 48.3,
            'uv_index': 10.0,
            'wind_speed': 0.8,
            'wind_deg': 180,
            'wind_gust': 1.2,
            'visibility': 5000,
            'cloudiness': 10,
            'dew_point': 35.2,
            'sunrise': 1758456226,
            'sunset': 1758500074,
            'timestamp': 1758460450,
            'timezone': 'America/Phoenix',
            'timezone_offset': -18000,
            'location': {
                'name': 'Unknown',
                'country': 'Unknown',
                'coordinates': {
                    'lat': 33.44,
                    'lon': -112.07
                }
            },
            'minutely_precipitation': []
        }
        mock_get_weather.return_value = mock_weather_data
        
        # Mock patient count
        mock_patient_query.filter_by.return_value.count.return_value = 15
        
        # Mock AI analysis
        mock_ai_analysis.return_value = {
            'risk_level': 'Critical',
            'health_concerns': [
                'Extreme heat poses severe risk to pregnant women',
                'High humidity increases heat stress and dehydration risk',
                'UV index at maximum level - severe sunburn risk'
            ],
            'immediate_recommendations': [
                'Stay indoors with air conditioning at all times',
                'Drink water every 15 minutes',
                'Monitor for signs of heat exhaustion',
                'Avoid any outdoor activities'
            ],
            'preventive_measures': [
                'Use fans and air conditioning continuously',
                'Wear light, loose, light-colored clothing',
                'Take cool showers or baths frequently',
                'Keep windows and doors closed during peak heat'
            ],
            'emergency_actions': [
                'Call 911 immediately if experiencing heat stroke symptoms',
                'Seek medical attention for any heat-related symptoms',
                'Move to air-conditioned environment immediately if outdoors'
            ]
        }
        
        # Test the endpoint
        response = self.client.get('/api/weather-ai-analysis/85001')
        
        # Verify response
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['weather_data']['temperature'] == 38.5
        assert data['weather_data']['is_heat_wave'] == True
        assert data['patient_count'] == 15
        assert data['ai_analysis']['risk_level'] == 'Critical'
        assert len(data['ai_analysis']['health_concerns']) == 3
        assert len(data['ai_analysis']['immediate_recommendations']) == 4
        assert 'timestamp' in data
        
        # Verify services were called
        mock_get_weather.assert_called_once_with('85001')
        mock_patient_query.filter_by.assert_called_once_with(zip_code='85001')
        mock_ai_analysis.assert_called_once_with(mock_weather_data, 15)
    
    def test_weather_endpoint_error_handling(self):
        """Test weather endpoint error handling"""
        with patch('app.services.weather_service.WeatherService.get_weather_data') as mock_get_weather:
            mock_get_weather.side_effect = Exception("Weather service unavailable")
            
            response = self.client.get('/api/weather/10001')
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] == False
            assert 'Failed to get weather data' in data['error']
    
    def test_weather_onecall_endpoint_error_handling(self):
        """Test OneCall weather endpoint error handling"""
        with patch('app.services.weather_service.WeatherService.get_onecall_weather_data') as mock_get_onecall:
            mock_get_onecall.side_effect = Exception("OneCall service unavailable")
            
            response = self.client.get('/api/weather-onecall/10001')
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] == False
            assert 'Failed to get OneCall weather data' in data['error']
    
    def test_weather_forecast_endpoint_error_handling(self):
        """Test weather forecast endpoint error handling"""
        with patch('app.services.weather_service.WeatherService.get_weather_forecast') as mock_get_forecast:
            mock_get_forecast.side_effect = Exception("Forecast service unavailable")
            
            response = self.client.get('/api/weather-forecast/10001')
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] == False
            assert 'Failed to get weather forecast' in data['error']
    
    def test_weather_alerts_endpoint_error_handling(self):
        """Test weather alerts endpoint error handling"""
        with patch('app.services.weather_service.WeatherService.get_weather_alerts') as mock_get_alerts:
            mock_get_alerts.side_effect = Exception("Alerts service unavailable")
            
            response = self.client.get('/api/weather-alerts/10001')
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] == False
            assert 'Failed to get weather alerts' in data['error']
    
    def test_weather_ai_analysis_endpoint_error_handling(self):
        """Test weather AI analysis endpoint error handling"""
        with patch('app.services.weather_service.WeatherService.get_weather_data') as mock_get_weather:
            mock_get_weather.side_effect = Exception("Weather service unavailable")
            
            response = self.client.get('/api/weather-ai-analysis/10001')
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] == False
            assert 'Failed to get weather AI analysis' in data['error']


class TestEnvironmentMetricsAPIIntegration:
    """Integration tests for environment metrics API endpoints"""
    
    def setup_method(self):
        """Setup test environment"""
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.app.config['WEATHER_API_KEY'] = 'test_weather_key_12345'
        self.app.config['GEMINI_API_KEY'] = 'test_gemini_key_67890'
        self.client = self.app.test_client()
    
    @patch('app.models.patient.Patient.query')
    @patch('app.services.weather_service.WeatherService.get_weather_data')
    @patch('app.services.risk_service.RiskAssessmentService.assess_risk')
    def test_environment_metrics_endpoint_integration(self, mock_assess_risk, mock_get_weather, mock_patient_query):
        """Test environment metrics endpoint with real service integration"""
        # Mock patient data
        mock_patients = [
            Mock(
                id=1,
                name="Patient 1",
                age=25,
                zip_code="10001",
                weeks_pregnant=20,
                pregnancy_icd10=None,
                comorbidity_icd10=None,
                get_conditions=Mock(return_value=[]),
                get_medications_list=Mock(return_value=[])
            ),
            Mock(
                id=2,
                name="Patient 2",
                age=30,
                zip_code="10001",
                weeks_pregnant=32,
                pregnancy_icd10="O24.4",
                comorbidity_icd10="I10",
                get_conditions=Mock(return_value=["O24.4", "I10"]),
                get_medications_list=Mock(return_value=["Insulin", "Labetalol"])
            ),
            Mock(
                id=3,
                name="Patient 3",
                age=35,
                zip_code="90210",
                weeks_pregnant=28,
                pregnancy_icd10=None,
                comorbidity_icd10=None,
                get_conditions=Mock(return_value=[]),
                get_medications_list=Mock(return_value=[])
            )
        ]
        mock_patient_query.all.return_value = mock_patients
        
        # Mock weather data for different locations
        def mock_weather_side_effect(zip_code):
            if zip_code == "10001":
                return {
                    'temperature': 38.5,
                    'feels_like': 42.1,
                    'humidity': 90,
                    'pressure': 1005,
                    'description': 'extremely hot and humid',
                    'is_heat_wave': True,
                    'heat_index': 48.3,
                    'uv_index': 10.0,
                    'wind_speed': 0.8,
                    'wind_deg': 180,
                    'wind_gust': 1.2,
                    'visibility': 5000,
                    'cloudiness': 10,
                    'dew_point': 35.2,
                    'sunrise': 1758456226,
                    'sunset': 1758500074,
                    'timestamp': 1758460450,
                    'timezone': 'America/New_York',
                    'timezone_offset': -18000,
                    'location': {
                        'name': 'Unknown',
                        'country': 'Unknown',
                        'coordinates': {'lat': 40.7128, 'lon': -74.0060}
                    },
                    'minutely_precipitation': []
                }
            else:  # 90210
                return {
                    'temperature': 22.0,
                    'feels_like': 23.5,
                    'humidity': 60,
                    'pressure': 1013,
                    'description': 'pleasant weather',
                    'is_heat_wave': False,
                    'heat_index': 24.2,
                    'uv_index': 5.0,
                    'wind_speed': 3.2,
                    'wind_deg': 270,
                    'wind_gust': 4.5,
                    'visibility': 15000,
                    'cloudiness': 30,
                    'dew_point': 15.0,
                    'sunrise': 1758456226,
                    'sunset': 1758500074,
                    'timestamp': 1758460450,
                    'timezone': 'America/Los_Angeles',
                    'timezone_offset': -18000,
                    'location': {
                        'name': 'Unknown',
                        'country': 'Unknown',
                        'coordinates': {'lat': 34.0522, 'lon': -118.2437}
                    },
                    'minutely_precipitation': []
                }
        
        mock_get_weather.side_effect = mock_weather_side_effect
        
        # Mock risk assessment for different patients
        def mock_assess_risk_side_effect(patient):
            if patient.id == 1:
                return {
                    'risk_level': 'medium',
                    'risk_score': 4,
                    'heat_wave_risk': True,
                    'factors': {
                        'age_risk': 'medium',
                        'trimester_risk': 'medium',
                        'location_risk': 'high',
                        'conditions_risk': 'low',
                        'medications_risk': 'low'
                    },
                    'weather_data': mock_weather_side_effect(patient.zip_code)
                }
            elif patient.id == 2:
                return {
                    'risk_level': 'high',
                    'risk_score': 8,
                    'heat_wave_risk': True,
                    'factors': {
                        'age_risk': 'medium',
                        'trimester_risk': 'high',
                        'location_risk': 'high',
                        'conditions_risk': 'high',
                        'medications_risk': 'high'
                    },
                    'weather_data': mock_weather_side_effect(patient.zip_code)
                }
            else:  # patient.id == 3
                return {
                    'risk_level': 'low',
                    'risk_score': 2,
                    'heat_wave_risk': False,
                    'factors': {
                        'age_risk': 'high',
                        'trimester_risk': 'medium',
                        'location_risk': 'low',
                        'conditions_risk': 'low',
                        'medications_risk': 'low'
                    },
                    'weather_data': mock_weather_side_effect(patient.zip_code)
                }
        
        mock_assess_risk.side_effect = mock_assess_risk_side_effect
        
        # Test the endpoint
        response = self.client.get('/api/environment-metrics')
        
        # Verify response
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        
        metrics = data['environment_metrics']
        assert metrics['total_patients'] == 3
        assert metrics['patients_at_risk'] == 2  # medium + high risk
        assert metrics['extreme_heat_conditions'] == 2  # 2 patients in 10001 with heat wave
        assert metrics['risk_distribution']['low'] == 1
        assert metrics['risk_distribution']['medium'] == 1
        assert metrics['risk_distribution']['high'] == 1
        
        # Verify weather conditions by location
        assert '10001' in metrics['weather_conditions']
        assert '90210' in metrics['weather_conditions']
        assert metrics['weather_conditions']['10001']['is_heat_wave'] == True
        assert metrics['weather_conditions']['90210']['is_heat_wave'] == False
        assert metrics['weather_conditions']['10001']['patient_count'] == 2
        assert metrics['weather_conditions']['90210']['patient_count'] == 1
        
        # Verify at-risk patients
        assert len(metrics['at_risk_patients']) == 2
        at_risk_zip_codes = [p['zip_code'] for p in metrics['at_risk_patients']]
        assert '10001' in at_risk_zip_codes
        assert '90210' not in at_risk_zip_codes  # Only low risk patient in 90210
    
    @patch('app.models.patient.Patient.query')
    def test_environment_metrics_no_patients(self, mock_patient_query):
        """Test environment metrics endpoint with no patients"""
        mock_patient_query.all.return_value = []
        
        response = self.client.get('/api/environment-metrics')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['message'] == 'No patients found'
        
        metrics = data['environment_metrics']
        assert metrics['total_patients'] == 0
        assert metrics['patients_at_risk'] == 0
        assert metrics['extreme_heat_conditions'] == 0
        assert metrics['risk_distribution'] == {}
        assert metrics['weather_conditions'] == {}
    
    def test_environment_metrics_error_handling(self):
        """Test environment metrics endpoint error handling"""
        with patch('app.models.patient.Patient.query') as mock_patient_query:
            mock_patient_query.all.side_effect = Exception("Database error")
            
            response = self.client.get('/api/environment-metrics')
            
            assert response.status_code == 500
            data = response.get_json()
            assert data['success'] == False
            assert 'Failed to get environment metrics' in data['error']

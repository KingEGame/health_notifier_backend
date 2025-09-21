import pytest
import os
import json
from unittest.mock import patch, Mock
from app.services.weather_service import WeatherService
from app.utils.exceptions import ExternalAPIException


class TestWeatherService:
    """Test cases for WeatherService API integration"""
    
    def setup_method(self):
        """Setup test environment"""
        self.test_zip_code = "101000"
        self.mock_api_key = "test_api_key_12345"
        
        # Mock environment variables
        os.environ['WEATHER_API_KEY'] = self.mock_api_key
    
    def teardown_method(self):
        """Cleanup after tests"""
        if 'WEATHER_API_KEY' in os.environ:
            del os.environ['WEATHER_API_KEY']
    
    def test_api_key_loading(self):
        """Test that API key is loaded from environment"""
        from app.config import Config
        assert Config.WEATHER_API_KEY == self.mock_api_key
    
    @patch('requests.get')
    def test_onecall_api_success(self, mock_get):
        """Test successful OneCall API response"""
        # Mock OneCall API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lat": 33.44,
            "lon": -94.04,
            "timezone": "America/Chicago",
            "timezone_offset": -18000,
            "current": {
                "dt": 1758460450,
                "sunrise": 1758456226,
                "sunset": 1758500074,
                "temp": 295.19,  # 22.04°C
                "feels_like": 295.77,  # 22.62°C
                "pressure": 1015,
                "humidity": 89,
                "dew_point": 293.29,  # 20.14°C
                "uvi": 0.21,
                "clouds": 0,
                "visibility": 10000,
                "wind_speed": 2.68,
                "wind_deg": 159,
                "wind_gust": 5.36,
                "weather": [
                    {
                        "id": 800,
                        "main": "Clear",
                        "description": "clear sky",
                        "icon": "01d"
                    }
                ]
            },
            "minutely": [
                {
                    "dt": 1758460500,
                    "precipitation": 0
                }
            ]
        }
        mock_get.return_value = mock_response
        
        # Test the API call
        result = WeatherService.get_onecall_weather_data(self.test_zip_code)
        
        # Verify API call was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "http://api.openweathermap.org/data/3.0/onecall"
        assert call_args[1]['params']['zip'] == self.test_zip_code
        assert call_args[1]['params']['appid'] == self.mock_api_key
        assert call_args[1]['params']['units'] == 'metric'
        
        # Verify response processing
        assert result['temperature'] == 22.0  # Converted from Kelvin
        assert result['feels_like'] == 22.6
        assert result['humidity'] == 89
        assert result['pressure'] == 1015
        assert result['description'] == "clear sky"
        assert result['uv_index'] == 0.21
        assert result['wind_speed'] == 2.68
        assert result['wind_deg'] == 159
        assert result['wind_gust'] == 5.36
        assert result['timezone'] == "America/Chicago"
        assert result['timezone_offset'] == -18000
        assert result['location']['coordinates']['lat'] == 33.44
        assert result['location']['coordinates']['lon'] == -94.04
        assert len(result['minutely_precipitation']) == 1
    
    @patch('requests.get')
    def test_current_weather_api_success(self, mock_get):
        """Test successful Current Weather API response"""
        # Mock Current Weather API response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "coord": {"lon": -94.04, "lat": 33.44},
            "weather": [
                {
                    "id": 800,
                    "main": "Clear",
                    "description": "clear sky",
                    "icon": "01d"
                }
            ],
            "main": {
                "temp": 22.0,
                "feels_like": 22.6,
                "pressure": 1015,
                "humidity": 89,
                "dew_point": 20.14
            },
            "visibility": 10000,
            "wind": {
                "speed": 2.68,
                "deg": 159,
                "gust": 5.36
            },
            "clouds": {"all": 0},
            "dt": 1758460450,
            "sys": {
                "sunrise": 1758456226,
                "sunset": 1758500074,
                "country": "US"
            },
            "name": "Test City"
        }
        mock_get.return_value = mock_response
        
        # Test the API call
        result = WeatherService.get_current_weather_data(self.test_zip_code)
        
        # Verify API call was made correctly
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[0][0] == "http://api.openweathermap.org/data/2.5/weather"
        assert call_args[1]['params']['zip'] == self.test_zip_code
        assert call_args[1]['params']['appid'] == self.mock_api_key
        assert call_args[1]['params']['units'] == 'metric'
        
        # Verify response processing
        assert result['temperature'] == 22.0
        assert result['feels_like'] == 22.6
        assert result['humidity'] == 89
        assert result['pressure'] == 1015
        assert result['description'] == "clear sky"
        assert result['wind_speed'] == 2.68
        assert result['wind_deg'] == 159
        assert result['wind_gust'] == 5.36
        assert result['location']['name'] == "Test City"
        assert result['location']['country'] == "US"
    
    @patch('requests.get')
    def test_api_fallback_mechanism(self, mock_get):
        """Test fallback from OneCall to Current Weather API"""
        # First call fails (OneCall API)
        # Second call succeeds (Current Weather API)
        mock_responses = [
            Mock(status_code=401),  # OneCall API fails
            Mock(status_code=200, json=lambda: {
                "coord": {"lon": -94.04, "lat": 33.44},
                "weather": [{"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}],
                "main": {"temp": 22.0, "feels_like": 22.6, "pressure": 1015, "humidity": 89, "dew_point": 20.14},
                "visibility": 10000,
                "wind": {"speed": 2.68, "deg": 159, "gust": 5.36},
                "clouds": {"all": 0},
                "dt": 1758460450,
                "sys": {"sunrise": 1758456226, "sunset": 1758500074, "country": "US"},
                "name": "Test City"
            })
        ]
        mock_get.side_effect = mock_responses
        
        # Test the fallback mechanism
        result = WeatherService.get_weather_data(self.test_zip_code)
        
        # Verify both APIs were called
        assert mock_get.call_count == 2
        
        # Verify the result comes from Current Weather API
        assert result['temperature'] == 22.0
        assert result['location']['name'] == "Test City"
    
    @patch('requests.get')
    def test_api_key_missing(self, mock_get):
        """Test behavior when API key is missing"""
        # Remove API key from environment
        if 'WEATHER_API_KEY' in os.environ:
            del os.environ['WEATHER_API_KEY']
        
        # Mock the config to return None for API key
        with patch('app.config.Config.WEATHER_API_KEY', None):
            with pytest.raises(ExternalAPIException):
                WeatherService.get_onecall_weather_data(self.test_zip_code)
    
    @patch('requests.get')
    def test_api_http_error(self, mock_get):
        """Test handling of HTTP errors"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"message": "Invalid API key"}
        mock_get.return_value = mock_response
        
        with pytest.raises(ExternalAPIException) as exc_info:
            WeatherService.get_onecall_weather_data(self.test_zip_code)
        
        assert "OneCall API returned status 401" in str(exc_info.value)
    
    @patch('requests.get')
    def test_api_network_error(self, mock_get):
        """Test handling of network errors"""
        mock_get.side_effect = Exception("Network error")
        
        with pytest.raises(ExternalAPIException) as exc_info:
            WeatherService.get_onecall_weather_data(self.test_zip_code)
        
        assert "OneCall API error: Network error" in str(exc_info.value)
    
    @patch('requests.get')
    def test_heat_wave_detection(self, mock_get):
        """Test heat wave detection logic"""
        # Test extreme heat conditions
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lat": 33.44,
            "lon": -94.04,
            "timezone": "America/Chicago",
            "timezone_offset": -18000,
            "current": {
                "dt": 1758460450,
                "temp": 310.15,  # 37°C - should trigger heat wave
                "feels_like": 315.15,  # 42°C
                "pressure": 1015,
                "humidity": 85,
                "dew_point": 300.15,
                "uvi": 8.5,
                "clouds": 10,
                "visibility": 10000,
                "wind_speed": 1.5,
                "wind_deg": 180,
                "wind_gust": 3.0,
                "weather": [
                    {
                        "id": 800,
                        "main": "Clear",
                        "description": "clear sky",
                        "icon": "01d"
                    }
                ]
            },
            "minutely": []
        }
        mock_get.return_value = mock_response
        
        result = WeatherService.get_onecall_weather_data(self.test_zip_code)
        
        # Verify heat wave detection
        assert result['temperature'] == 37.0
        assert result['is_heat_wave'] == True
        assert result['heat_index'] > 40  # Should be high due to temperature and humidity
    
    @patch('requests.get')
    def test_forecast_api(self, mock_get):
        """Test weather forecast API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "city": {
                "name": "Test City",
                "country": "US"
            },
            "list": [
                {
                    "dt": 1758460800,
                    "main": {
                        "temp": 25.0,
                        "feels_like": 26.0,
                        "pressure": 1013,
                        "humidity": 70
                    },
                    "weather": [
                        {
                            "id": 800,
                            "main": "Clear",
                            "description": "clear sky",
                            "icon": "01d"
                        }
                    ],
                    "wind": {
                        "speed": 3.0
                    },
                    "pop": 0.1
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = WeatherService.get_weather_forecast(self.test_zip_code, days=1)
        
        # Verify API call
        call_args = mock_get.call_args
        assert call_args[0][0] == "http://api.openweathermap.org/data/2.5/forecast"
        assert call_args[1]['params']['zip'] == self.test_zip_code
        assert call_args[1]['params']['appid'] == self.mock_api_key
        assert call_args[1]['params']['units'] == 'metric'
        assert call_args[1]['params']['cnt'] == 8  # 1 day * 8 forecasts
        
        # Verify response processing
        assert len(result['forecasts']) == 1
        assert result['forecasts'][0]['temperature'] == 25.0
        assert result['forecasts'][0]['precipitation_probability'] == 10.0
        assert result['location']['name'] == "Test City"
    
    @patch('requests.get')
    def test_weather_alerts_api(self, mock_get):
        """Test weather alerts API"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "lat": 33.44,
            "lon": -94.04,
            "timezone": "America/Chicago",
            "timezone_offset": -18000,
            "current": {
                "dt": 1758460450,
                "temp": 295.19,
                "feels_like": 295.77,
                "pressure": 1015,
                "humidity": 89,
                "dew_point": 293.29,
                "uvi": 0.21,
                "clouds": 0,
                "visibility": 10000,
                "wind_speed": 2.68,
                "wind_deg": 159,
                "wind_gust": 5.36,
                "weather": [
                    {
                        "id": 800,
                        "main": "Clear",
                        "description": "clear sky",
                        "icon": "01d"
                    }
                ]
            },
            "alerts": [
                {
                    "sender_name": "NWS",
                    "event": "Heat Advisory",
                    "start": 1758460450,
                    "end": 1758500000,
                    "description": "High temperatures expected",
                    "tags": ["Extreme temperature value"]
                }
            ]
        }
        mock_get.return_value = mock_response
        
        result = WeatherService.get_weather_alerts(self.test_zip_code)
        
        # Verify API call
        call_args = mock_get.call_args
        assert call_args[0][0] == "http://api.openweathermap.org/data/3.0/onecall"
        assert call_args[1]['params']['zip'] == self.test_zip_code
        assert call_args[1]['params']['appid'] == self.mock_api_key
        assert call_args[1]['params']['units'] == 'metric'
        assert call_args[1]['params']['exclude'] == 'minutely,hourly,daily'
        
        # Verify response processing
        assert result['has_alerts'] == True
        assert result['alert_count'] == 1
        assert len(result['alerts']) == 1
        assert result['alerts'][0]['event'] == "Heat Advisory"
    
    def test_default_weather_data(self):
        """Test default weather data when API fails"""
        result = WeatherService._get_default_weather_data()
        
        assert result['temperature'] == 25
        assert result['feels_like'] == 25
        assert result['humidity'] == 50
        assert result['pressure'] == 1013
        assert result['description'] == 'Unknown'
        assert result['is_heat_wave'] == False
        assert result['heat_index'] == 25
        assert result['uv_index'] == 0
        assert result['wind_speed'] == 0
        assert result['wind_deg'] == 0
        assert result['wind_gust'] == 0
        assert result['visibility'] == 10000
        assert result['cloudiness'] == 0
        assert result['dew_point'] == 0
        assert result['sunrise'] == 0
        assert result['sunset'] == 0
        assert result['timestamp'] == 0
        assert result['timezone'] == 'Unknown'
        assert result['timezone_offset'] == 0
        assert result['location']['name'] == 'Unknown'
        assert result['location']['country'] == 'Unknown'
        assert result['location']['coordinates']['lat'] == 0
        assert result['location']['coordinates']['lon'] == 0
        assert result['minutely_precipitation'] == []
    
    def test_heat_index_calculation(self):
        """Test heat index calculation"""
        # Test normal conditions
        heat_index = WeatherService._calculate_heat_index(25, 50)
        assert isinstance(heat_index, float)
        assert heat_index > 20  # Should be reasonable
        
        # Test extreme conditions
        heat_index_extreme = WeatherService._calculate_heat_index(40, 90)
        assert heat_index_extreme > heat_index  # Should be higher for extreme conditions
    
    def test_heat_wave_detection_logic(self):
        """Test heat wave detection logic"""
        # Test normal temperature
        assert WeatherService._is_heat_wave(25, 50) == False
        
        # Test high temperature
        assert WeatherService._is_heat_wave(36, 50) == True
        
        # Test high heat index
        assert WeatherService._is_heat_wave(30, 90) == True  # High humidity should trigger heat wave


class TestWeatherAPIEndpoints:
    """Test cases for weather API endpoints"""
    
    def setup_method(self):
        """Setup test environment"""
        self.app = None
        self.client = None
        
    def create_app(self):
        """Create test Flask app"""
        from app import create_app
        self.app = create_app('testing')
        self.app.config['TESTING'] = True
        self.app.config['WEATHER_API_KEY'] = 'test_api_key_12345'
        self.app.config['GEMINI_API_KEY'] = 'test_gemini_key_12345'
        return self.app
    
    @patch('app.services.weather_service.WeatherService.get_weather_data')
    def test_weather_endpoint(self, mock_get_weather):
        """Test /api/weather/{zip_code} endpoint"""
        app = self.create_app()
        client = app.test_client()
        
        # Mock weather data
        mock_weather_data = {
            'temperature': 22.0,
            'feels_like': 23.5,
            'humidity': 89,
            'pressure': 1015,
            'description': 'clear sky',
            'is_heat_wave': False,
            'heat_index': 24.2
        }
        mock_get_weather.return_value = mock_weather_data
        
        # Test the endpoint
        response = client.get('/api/weather/101000')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['weather']['temperature'] == 22.0
        assert data['weather']['description'] == 'clear sky'
    
    @patch('app.services.weather_service.WeatherService.get_onecall_weather_data')
    def test_weather_onecall_endpoint(self, mock_get_onecall):
        """Test /api/weather-onecall/{zip_code} endpoint"""
        app = self.create_app()
        client = app.test_client()
        
        # Mock OneCall weather data
        mock_weather_data = {
            'temperature': 22.0,
            'feels_like': 23.5,
            'humidity': 89,
            'pressure': 1015,
            'description': 'clear sky',
            'is_heat_wave': False,
            'heat_index': 24.2,
            'uv_index': 0.21,
            'wind_speed': 2.68,
            'timezone': 'America/Chicago',
            'minutely_precipitation': []
        }
        mock_get_onecall.return_value = mock_weather_data
        
        # Test the endpoint
        response = client.get('/api/weather-onecall/101000')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['weather']['temperature'] == 22.0
        assert data['weather']['timezone'] == 'America/Chicago'
    
    @patch('app.services.weather_service.WeatherService.get_weather_forecast')
    def test_weather_forecast_endpoint(self, mock_get_forecast):
        """Test /api/weather-forecast/{zip_code} endpoint"""
        app = self.create_app()
        client = app.test_client()
        
        # Mock forecast data
        mock_forecast_data = {
            'forecasts': [
                {
                    'datetime': 1758460800,
                    'temperature': 25.0,
                    'feels_like': 26.0,
                    'humidity': 70,
                    'description': 'clear sky',
                    'precipitation_probability': 10.0
                }
            ],
            'location': {
                'name': 'Test City',
                'country': 'US'
            }
        }
        mock_get_forecast.return_value = mock_forecast_data
        
        # Test the endpoint
        response = client.get('/api/weather-forecast/101000?days=1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert len(data['forecast']['forecasts']) == 1
        assert data['forecast']['forecasts'][0]['temperature'] == 25.0
    
    @patch('app.services.weather_service.WeatherService.get_weather_alerts')
    def test_weather_alerts_endpoint(self, mock_get_alerts):
        """Test /api/weather-alerts/{zip_code} endpoint"""
        app = self.create_app()
        client = app.test_client()
        
        # Mock alerts data
        mock_alerts_data = {
            'alerts': [
                {
                    'sender_name': 'NWS',
                    'event': 'Heat Advisory',
                    'description': 'High temperatures expected'
                }
            ],
            'has_alerts': True,
            'alert_count': 1
        }
        mock_get_alerts.return_value = mock_alerts_data
        
        # Test the endpoint
        response = client.get('/api/weather-alerts/101000')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        assert data['alerts']['has_alerts'] == True
        assert data['alerts']['alert_count'] == 1
        assert len(data['alerts']['alerts']) == 1
        assert data['alerts']['alerts'][0]['event'] == 'Heat Advisory'

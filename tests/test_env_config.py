import pytest
import os
import tempfile
from unittest.mock import patch
from app.config import Config, DevelopmentConfig, ProductionConfig, TestConfig


class TestEnvironmentConfiguration:
    """Test cases for environment configuration and API key loading"""
    
    def setup_method(self):
        """Setup test environment"""
        # Store original environment variables
        self.original_env = {}
        for key in ['WEATHER_API_KEY', 'GEMINI_API_KEY', 'DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']:
            if key in os.environ:
                self.original_env[key] = os.environ[key]
    
    def teardown_method(self):
        """Cleanup after tests"""
        # Restore original environment variables
        for key in self.original_env:
            os.environ[key] = self.original_env[key]
        
        # Remove test environment variables
        for key in ['WEATHER_API_KEY', 'GEMINI_API_KEY', 'DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']:
            if key in os.environ and key not in self.original_env:
                del os.environ[key]
    
    def test_config_loading_with_env_vars(self):
        """Test that configuration loads environment variables correctly"""
        # Set test environment variables
        os.environ['WEATHER_API_KEY'] = 'test_weather_key_12345'
        os.environ['GEMINI_API_KEY'] = 'test_gemini_key_67890'
        os.environ['GEMINI_MODEL'] = 'gemini-2.0-flash-exp'
        os.environ['DB_HOST'] = 'test_host'
        os.environ['DB_USER'] = 'test_user'
        os.environ['DB_PASSWORD'] = 'test_password'
        os.environ['DB_NAME'] = 'test_database'
        
        # Test base config
        assert Config.WEATHER_API_KEY == 'test_weather_key_12345'
        assert Config.GEMINI_API_KEY == 'test_gemini_key_67890'
        assert Config.GEMINI_MODEL == 'gemini-2.0-flash-exp'
        
        # Test development config
        dev_config = DevelopmentConfig()
        assert dev_config.WEATHER_API_KEY == 'test_weather_key_12345'
        assert dev_config.GEMINI_API_KEY == 'test_gemini_key_67890'
        assert dev_config.GEMINI_MODEL == 'gemini-2.0-flash-exp'
        assert dev_config.DB_HOST == 'test_host'
        assert dev_config.DB_USER == 'test_user'
        assert dev_config.DB_PASSWORD == 'test_password'
        assert dev_config.DB_NAME == 'test_database'
        assert dev_config.DEBUG == True
    
    def test_config_default_values(self):
        """Test that configuration uses default values when env vars are not set"""
        # Clear environment variables
        for key in ['WEATHER_API_KEY', 'GEMINI_API_KEY', 'GEMINI_MODEL', 'DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']:
            if key in os.environ:
                del os.environ[key]
        
        # Test base config with defaults
        assert Config.WEATHER_API_KEY is None
        assert Config.GEMINI_API_KEY is None
        assert Config.GEMINI_MODEL == 'gemini-2.0-flash-exp'
        
        # Test development config with defaults
        dev_config = DevelopmentConfig()
        assert dev_config.WEATHER_API_KEY is None
        assert dev_config.GEMINI_API_KEY is None
        assert dev_config.GEMINI_MODEL == 'gemini-2.0-flash-exp'
        assert dev_config.DB_HOST == 'localhost'
        assert dev_config.DB_USER == 'root'
        assert dev_config.DB_PASSWORD == ''
        assert dev_config.DB_NAME == 'health_notifier'
        assert dev_config.DEBUG == True
    
    def test_production_config(self):
        """Test production configuration"""
        os.environ['DATABASE_URL'] = 'postgresql://user:pass@host:5432/db'
        
        prod_config = ProductionConfig()
        assert prod_config.DATABASE_URL == 'postgresql://user:pass@host:5432/db'
        assert prod_config.DEBUG == False
    
    def test_test_config(self):
        """Test test configuration"""
        test_config = TestConfig()
        assert test_config.TESTING == True
        assert test_config.SQLALCHEMY_DATABASE_URI == 'sqlite:///:memory:'
    
    def test_config_dict(self):
        """Test configuration dictionary"""
        from app.config import config
        
        assert 'development' in config
        assert 'production' in config
        assert 'testing' in config
        assert 'default' in config
        
        assert config['development'] == DevelopmentConfig
        assert config['production'] == ProductionConfig
        assert config['testing'] == TestConfig
        assert config['default'] == DevelopmentConfig
    
    @patch('app.config.load_dotenv')
    def test_dotenv_loading(self, mock_load_dotenv):
        """Test that dotenv is loaded on import"""
        # Re-import config to test dotenv loading
        import importlib
        import app.config
        importlib.reload(app.config)
        
        # Verify load_dotenv was called
        mock_load_dotenv.assert_called_once()
    
    def test_api_key_validation(self):
        """Test API key validation in services"""
        from app.services.weather_service import WeatherService
        from app.services.ai_service import AIService
        from app.utils.exceptions import ExternalAPIException
        
        # Test with missing API key
        with patch('app.config.Config.WEATHER_API_KEY', None):
            with pytest.raises(ExternalAPIException) as exc_info:
                WeatherService.get_onecall_weather_data("101000")
            assert "OneCall API error" in str(exc_info.value)
        
        with patch('app.config.Config.GEMINI_API_KEY', None):
            with pytest.raises(ExternalAPIException) as exc_info:
                AIService.get_risk_recommendations(None, {})
            assert "Gemini API key not configured" in str(exc_info.value)
    
    def test_gemini_model_configuration(self):
        """Test Gemini model configuration"""
        from app.services.ai_service import AIService
        from app.utils.exceptions import ExternalAPIException
        
        # Test with custom model
        with patch('app.config.Config.GEMINI_API_KEY', 'test_key'):
            with patch('app.config.Config.GEMINI_MODEL', 'gemini-1.5-pro'):
                with patch('google.generativeai.configure') as mock_configure:
                    with patch('google.generativeai.GenerativeModel') as mock_model_class:
                        mock_model = Mock()
                        mock_model.generate_content.return_value.text = '{"test": "response"}'
                        mock_model_class.return_value = mock_model
                        
                        # This should use the custom model
                        try:
                            AIService.get_risk_recommendations(None, {})
                        except Exception:
                            pass  # We expect it to fail, just testing model configuration
                        
                        # Verify the correct model was used
                        mock_model_class.assert_called_with('gemini-1.5-pro')
        
        # Test with default model
        with patch('app.config.Config.GEMINI_API_KEY', 'test_key'):
            with patch('app.config.Config.GEMINI_MODEL', None):  # Should use default
                with patch('google.generativeai.configure') as mock_configure:
                    with patch('google.generativeai.GenerativeModel') as mock_model_class:
                        mock_model = Mock()
                        mock_model.generate_content.return_value.text = '{"test": "response"}'
                        mock_model_class.return_value = mock_model
                        
                        try:
                            AIService.get_risk_recommendations(None, {})
                        except Exception:
                            pass
                        
                        # Verify the default model was used
                        mock_model_class.assert_called_with('gemini-2.0-flash-exp')
    
    def test_database_uri_construction(self):
        """Test database URI construction"""
        os.environ['DB_HOST'] = 'test_host'
        os.environ['DB_USER'] = 'test_user'
        os.environ['DB_PASSWORD'] = 'test_password'
        os.environ['DB_NAME'] = 'test_database'
        
        dev_config = DevelopmentConfig()
        expected_uri = "mysql+pymysql://test_user:test_password@test_host/test_database"
        assert dev_config.SQLALCHEMY_DATABASE_URI == expected_uri
    
    def test_database_uri_with_empty_password(self):
        """Test database URI construction with empty password"""
        os.environ['DB_HOST'] = 'test_host'
        os.environ['DB_USER'] = 'test_user'
        os.environ['DB_PASSWORD'] = ''
        os.environ['DB_NAME'] = 'test_database'
        
        dev_config = DevelopmentConfig()
        expected_uri = "mysql+pymysql://test_user:@test_host/test_database"
        assert dev_config.SQLALCHEMY_DATABASE_URI == expected_uri
    
    def test_database_uri_with_special_characters(self):
        """Test database URI construction with special characters in password"""
        os.environ['DB_HOST'] = 'test_host'
        os.environ['DB_USER'] = 'test_user'
        os.environ['DB_PASSWORD'] = 'p@ssw0rd!@#'
        os.environ['DB_NAME'] = 'test_database'
        
        dev_config = DevelopmentConfig()
        # Password should be URL encoded
        expected_uri = "mysql+pymysql://test_user:p%40ssw0rd%21%40%23@test_host/test_database"
        assert dev_config.SQLALCHEMY_DATABASE_URI == expected_uri


class TestEnvironmentFileLoading:
    """Test cases for .env file loading"""
    
    def test_env_file_loading(self):
        """Test loading environment variables from .env file"""
        # Create a temporary .env file
        env_content = """
WEATHER_API_KEY=test_weather_key_from_file
GEMINI_API_KEY=test_gemini_key_from_file
DB_HOST=localhost_from_file
DB_USER=root_from_file
DB_PASSWORD=password_from_file
DB_NAME=health_notifier_from_file
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file_path = f.name
        
        try:
            # Mock load_dotenv to load our test file
            with patch('app.config.load_dotenv') as mock_load_dotenv:
                # Simulate loading the .env file
                import os
                from dotenv import load_dotenv
                load_dotenv(env_file_path)
                
                # Verify the environment variables are loaded
                assert os.environ.get('WEATHER_API_KEY') == 'test_weather_key_from_file'
                assert os.environ.get('GEMINI_API_KEY') == 'test_gemini_key_from_file'
                assert os.environ.get('DB_HOST') == 'localhost_from_file'
                assert os.environ.get('DB_USER') == 'root_from_file'
                assert os.environ.get('DB_PASSWORD') == 'password_from_file'
                assert os.environ.get('DB_NAME') == 'health_notifier_from_file'
                
                # Verify load_dotenv was called
                mock_load_dotenv.assert_called_once()
        
        finally:
            # Clean up the temporary file
            os.unlink(env_file_path)
    
    def test_env_file_with_comments(self):
        """Test loading .env file with comments"""
        env_content = """
# Weather API Configuration
WEATHER_API_KEY=test_weather_key
# AI API Configuration
GEMINI_API_KEY=test_gemini_key
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=health_notifier
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file_path = f.name
        
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file_path)
            
            # Verify the environment variables are loaded (comments should be ignored)
            assert os.environ.get('WEATHER_API_KEY') == 'test_weather_key'
            assert os.environ.get('GEMINI_API_KEY') == 'test_gemini_key'
            assert os.environ.get('DB_HOST') == 'localhost'
            assert os.environ.get('DB_USER') == 'root'
            assert os.environ.get('DB_PASSWORD') == 'password'
            assert os.environ.get('DB_NAME') == 'health_notifier'
        
        finally:
            os.unlink(env_file_path)
    
    def test_env_file_with_empty_lines(self):
        """Test loading .env file with empty lines"""
        env_content = """
WEATHER_API_KEY=test_weather_key

GEMINI_API_KEY=test_gemini_key

DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=health_notifier
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.env', delete=False) as f:
            f.write(env_content)
            env_file_path = f.name
        
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file_path)
            
            # Verify the environment variables are loaded (empty lines should be ignored)
            assert os.environ.get('WEATHER_API_KEY') == 'test_weather_key'
            assert os.environ.get('GEMINI_API_KEY') == 'test_gemini_key'
            assert os.environ.get('DB_HOST') == 'localhost'
            assert os.environ.get('DB_USER') == 'root'
            assert os.environ.get('DB_PASSWORD') == 'password'
            assert os.environ.get('DB_NAME') == 'health_notifier'
        
        finally:
            os.unlink(env_file_path)


class TestAPIKeyIntegration:
    """Test cases for API key integration in services"""
    
    def setup_method(self):
        """Setup test environment"""
        self.original_env = {}
        for key in ['WEATHER_API_KEY', 'GEMINI_API_KEY']:
            if key in os.environ:
                self.original_env[key] = os.environ[key]
    
    def teardown_method(self):
        """Cleanup after tests"""
        for key in self.original_env:
            os.environ[key] = self.original_env[key]
        
        for key in ['WEATHER_API_KEY', 'GEMINI_API_KEY']:
            if key in os.environ and key not in self.original_env:
                del os.environ[key]
    
    @patch('requests.get')
    def test_weather_service_with_api_key(self, mock_get):
        """Test WeatherService with valid API key"""
        os.environ['WEATHER_API_KEY'] = 'valid_weather_key'
        
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
            "minutely": []
        }
        mock_get.return_value = mock_response
        
        from app.services.weather_service import WeatherService
        
        result = WeatherService.get_onecall_weather_data("101000")
        
        # Verify API key was used in the request
        call_args = mock_get.call_args
        assert call_args[1]['params']['appid'] == 'valid_weather_key'
        
        # Verify response was processed correctly
        assert result['temperature'] == 22.0
        assert result['humidity'] == 89
    
    @patch('google.generativeai.configure')
    @patch('google.generativeai.GenerativeModel')
    def test_ai_service_with_api_key(self, mock_model_class, mock_configure):
        """Test AIService with valid API key"""
        os.environ['GEMINI_API_KEY'] = 'valid_gemini_key'
        
        # Mock the AI response
        mock_model = Mock()
        mock_model.generate_content.return_value.text = '{"immediate_actions": ["Test action"]}'
        mock_model_class.return_value = mock_model
        
        from app.services.ai_service import AIService
        from app.models.patient import Patient
        
        # Create a mock patient
        mock_patient = Mock()
        mock_patient.age = 25
        mock_patient.weeks_pregnant = 20
        mock_patient.zip_code = "101000"
        mock_patient.pregnancy_icd10 = None
        mock_patient.comorbidity_icd10 = None
        mock_patient.get_conditions.return_value = []
        mock_patient.get_medications_list.return_value = []
        
        risk_data = {
            'risk_level': 'medium',
            'risk_score': 3,
            'factors': {},
            'weather_data': {'temperature': 25, 'humidity': 50}
        }
        
        result = AIService.get_risk_recommendations(mock_patient, risk_data)
        
        # Verify API key was used
        mock_configure.assert_called_once_with(api_key='valid_gemini_key')
        
        # Verify response was processed
        assert 'immediate_actions' in result
    
    def test_missing_api_keys_error_handling(self):
        """Test error handling when API keys are missing"""
        # Clear API keys
        if 'WEATHER_API_KEY' in os.environ:
            del os.environ['WEATHER_API_KEY']
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        
        from app.services.weather_service import WeatherService
        from app.services.ai_service import AIService
        from app.utils.exceptions import ExternalAPIException
        
        # Test WeatherService with missing API key
        with pytest.raises(ExternalAPIException):
            WeatherService.get_onecall_weather_data("101000")
        
        # Test AIService with missing API key
        with pytest.raises(ExternalAPIException):
            AIService.get_risk_recommendations(None, {})
    
    def test_invalid_api_keys_error_handling(self):
        """Test error handling with invalid API keys"""
        os.environ['WEATHER_API_KEY'] = 'invalid_key'
        os.environ['GEMINI_API_KEY'] = 'invalid_key'
        
        from app.services.weather_service import WeatherService
        from app.services.ai_service import AIService
        from app.utils.exceptions import ExternalAPIException
        
        # Test WeatherService with invalid API key
        with patch('requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 401
            mock_response.json.return_value = {"message": "Invalid API key"}
            mock_get.return_value = mock_response
            
            with pytest.raises(ExternalAPIException):
                WeatherService.get_onecall_weather_data("101000")
        
        # Test AIService with invalid API key
        with patch('google.generativeai.configure') as mock_configure:
            mock_configure.side_effect = Exception("Invalid API key")
            
            with pytest.raises(ExternalAPIException):
                AIService.get_risk_recommendations(None, {})

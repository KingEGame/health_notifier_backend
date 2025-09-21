# Weather API Testing Guide

This guide explains how to test the weather API integration and environment configuration.

## Test Files Overview

### 1. `test_weather_api.py`
Tests the core WeatherService functionality:
- API key loading and validation
- OneCall API integration
- Current Weather API integration
- Fallback mechanisms
- Error handling
- Heat wave detection
- Weather data processing

### 2. `test_env_config.py`
Tests environment configuration:
- .env file loading
- API key configuration
- Database configuration
- Default values
- Error handling for missing keys

### 3. `test_api_integration.py`
Tests API endpoints integration:
- Weather endpoints with real service calls
- Environment metrics endpoints
- Error handling in endpoints
- Response format validation

## Running Tests

### Run All Weather Tests
```bash
python tests/run_weather_tests.py
```

### Run Specific Test Categories
```bash
# Run only weather API tests
python tests/run_weather_tests.py weather

# Run only environment configuration tests
python tests/run_weather_tests.py env

# Run only integration tests
python tests/run_weather_tests.py integration
```

### Run Individual Test Files
```bash
# Run weather API tests
pytest tests/test_weather_api.py -v

# Run environment config tests
pytest tests/test_env_config.py -v

# Run integration tests
pytest tests/test_api_integration.py -v
```

### Run Specific Test Functions
```bash
# Run specific test function
pytest tests/test_weather_api.py::TestWeatherService::test_onecall_api_success -v

# Run tests matching a pattern
pytest tests/test_weather_api.py -k "api_key" -v
```

## Test Environment Setup

### Required Environment Variables
The tests use mock API keys, but you can set real ones for integration testing:

```bash
export WEATHER_API_KEY="your_openweather_api_key"
export GEMINI_API_KEY="your_gemini_api_key"
```

### Test Database
Tests use in-memory SQLite database by default. No setup required.

## Test Coverage

### WeatherService Tests
- ✅ API key loading from environment
- ✅ OneCall API (3.0) integration
- ✅ Current Weather API (2.5) integration
- ✅ Automatic fallback mechanism
- ✅ Temperature conversion (Kelvin to Celsius)
- ✅ Heat wave detection logic
- ✅ Heat index calculation
- ✅ Weather data processing
- ✅ Error handling for HTTP errors
- ✅ Error handling for network errors
- ✅ Default data when API fails

### Environment Configuration Tests
- ✅ .env file loading
- ✅ API key validation
- ✅ Database URI construction
- ✅ Default value handling
- ✅ Special characters in passwords
- ✅ Missing API key error handling
- ✅ Invalid API key error handling

### API Integration Tests
- ✅ Weather endpoint (`/api/weather/{zip_code}`)
- ✅ OneCall endpoint (`/api/weather-onecall/{zip_code}`)
- ✅ Forecast endpoint (`/api/weather-forecast/{zip_code}`)
- ✅ Alerts endpoint (`/api/weather-alerts/{zip_code}`)
- ✅ AI analysis endpoint (`/api/weather-ai-analysis/{zip_code}`)
- ✅ Environment metrics endpoint (`/api/environment-metrics`)
- ✅ Error handling in all endpoints
- ✅ Response format validation

## Mock Data Examples

### OneCall API Response
```json
{
  "lat": 33.44,
  "lon": -94.04,
  "timezone": "America/Chicago",
  "timezone_offset": -18000,
  "current": {
    "dt": 1758460450,
    "sunrise": 1758456226,
    "sunset": 1758500074,
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
  "minutely": [
    {
      "dt": 1758460500,
      "precipitation": 0
    }
  ]
}
```

### Processed Weather Data
```json
{
  "temperature": 22.0,
  "feels_like": 22.6,
  "humidity": 89,
  "pressure": 1015,
  "description": "clear sky",
  "is_heat_wave": false,
  "heat_index": 24.2,
  "uv_index": 0.21,
  "wind_speed": 2.68,
  "wind_deg": 159,
  "wind_gust": 5.36,
  "visibility": 10000,
  "cloudiness": 0,
  "dew_point": 20.14,
  "sunrise": 1758456226,
  "sunset": 1758500074,
  "timestamp": 1758460450,
  "timezone": "America/Chicago",
  "timezone_offset": -18000,
  "location": {
    "name": "Unknown",
    "country": "Unknown",
    "coordinates": {
      "lat": 33.44,
      "lon": -94.04
    }
  },
  "minutely_precipitation": [
    {
      "datetime": 1758460500,
      "precipitation": 0
    }
  ]
}
```

## Expected Test Results

### Successful Test Run
```
🌤️  Running Weather API and Environment Configuration Tests
============================================================

tests/test_weather_api.py::TestWeatherService::test_api_key_loading PASSED
tests/test_weather_api.py::TestWeatherService::test_onecall_api_success PASSED
tests/test_weather_api.py::TestWeatherService::test_current_weather_api_success PASSED
tests/test_weather_api.py::TestWeatherService::test_api_fallback_mechanism PASSED
tests/test_weather_api.py::TestWeatherService::test_api_key_missing PASSED
tests/test_weather_api.py::TestWeatherService::test_api_http_error PASSED
tests/test_weather_api.py::TestWeatherService::test_api_network_error PASSED
tests/test_weather_api.py::TestWeatherService::test_heat_wave_detection PASSED
tests/test_weather_api.py::TestWeatherService::test_forecast_api PASSED
tests/test_weather_api.py::TestWeatherService::test_weather_alerts_api PASSED
tests/test_weather_api.py::TestWeatherService::test_default_weather_data PASSED
tests/test_weather_api.py::TestWeatherService::test_heat_index_calculation PASSED
tests/test_weather_api.py::TestWeatherService::test_heat_wave_detection_logic PASSED
tests/test_weather_api.py::TestWeatherAPIEndpoints::test_weather_endpoint PASSED
tests/test_weather_api.py::TestWeatherAPIEndpoints::test_weather_onecall_endpoint PASSED
tests/test_weather_api.py::TestWeatherAPIEndpoints::test_weather_forecast_endpoint PASSED
tests/test_weather_api.py::TestWeatherAPIEndpoints::test_weather_alerts_endpoint PASSED

tests/test_env_config.py::TestEnvironmentConfiguration::test_config_loading_with_env_vars PASSED
tests/test_env_config.py::TestEnvironmentConfiguration::test_config_default_values PASSED
tests/test_env_config.py::TestEnvironmentConfiguration::test_production_config PASSED
tests/test_env_config.py::TestEnvironmentConfiguration::test_test_config PASSED
tests/test_env_config.py::TestEnvironmentConfiguration::test_config_dict PASSED
tests/test_env_config.py::TestEnvironmentConfiguration::test_dotenv_loading PASSED
tests/test_env_config.py::TestEnvironmentConfiguration::test_api_key_validation PASSED
tests/test_env_config.py::TestEnvironmentConfiguration::test_database_uri_construction PASSED
tests/test_env_config.py::TestEnvironmentConfiguration::test_database_uri_with_empty_password PASSED
tests/test_env_config.py::TestEnvironmentConfiguration::test_database_uri_with_special_characters PASSED

tests/test_api_integration.py::TestWeatherAPIIntegration::test_weather_endpoint_integration PASSED
tests/test_api_integration.py::TestWeatherAPIIntegration::test_weather_onecall_endpoint_integration PASSED
tests/test_api_integration.py::TestWeatherAPIIntegration::test_weather_forecast_endpoint_integration PASSED
tests/test_api_integration.py::TestWeatherAPIIntegration::test_weather_alerts_endpoint_integration PASSED
tests/test_api_integration.py::TestWeatherAPIIntegration::test_weather_ai_analysis_endpoint_integration PASSED
tests/test_api_integration.py::TestWeatherAPIIntegration::test_weather_endpoint_error_handling PASSED
tests/test_api_integration.py::TestWeatherAPIIntegration::test_weather_onecall_endpoint_error_handling PASSED
tests/test_api_integration.py::TestWeatherAPIIntegration::test_weather_forecast_endpoint_error_handling PASSED
tests/test_api_integration.py::TestWeatherAPIIntegration::test_weather_alerts_endpoint_error_handling PASSED
tests/test_api_integration.py::TestWeatherAPIIntegration::test_weather_ai_analysis_endpoint_error_handling PASSED
tests/test_api_integration.py::TestEnvironmentMetricsAPIIntegration::test_environment_metrics_endpoint_integration PASSED
tests/test_api_integration.py::TestEnvironmentMetricsAPIIntegration::test_environment_metrics_no_patients PASSED
tests/test_api_integration.py::TestEnvironmentMetricsAPIIntegration::test_environment_metrics_error_handling PASSED

========================================= 42 passed in 2.34s =========================================

✅ All tests passed successfully!
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Make sure you're running tests from the project root
   - Check that all dependencies are installed

2. **API Key Errors**
   - Tests use mock API keys by default
   - For real API testing, set environment variables

3. **Database Errors**
   - Tests use in-memory SQLite
   - No database setup required

4. **Mock Errors**
   - Check that mock patches are correctly applied
   - Verify mock return values match expected format

### Debug Mode
Run tests with debug output:
```bash
pytest tests/test_weather_api.py -v -s --tb=long
```

### Coverage Report
Generate test coverage report:
```bash
pytest tests/ --cov=app.services.weather_service --cov=app.config --cov-report=html
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:
- No external dependencies required
- All API calls are mocked
- Fast execution time
- Comprehensive error handling tests

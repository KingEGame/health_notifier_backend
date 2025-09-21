import requests
from flask import current_app
from app.utils.exceptions import ExternalAPIException
import logging

logger = logging.getLogger(__name__)

class WeatherService:
    """Service for weather data integration"""
    
    @staticmethod
    def get_weather_data(zip_code):
        """Get weather data by zip code using OpenWeatherMap API"""
        try:
            # Try OneCall API first (more comprehensive data)
            return WeatherService.get_onecall_weather_data(zip_code)
        except Exception as e:
            logger.warning(f"OneCall API failed, trying Current Weather API: {e}")
            # Fallback to Current Weather API
            return WeatherService.get_current_weather_data(zip_code)
    
    @staticmethod
    def get_onecall_weather_data(zip_code):
        """Get weather data using OneCall API (3.0)"""
        try:
            url = "http://api.openweathermap.org/data/3.0/onecall"
            params = {
                'zip': zip_code,
                'appid': current_app.config['WEATHER_API_KEY'],
                'units': 'metric'
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return WeatherService._process_weather_data(data)
            else:
                raise ExternalAPIException(f"OneCall API returned status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"OneCall API error: {e}")
            raise ExternalAPIException(f"OneCall API error: {str(e)}")
    
    @staticmethod
    def get_current_weather_data(zip_code):
        """Get weather data using Current Weather API (2.5)"""
        try:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {
                'zip': zip_code,
                'appid': current_app.config['WEATHER_API_KEY'],
                'units': 'metric'
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return WeatherService._process_weather_data(data)
            else:
                raise ExternalAPIException(f"Current Weather API returned status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Current Weather API error: {e}")
            # Return default values if API fails
            return WeatherService._get_default_weather_data()
    
    @staticmethod
    def get_weather_forecast(zip_code, days=5):
        """Get weather forecast for multiple days"""
        try:
            url = "http://api.openweathermap.org/data/2.5/forecast"
            params = {
                'zip': zip_code,
                'appid': current_app.config['WEATHER_API_KEY'],
                'units': 'metric',
                'cnt': days * 8  # 8 forecasts per day (every 3 hours)
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return WeatherService._process_forecast_data(data)
            else:
                raise ExternalAPIException(f"Weather forecast API returned status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather forecast API error: {e}")
            return WeatherService._get_default_forecast_data()
    
    @staticmethod
    def get_weather_alerts(zip_code):
        """Get weather alerts and warnings using OneCall API"""
        try:
            url = "http://api.openweathermap.org/data/3.0/onecall"
            params = {
                'zip': zip_code,
                'appid': current_app.config['WEATHER_API_KEY'],
                'units': 'metric',
                'exclude': 'minutely,hourly,daily'
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return WeatherService._process_alert_data(data)
            else:
                # Fallback to basic weather data
                return WeatherService.get_weather_data(zip_code)
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Weather alerts API error: {e}")
            return WeatherService.get_weather_data(zip_code)
    
    @staticmethod
    def _process_weather_data(data):
        """Process weather data from API response - supports both Current Weather and OneCall APIs"""
        # Check if this is OneCall API format (has 'current' key)
        if 'current' in data:
            return WeatherService._process_onecall_data(data)
        else:
            return WeatherService._process_current_weather_data(data)
    
    @staticmethod
    def _process_onecall_data(data):
        """Process OneCall API data format"""
        current = data.get('current', {})
        weather = current.get('weather', [{}])[0]
        
        # Convert temperature from Kelvin to Celsius
        temperature = current.get('temp', 295.15) - 273.15
        feels_like = current.get('feels_like', temperature + 273.15) - 273.15
        humidity = current.get('humidity', 50)
        
        return {
            'temperature': round(temperature, 1),
            'feels_like': round(feels_like, 1),
            'humidity': humidity,
            'pressure': current.get('pressure', 1013),
            'description': weather.get('description', 'Unknown'),
            'is_heat_wave': WeatherService._is_heat_wave(temperature, humidity),
            'heat_index': WeatherService._calculate_heat_index(temperature, humidity),
            'uv_index': current.get('uvi', 0),
            'wind_speed': current.get('wind_speed', 0),
            'wind_deg': current.get('wind_deg', 0),
            'wind_gust': current.get('wind_gust', 0),
            'visibility': current.get('visibility', 10000),
            'cloudiness': current.get('clouds', 0),
            'dew_point': current.get('dew_point', 0) - 273.15,  # Convert from Kelvin
            'sunrise': current.get('sunrise', 0),
            'sunset': current.get('sunset', 0),
            'timestamp': current.get('dt', 0),
            'timezone': data.get('timezone', 'Unknown'),
            'timezone_offset': data.get('timezone_offset', 0),
            'location': {
                'name': 'Unknown',  # OneCall doesn't provide city name
                'country': 'Unknown',
                'coordinates': {
                    'lat': data.get('lat', 0),
                    'lon': data.get('lon', 0)
                }
            },
            'minutely_precipitation': WeatherService._process_minutely_data(data.get('minutely', []))
        }
    
    @staticmethod
    def _process_current_weather_data(data):
        """Process Current Weather API data format"""
        main = data.get('main', {})
        weather = data.get('weather', [{}])[0]
        
        temperature = main.get('temp', 25)
        humidity = main.get('humidity', 50)
        
        return {
            'temperature': temperature,
            'feels_like': main.get('feels_like', temperature),
            'humidity': humidity,
            'pressure': main.get('pressure', 1013),
            'description': weather.get('description', 'Unknown'),
            'is_heat_wave': WeatherService._is_heat_wave(temperature, humidity),
            'heat_index': WeatherService._calculate_heat_index(temperature, humidity),
            'uv_index': data.get('uvi', 0),
            'wind_speed': data.get('wind', {}).get('speed', 0),
            'wind_deg': data.get('wind', {}).get('deg', 0),
            'wind_gust': data.get('wind', {}).get('gust', 0),
            'visibility': data.get('visibility', 10000),
            'cloudiness': data.get('clouds', {}).get('all', 0),
            'dew_point': main.get('dew_point', 0),
            'sunrise': data.get('sys', {}).get('sunrise', 0),
            'sunset': data.get('sys', {}).get('sunset', 0),
            'timestamp': data.get('dt', 0),
            'timezone': 'Unknown',
            'timezone_offset': 0,
            'location': {
                'name': data.get('name', 'Unknown'),
                'country': data.get('sys', {}).get('country', 'Unknown'),
                'coordinates': {
                    'lat': data.get('coord', {}).get('lat', 0),
                    'lon': data.get('coord', {}).get('lon', 0)
                }
            },
            'minutely_precipitation': []
        }
    
    @staticmethod
    def _process_minutely_data(minutely_data):
        """Process minutely precipitation data"""
        if not minutely_data:
            return []
        
        # Return first 60 minutes of precipitation data
        return [
            {
                'datetime': item.get('dt', 0),
                'precipitation': item.get('precipitation', 0)
            }
            for item in minutely_data[:60]
        ]
    
    @staticmethod
    def _process_forecast_data(data):
        """Process forecast data from API response"""
        forecasts = []
        
        for item in data.get('list', []):
            main = item.get('main', {})
            weather = item.get('weather', [{}])[0]
            
            temperature = main.get('temp', 25)
            humidity = main.get('humidity', 50)
            
            forecasts.append({
                'datetime': item.get('dt', 0),
                'temperature': temperature,
                'feels_like': main.get('feels_like', temperature),
                'humidity': humidity,
                'pressure': main.get('pressure', 1013),
                'description': weather.get('description', 'Unknown'),
                'is_heat_wave': WeatherService._is_heat_wave(temperature, humidity),
                'heat_index': WeatherService._calculate_heat_index(temperature, humidity),
                'precipitation_probability': item.get('pop', 0) * 100,
                'wind_speed': item.get('wind', {}).get('speed', 0)
            })
        
        return {
            'forecasts': forecasts,
            'location': {
                'name': data.get('city', {}).get('name', 'Unknown'),
                'country': data.get('city', {}).get('country', 'Unknown')
            }
        }
    
    @staticmethod
    def _process_alert_data(data):
        """Process alert data from API response"""
        alerts = data.get('alerts', [])
        
        return {
            'alerts': alerts,
            'has_alerts': len(alerts) > 0,
            'alert_count': len(alerts)
        }
    
    @staticmethod
    def _is_heat_wave(temperature, humidity):
        """Determine if current conditions constitute a heat wave"""
        # Heat wave criteria: temperature > 35°C OR heat index > 40°C
        heat_index = WeatherService._calculate_heat_index(temperature, humidity)
        return temperature > 35 or heat_index > 40
    
    @staticmethod
    def _get_default_weather_data():
        """Get default weather data when API fails"""
        return {
            'temperature': 25,
            'feels_like': 25,
            'humidity': 50,
            'pressure': 1013,
            'description': 'Unknown',
            'is_heat_wave': False,
            'heat_index': 25,
            'uv_index': 0,
            'wind_speed': 0,
            'wind_deg': 0,
            'wind_gust': 0,
            'visibility': 10000,
            'cloudiness': 0,
            'dew_point': 0,
            'sunrise': 0,
            'sunset': 0,
            'timestamp': 0,
            'timezone': 'Unknown',
            'timezone_offset': 0,
            'location': {
                'name': 'Unknown',
                'country': 'Unknown',
                'coordinates': {'lat': 0, 'lon': 0}
            },
            'minutely_precipitation': []
        }
    
    @staticmethod
    def _get_default_forecast_data():
        """Get default forecast data when API fails"""
        return {
            'forecasts': [],
            'location': {
                'name': 'Unknown',
                'country': 'Unknown'
            }
        }
    
    @staticmethod
    def _calculate_heat_index(temp_c, humidity):
        """Calculate heat index in Celsius"""
        # Convert to Fahrenheit for calculation
        temp_f = (temp_c * 9/5) + 32
        
        # Heat index formula
        hi = -42.379 + 2.04901523 * temp_f + 10.14333127 * humidity
        hi += -0.22475541 * temp_f * humidity - 6.83783e-3 * temp_f**2
        hi += -5.481717e-2 * humidity**2 + 1.22874e-3 * temp_f**2 * humidity
        hi += 8.5282e-4 * temp_f * humidity**2 - 1.99e-6 * temp_f**2 * humidity**2
        
        # Convert back to Celsius
        return (hi - 32) * 5/9

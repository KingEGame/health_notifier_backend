import requests
from flask import current_app
from app.utils.exceptions import ExternalAPIException

class WeatherService:
    """Service for weather data integration"""
    
    @staticmethod
    def get_weather_data(zip_code):
        """Get weather data by zip code using OpenWeatherMap API"""
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
                return {
                    'temperature': data['main']['temp'],
                    'feels_like': data['main']['feels_like'],
                    'humidity': data['main']['humidity'],
                    'pressure': data['main']['pressure'],
                    'description': data['weather'][0]['description'],
                    'is_heat_wave': data['main']['temp'] > 35,
                    'heat_index': WeatherService._calculate_heat_index(
                        data['main']['temp'], 
                        data['main']['humidity']
                    )
                }
            else:
                raise ExternalAPIException(f"Weather API returned status {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Weather API error: {e}")
            # Return default values if API fails
            return {
                'temperature': 25,
                'feels_like': 25,
                'humidity': 50,
                'pressure': 1013,
                'description': 'Unknown',
                'is_heat_wave': False,
                'heat_index': 25
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

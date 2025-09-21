#!/usr/bin/env python3
"""
Demo script showing how to use the weather API endpoints
"""

import requests
import json
import time
from typing import Dict, Any

class WeatherAPIDemo:
    """Demo class for weather API usage"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def test_health_check(self) -> Dict[str, Any]:
        """Test health check endpoint"""
        print("🏥 Testing health check...")
        try:
            response = self.session.get(f"{self.base_url}/api/health")
            response.raise_for_status()
            data = response.json()
            print(f"✅ Health check: {data['status']}")
            return data
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return {}
    
    def test_weather_data(self, zip_code: str) -> Dict[str, Any]:
        """Test basic weather data endpoint"""
        print(f"🌤️  Testing weather data for {zip_code}...")
        try:
            response = self.session.get(f"{self.base_url}/api/weather/{zip_code}")
            response.raise_for_status()
            data = response.json()
            if data['success']:
                weather = data['weather']
                print(f"✅ Weather: {weather['temperature']}°C, {weather['description']}")
                print(f"   Heat wave: {weather['is_heat_wave']}, Heat index: {weather['heat_index']:.1f}°C")
                return data
            else:
                print(f"❌ Weather API error: {data.get('error', 'Unknown error')}")
                return {}
        except Exception as e:
            print(f"❌ Weather request failed: {e}")
            return {}
    
    def test_weather_onecall(self, zip_code: str) -> Dict[str, Any]:
        """Test OneCall weather data endpoint"""
        print(f"🌡️  Testing OneCall weather data for {zip_code}...")
        try:
            response = self.session.get(f"{self.base_url}/api/weather-onecall/{zip_code}")
            response.raise_for_status()
            data = response.json()
            if data['success']:
                weather = data['weather']
                print(f"✅ OneCall Weather: {weather['temperature']}°C, {weather['description']}")
                print(f"   UV Index: {weather['uv_index']}, Wind: {weather['wind_speed']} m/s")
                print(f"   Timezone: {weather['timezone']}")
                return data
            else:
                print(f"❌ OneCall API error: {data.get('error', 'Unknown error')}")
                return {}
        except Exception as e:
            print(f"❌ OneCall request failed: {e}")
            return {}
    
    def test_weather_forecast(self, zip_code: str, days: int = 3) -> Dict[str, Any]:
        """Test weather forecast endpoint"""
        print(f"📅 Testing weather forecast for {zip_code} ({days} days)...")
        try:
            response = self.session.get(f"{self.base_url}/api/weather-forecast/{zip_code}?days={days}")
            response.raise_for_status()
            data = response.json()
            if data['success']:
                forecast = data['forecast']
                print(f"✅ Forecast: {len(forecast['forecasts'])} periods")
                for i, period in enumerate(forecast['forecasts'][:3]):  # Show first 3
                    print(f"   Period {i+1}: {period['temperature']}°C, {period['description']}")
                return data
            else:
                print(f"❌ Forecast API error: {data.get('error', 'Unknown error')}")
                return {}
        except Exception as e:
            print(f"❌ Forecast request failed: {e}")
            return {}
    
    def test_weather_alerts(self, zip_code: str) -> Dict[str, Any]:
        """Test weather alerts endpoint"""
        print(f"⚠️  Testing weather alerts for {zip_code}...")
        try:
            response = self.session.get(f"{self.base_url}/api/weather-alerts/{zip_code}")
            response.raise_for_status()
            data = response.json()
            if data['success']:
                alerts = data['alerts']
                print(f"✅ Alerts: {alerts['alert_count']} active alerts")
                if alerts['has_alerts']:
                    for alert in alerts['alerts'][:2]:  # Show first 2 alerts
                        print(f"   - {alert['event']}: {alert['description'][:50]}...")
                else:
                    print("   No active weather alerts")
                return data
            else:
                print(f"❌ Alerts API error: {data.get('error', 'Unknown error')}")
                return {}
        except Exception as e:
            print(f"❌ Alerts request failed: {e}")
            return {}
    
    def test_weather_ai_analysis(self, zip_code: str) -> Dict[str, Any]:
        """Test weather AI analysis endpoint"""
        print(f"🤖 Testing weather AI analysis for {zip_code}...")
        try:
            response = self.session.get(f"{self.base_url}/api/weather-ai-analysis/{zip_code}")
            response.raise_for_status()
            data = response.json()
            if data['success']:
                ai_analysis = data['ai_analysis']
                print(f"✅ AI Analysis: Risk level {ai_analysis['risk_level']}")
                print(f"   Patient count: {data['patient_count']}")
                if 'health_concerns' in ai_analysis:
                    print(f"   Health concerns: {len(ai_analysis['health_concerns'])} identified")
                return data
            else:
                print(f"❌ AI Analysis error: {data.get('error', 'Unknown error')}")
                return {}
        except Exception as e:
            print(f"❌ AI Analysis request failed: {e}")
            return {}
    
    def test_environment_metrics(self) -> Dict[str, Any]:
        """Test environment metrics endpoint"""
        print("📊 Testing environment metrics...")
        try:
            response = self.session.get(f"{self.base_url}/api/environment-metrics")
            response.raise_for_status()
            data = response.json()
            if data['success']:
                metrics = data['environment_metrics']
                print(f"✅ Environment Metrics:")
                print(f"   Total patients: {metrics['total_patients']}")
                print(f"   Patients at risk: {metrics['patients_at_risk']}")
                print(f"   Extreme heat conditions: {metrics['extreme_heat_conditions']}")
                print(f"   Risk distribution: {metrics['risk_distribution']}")
                return data
            else:
                print(f"❌ Environment metrics error: {data.get('error', 'Unknown error')}")
                return {}
        except Exception as e:
            print(f"❌ Environment metrics request failed: {e}")
            return {}
    
    def test_risk_patients(self) -> Dict[str, Any]:
        """Test risk patients endpoint"""
        print("👥 Testing risk patients...")
        try:
            response = self.session.get(f"{self.base_url}/api/risk-patients")
            response.raise_for_status()
            data = response.json()
            if data['success']:
                summary = data['summary']
                print(f"✅ Risk Patients:")
                print(f"   Total patients: {summary['total_patients']}")
                print(f"   Patients at risk: {summary['patients_at_risk']}")
                print(f"   Risk distribution: {summary['risk_distribution']}")
                return data
            else:
                print(f"❌ Risk patients error: {data.get('error', 'Unknown error')}")
                return {}
        except Exception as e:
            print(f"❌ Risk patients request failed: {e}")
            return {}
    
    def run_full_demo(self, zip_codes: list = None):
        """Run full API demo"""
        if zip_codes is None:
            zip_codes = ["10001", "90210", "33101"]  # NYC, Beverly Hills, Miami
        
        print("🚀 Starting Weather API Demo")
        print("=" * 50)
        
        # Test health check first
        health_data = self.test_health_check()
        if not health_data:
            print("❌ Health check failed, stopping demo")
            return
        
        print("\n" + "=" * 50)
        
        # Test each zip code
        for zip_code in zip_codes:
            print(f"\n📍 Testing location: {zip_code}")
            print("-" * 30)
            
            # Basic weather data
            self.test_weather_data(zip_code)
            time.sleep(0.5)  # Small delay between requests
            
            # OneCall weather data
            self.test_weather_onecall(zip_code)
            time.sleep(0.5)
            
            # Weather forecast
            self.test_weather_forecast(zip_code, days=2)
            time.sleep(0.5)
            
            # Weather alerts
            self.test_weather_alerts(zip_code)
            time.sleep(0.5)
            
            # AI analysis
            self.test_weather_ai_analysis(zip_code)
            time.sleep(0.5)
        
        print("\n" + "=" * 50)
        
        # Test system-wide endpoints
        print("\n📊 Testing system-wide endpoints:")
        print("-" * 30)
        
        # Environment metrics
        self.test_environment_metrics()
        time.sleep(0.5)
        
        # Risk patients
        self.test_risk_patients()
        
        print("\n🎉 Demo completed!")

def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Weather API Demo')
    parser.add_argument('--url', default='http://localhost:5000', help='Base URL for API')
    parser.add_argument('--zip', nargs='+', help='Zip codes to test')
    parser.add_argument('--quick', action='store_true', help='Run quick demo with fewer tests')
    
    args = parser.parse_args()
    
    demo = WeatherAPIDemo(args.url)
    
    if args.quick:
        print("🏃 Running quick demo...")
        demo.test_health_check()
        demo.test_weather_data("10001")
        demo.test_environment_metrics()
    else:
        demo.run_full_demo(args.zip)

if __name__ == '__main__':
    main()

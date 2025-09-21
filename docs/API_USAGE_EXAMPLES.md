# API Usage Examples

## New API Endpoints for Environmental Metrics and Patient Risk Assessment

### 1. Environmental Condition Metrics

#### Get metrics for all patients
```bash
GET /api/environment-metrics
```

**Response:**
```json
{
  "success": true,
  "environment_metrics": {
    "total_patients": 150,
    "patients_at_risk": 45,
    "extreme_heat_conditions": 12,
    "risk_distribution": {
      "low": 105,
      "medium": 30,
      "high": 15
    },
    "weather_conditions": {
      "101000": {
        "temperature": 38.5,
        "feels_like": 42.1,
        "humidity": 75,
        "description": "Extreme heat",
        "is_heat_wave": true,
        "heat_index": 45.2,
        "patient_count": 25
      }
    },
    "at_risk_patients": [...]
  }
}
```

#### Get metrics for specific location
```bash
GET /api/environment-metrics/101000
```

### 2. Weather Data and Forecasts

#### Current weather
```bash
GET /api/weather/101000
```

#### Comprehensive weather data (OneCall API)
```bash
GET /api/weather-onecall/101000
```

**Response:**
```json
{
  "success": true,
  "weather": {
    "temperature": 22.0,
    "feels_like": 23.5,
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
}
```

#### Weather forecast
```bash
GET /api/weather-forecast/101000?days=5
```

#### Weather alerts
```bash
GET /api/weather-alerts/101000
```

#### AI weather risk analysis
```bash
GET /api/weather-ai-analysis/101000
```

**Response:**
```json
{
  "success": true,
  "weather_data": {...},
  "patient_count": 25,
  "ai_analysis": {
    "risk_level": "High",
    "health_concerns": [
      "Heat exhaustion risk for pregnant women",
      "Dehydration risk due to high temperature and humidity"
    ],
    "immediate_recommendations": [
      "Stay indoors with air conditioning",
      "Drink plenty of water",
      "Monitor for heat exhaustion symptoms"
    ],
    "preventive_measures": [
      "Avoid outdoor activities during peak heat",
      "Wear light, loose clothing",
      "Use fans or air conditioning"
    ],
    "emergency_actions": [
      "Seek medical help if symptoms worsen",
      "Call emergency services for severe symptoms"
    ]
  }
}
```

### 3. Patients with Risk Assessment

#### Get all patients with risks
```bash
GET /api/risk-patients
```

**Query parameters:**
- `risk_level` - filter by risk level (low, medium, high)
- `location` - filter by zip_code
- `include_ai_suggestions` - include AI suggestions (true/false)

**Example:**
```bash
GET /api/risk-patients?risk_level=high&include_ai_suggestions=true
```

#### Get risk details for specific patient
```bash
GET /api/risk-patients/123
```

#### Comprehensive risk assessment for patient
```bash
GET /api/risk-patients/123/comprehensive
```

**Response:**
```json
{
  "success": true,
  "comprehensive_assessment": {
    "patient_id": 123,
    "patient_name": "Anna Ivanova",
    "basic_risk": {
      "risk_level": "high",
      "risk_score": 7,
      "heat_wave_risk": true,
      "factors": {...}
    },
    "weather_analysis": {
      "current_conditions": {...},
      "risk_level": "high",
      "recommendations": [
        "Stay indoors with air conditioning",
        "Drink plenty of water",
        "Avoid outdoor activities"
      ]
    },
    "overall_assessment": {
      "risk_level": "high",
      "risk_score": 7,
      "priority_level": "high",
      "immediate_concerns": [
        "Extreme heat wave conditions",
        "Third trimester pregnancy"
      ],
      "monitoring_needs": [
        "Increased monitoring due to third trimester",
        "Medical conditions require specialized monitoring"
      ]
    },
    "recommendations": [
      "More frequent prenatal check-ups recommended",
      "Follow medical provider's specific instructions"
    ],
    "ai_suggestions": {
      "immediate_actions": [
        "Immediate medical consultation recommended",
        "Monitor vital signs closely"
      ],
      "medical_recommendations": [
        "Regular prenatal care with increased frequency",
        "Consider hospitalization if symptoms worsen"
      ],
      "lifestyle_changes": [
        "Stay indoors during peak heat hours",
        "Ensure adequate hydration",
        "Use air conditioning if available"
      ],
      "monitoring_guidelines": [
        "Check temperature every 2 hours",
        "Monitor blood pressure daily",
        "Watch for signs of dehydration"
      ],
      "emergency_signs": [
        "Severe headache or dizziness",
        "High fever above 38.5°C",
        "Decreased fetal movement",
        "Severe abdominal pain"
      ],
      "weather_precautions": [
        "Stay indoors with air conditioning",
        "Wear light, loose clothing",
        "Avoid direct sunlight"
      ],
      "follow_up_schedule": [
        "Daily check-ins during heat wave",
        "Weekly prenatal visits",
        "Immediate consultation if symptoms worsen"
      ],
      "priority_level": "High"
    }
  }
}
```

#### Risk summary
```bash
GET /api/risk-patients/summary
```

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_patients": 150,
    "risk_distribution": {
      "low": 105,
      "medium": 30,
      "high": 15
    },
    "patients_at_risk": 45,
    "extreme_heat_risk": 12,
    "average_risk_score": 2.3,
    "risk_percentages": {
      "low": 70.0,
      "medium": 20.0,
      "high": 10.0
    }
  }
}
```

## API Keys Configuration

To work with AI and weather data, you need to configure the following environment variables in the `.env` file:

```env
# OpenWeather API key
WEATHER_API_KEY=your_openweather_api_key_here

# Google Gemini API configuration
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash-exp
```

### Available Gemini Models

You can configure different Gemini models by setting the `GEMINI_MODEL` environment variable:

- `gemini-2.0-flash-exp` (default) - Latest experimental model
- `gemini-1.5-pro` - Pro model with advanced capabilities
- `gemini-1.5-flash` - Fast model for quick responses
- `gemini-pro` - Standard model (legacy)

## Usage Features

1. **AI suggestions**: Require GEMINI_API_KEY configuration. If the key is not configured, fallback recommendations are returned.

2. **Weather data**: Requires WEATHER_API_KEY configuration. If the API is unavailable, default values are returned.

3. **Filtering**: All endpoints support filtering by various parameters.

4. **Pagination**: Pagination is used for large datasets.

5. **Error handling**: All endpoints return structured responses with success/error information.

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

#### Get all patients with risks (Limited to 10 patients for performance)
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

**Response:**
```json
{
  "success": true,
  "risk_patients": [
    {
      "patient_id": 1,
      "name": "Mia Clark",
      "age": 34,
      "zip_code": "10301",
      "phone_number": "+1-555-0123",
      "email": "mia.clark@email.com",
      "address": "123 Main St, New York, NY",
      
      "pregnancy_weeks": 34,
      "trimester": 3,
      "pregnancy_icd10": "O09.5",
      "pregnancy_description": "Supervision of elderly primigravida",
      
      "comorbidity_icd10": "I10",
      "comorbidity_description": "Essential hypertension",
      "conditions": [
        "O09.5: Supervision of elderly primigravida",
        "I10: Essential hypertension"
      ],
      
      "medications": ["Labetalol"],
      "medication_notes": "For hypertension management",
      "ndc_codes": ["00173-0834-01"],
      
      "risk_level": "high",
      "risk_score": 13,
      "heat_wave_risk": false,
      "risk_factors": {
        "age_risk": "high",
        "trimester_risk": "high",
        "location_risk": "low",
        "conditions_risk": "high",
        "medications_risk": "high"
      },
      "weather_conditions": {
        "temperature": 25,
        "description": "Weather API disabled"
      },
      
      "is_high_risk_age": false,
      "age_group": "outside_optimal",
      
      "created_at": "2025-09-21T15:30:06.125059",
      "updated_at": "2025-09-21T15:30:06.125059"
    }
  ],
  "summary": {
    "total_patients": 10,
    "total_available_patients": 1000,
    "patients_limited_to": 10,
    "risk_distribution": {
      "high": 10,
      "medium": 0,
      "low": 0
    },
    "patients_at_risk": 10,
    "filters_applied": {
      "risk_level": null,
      "location": null,
      "include_ai_suggestions": false
    }
  }
}
```

**Key Features:**
- **Performance Optimized**: Returns only first 10 patients for fast response
- **Comprehensive Patient Data**: Includes detailed medical information
- **Risk Assessment**: Complete risk analysis with scoring
- **Medical Details**: Medications, conditions, NDC codes
- **Pregnancy Information**: Weeks, trimester calculation, ICD10 codes
- **Contact Information**: Full patient contact details
- **Timestamps**: Creation and update tracking

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

#### Risk summary (Limited to 10 patients for performance)
```bash
GET /api/risk-patients/summary
```

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_patients": 10,
    "total_available_patients": 1000,
    "patients_limited_to": 10,
    "risk_distribution": {
      "high": 10,
      "medium": 0,
      "low": 0
    },
    "patients_at_risk": 10,
    "extreme_heat_risk": 0,
    "average_risk_score": 12.5,
    "risk_percentages": {
      "high": 100.0,
      "medium": 0.0,
      "low": 0.0
    }
  }
}
```

**Note:** The summary is calculated based on the first 10 patients for performance optimization. The `total_available_patients` field shows the actual total number of patients in the system.

## Recent Updates and Fixes

### Version 1.1.0 - Performance and Data Enhancements

#### ✅ **Fixed Issues:**
1. **Trimester Calculation Error**: Fixed `'CSVPatient' object has no attribute 'trimester'` error by properly calling `_calculate_trimester()` method
2. **API Performance**: Temporarily disabled Weather API to prevent hanging and improve response times
3. **Data Limitation**: Limited patient results to 10 patients for better performance and faster API responses

#### 🚀 **New Features:**
1. **Enhanced Patient Data**: Added comprehensive patient information including:
   - Trimester calculation (1st, 2nd, 3rd)
   - Age group classification (optimal/outside_optimal)
   - Detailed medication information with NDC codes
   - Complete medical conditions and ICD10 codes
   - Contact information and timestamps

2. **Performance Optimizations**:
   - Limited API responses to 10 patients for faster loading
   - Added caching for weather data (when enabled)
   - Reduced timeout values for external API calls
   - Fallback data when external services are unavailable

3. **Improved API Responses**:
   - Added `total_available_patients` field to show actual patient count
   - Added `patients_limited_to` field to indicate performance limitation
   - Enhanced error handling and logging

#### 📊 **Current API Status:**
- **Weather API**: Temporarily disabled (returns default values)
- **AI Suggestions**: Available (requires GEMINI_API_KEY)
- **Patient Data**: Full 1000 patients available, API returns first 10
- **Risk Assessment**: Fully functional with comprehensive scoring

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

2. **Weather data**: Currently disabled for performance. Returns default values to prevent API hanging.

3. **Patient Data Limitation**: API returns only first 10 patients for optimal performance. Use individual patient endpoints for specific data.

4. **Filtering**: All endpoints support filtering by various parameters (risk_level, location, etc.).

5. **Comprehensive Patient Information**: Each patient response includes:
   - Complete medical history and conditions
   - Detailed medication information with NDC codes
   - Pregnancy details with trimester calculation
   - Risk assessment with detailed scoring
   - Contact information and timestamps

6. **Error handling**: All endpoints return structured responses with success/error information and detailed logging.

7. **Performance Optimized**: Fast response times with limited data sets for better user experience.

## Quick Start Examples

### Get Risk Patients (Basic)
```bash
curl "http://localhost:5000/api/risk-patients"
```

### Get Risk Patients with AI Suggestions
```bash
curl "http://localhost:5000/api/risk-patients?include_ai_suggestions=true"
```

### Get High-Risk Patients Only
```bash
curl "http://localhost:5000/api/risk-patients?risk_level=high"
```

### Get Risk Summary
```bash
curl "http://localhost:5000/api/risk-patients/summary"
```

### Get Specific Patient Details
```bash
curl "http://localhost:5000/api/risk-patients/1"
```

## Comprehensive Patient Data API

### Get All Patients with Risks and Recommendations
```bash
# Get all patients with comprehensive risk data (with pagination by default)
curl "http://localhost:5000/api/patients/with-risks"

# Get ALL patients without pagination (processes all patients first, then returns all)
curl "http://localhost:5000/api/patients/with-risks?no_pagination=true"

# With pagination
curl "http://localhost:5000/api/patients/with-risks?page=1&per_page=20"

# Filter by risk level (processes all patients, then filters)
curl "http://localhost:5000/api/patients/with-risks?risk_level=high"

# Filter by location (zip code)
curl "http://localhost:5000/api/patients/with-risks?location=10001"

# Include AI suggestions (default: true)
curl "http://localhost:5000/api/patients/with-risks?include_ai_suggestions=true"

# Include notifications (default: true)
curl "http://localhost:5000/api/patients/with-risks?include_notifications=true"

# Combined filters with all patients
curl "http://localhost:5000/api/patients/with-risks?risk_level=medium&location=10001&no_pagination=true"

# Combined filters with pagination
curl "http://localhost:5000/api/patients/with-risks?risk_level=medium&location=10001&page=1&per_page=10"
```

### Stream All Patients with Risks (Real-time Processing)
```bash
# Stream all patients with comprehensive risk data (real-time processing)
curl "http://localhost:5000/api/patients/with-risks/stream"

# Stream with custom batch size (default: 10 patients per batch)
curl "http://localhost:5000/api/patients/with-risks/stream?batch_size=5"

# Stream with filters
curl "http://localhost:5000/api/patients/with-risks/stream?risk_level=high&batch_size=20"

# Stream by location
curl "http://localhost:5000/api/patients/with-risks/stream?location=10001&batch_size=15"

# Stream without AI suggestions for faster processing
curl "http://localhost:5000/api/patients/with-risks/stream?include_ai_suggestions=false&batch_size=25"
```

### Get Comprehensive Patient Statistics
```bash
# Get basic statistics
curl "http://localhost:5000/api/patients/statistics"

# Get detailed breakdown including medications and conditions
curl "http://localhost:5000/api/patients/statistics?include_detailed_breakdown=true"

# Filter by location
curl "http://localhost:5000/api/patients/statistics?location=10001"

# Combined filters
curl "http://localhost:5000/api/patients/statistics?location=10001&include_detailed_breakdown=true"
```

### Response Examples

#### Patients with Risks Response
```json
{
  "success": true,
  "patients": [
    {
      "patient_id": 1,
      "name": "Jane Doe",
      "age": 28,
      "zip_code": "10001",
      "phone_number": "+1234567890",
      "email": "jane@example.com",
      "address": "123 Main St",
      "pregnancy_weeks": 24,
      "trimester": 2,
      "pregnancy_icd10": "Z34.90",
      "pregnancy_description": "Encounter for supervision of normal pregnancy",
      "comorbidity_icd10": "E11.9",
      "comorbidity_description": "Type 2 diabetes mellitus without complications",
      "conditions": [
        "Z34.90: Encounter for supervision of normal pregnancy",
        "E11.9: Type 2 diabetes mellitus without complications"
      ],
      "medications": ["Metformin", "Folic Acid"],
      "medication_notes": "Take with food",
      "ndc_codes": ["12345-678-90", "98765-432-10"],
      "risk_level": "medium",
      "risk_score": 6.5,
      "heat_wave_risk": false,
      "risk_factors": {
        "age_risk": "low",
        "trimester_risk": "medium",
        "location_risk": "low",
        "conditions_risk": "high",
        "medications_risk": "low"
      },
      "weather_conditions": {
        "temperature": 25,
        "feels_like": 25,
        "humidity": 50,
        "description": "Weather API disabled"
      },
      "is_high_risk_age": true,
      "age_group": "optimal",
      "ai_suggestions": {
        "recommendations": [
          "Monitor blood sugar levels closely",
          "Regular prenatal check-ups recommended",
          "Follow diabetic diet guidelines"
        ],
        "priority_actions": [
          "Schedule endocrinologist consultation",
          "Monitor fetal development"
        ]
      },
      "notifications": [
        {
          "id": 1,
          "message": "Regular check-up reminder",
          "notification_type": "reminder",
          "priority": "medium",
          "status": "sent"
        }
      ],
      "risk_history": [
        {
          "id": 1,
          "risk_level": "medium",
          "risk_score": 6.5,
          "assessment_date": "2024-01-15T10:30:00"
        }
      ],
      "created_at": "2024-01-01T00:00:00",
      "updated_at": "2024-01-15T10:30:00"
    }
  ],
  "pagination": {
    "total": 100,
    "pages": 5,
    "current_page": 1,
    "per_page": 20,
    "has_next": true,
    "has_prev": false
  },
  "summary": {
    "total_patients": 20,
    "total_processed_patients": 100,
    "total_available_patients": 100,
    "risk_distribution": {
      "low": 5,
      "medium": 12,
      "high": 3
    },
    "patients_at_risk": 15,
    "filters_applied": {
      "risk_level": null,
      "location": null,
      "include_ai_suggestions": true,
      "include_notifications": true,
      "no_pagination": false
    }
  }
}
```

#### Streaming Response Examples

The streaming API returns data in NDJSON format (newline-delimited JSON), where each line is a separate JSON object:

**Initial Metadata:**
```json
{"type": "metadata", "total_patients": 1000, "batch_size": 10, "filters_applied": {"risk_level": null, "location": null, "include_ai_suggestions": true, "include_notifications": true}}
```

**Patient Batch:**
```json
{"type": "batch", "patients": [{"patient_id": 1, "name": "Jane Doe", "age": 28, "risk_level": "medium", "risk_score": 6.5, "ai_suggestions": {"recommendations": ["Monitor blood sugar levels"]}, {"patient_id": 2, "name": "John Smith", "age": 32, "risk_level": "high", "risk_score": 8.2, "ai_suggestions": {"recommendations": ["Immediate consultation needed"]}}], "processed_count": 10, "total_patients": 1000}
```

**Final Summary:**
```json
{"type": "summary", "total_processed": 1000, "total_available_patients": 1000, "risk_distribution": {"low": 300, "medium": 500, "high": 200}, "patients_at_risk": 700, "filters_applied": {"risk_level": null, "location": null, "include_ai_suggestions": true, "include_notifications": true}}
```

**Error Response:**
```json
{"type": "error", "error": "Failed to generate patient stream"}
```

#### Statistics Response
```json
{
  "success": true,
  "statistics": {
    "total_patients": 100,
    "risk_distribution": {
      "low": 30,
      "medium": 50,
      "high": 20
    },
    "risk_percentages": {
      "low": 30.0,
      "medium": 50.0,
      "high": 20.0
    },
    "patients_at_risk": 70,
    "patients_at_risk_percentage": 70.0,
    "extreme_heat_risk": 15,
    "extreme_heat_risk_percentage": 15.0,
    "average_risk_score": 5.8,
    "age_distribution": {
      "under_21": 10,
      "21_30": 40,
      "31_35": 35,
      "over_35": 15
    },
    "age_percentages": {
      "under_21": 10.0,
      "21_30": 40.0,
      "31_35": 35.0,
      "over_35": 15.0
    },
    "trimester_distribution": {
      "1": 25,
      "2": 35,
      "3": 30,
      "unknown": 10
    },
    "trimester_percentages": {
      "1": 25.0,
      "2": 35.0,
      "3": 30.0,
      "unknown": 10.0
    },
    "medication_risks": {
      "Metformin": {
        "count": 15,
        "risk_levels": {
          "low": 5,
          "medium": 8,
          "high": 2
        }
      },
      "Folic Acid": {
        "count": 80,
        "risk_levels": {
          "low": 60,
          "medium": 18,
          "high": 2
        }
      }
    },
    "condition_risks": {
      "Z34.90: Encounter for supervision of normal pregnancy": {
        "count": 90,
        "risk_levels": {
          "low": 30,
          "medium": 45,
          "high": 15
        }
      }
    },
    "top_medications": [
      ["Folic Acid", {"count": 80, "risk_levels": {"low": 60, "medium": 18, "high": 2}}],
      ["Metformin", {"count": 15, "risk_levels": {"low": 5, "medium": 8, "high": 2}}]
    ],
    "top_conditions": [
      ["Z34.90: Encounter for supervision of normal pregnancy", {"count": 90, "risk_levels": {"low": 30, "medium": 45, "high": 15}}]
    ],
    "filters_applied": {
      "location": null,
      "include_detailed_breakdown": true
    }
  }
}
```
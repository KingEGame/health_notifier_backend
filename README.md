# Health Notification System for Pregnant Women

A comprehensive health monitoring system for pregnant women with climate data integration, risk assessment, and personalized notifications.

## Key Features

- **Patient Management**: Complete CRUD operations for patient records with detailed medical data
- **Risk Assessment**: AI-powered risk evaluation based on multiple factors
- **Weather Integration**: Real-time weather data and heat wave detection
- **Personalized Notifications**: AI-generated health advice in Russian
- **REST API**: Complete RESTful API for all operations
- **Database Support**: MySQL database
- **Data Import**: Bulk import of patients from CSV files

## Patient Data Structure

### New Fields (Updated Model)

- **name** (string): Patient name
- **age** (integer): Age (17-45 years)
- **pregnancy_icd10** (string): ICD-10 pregnancy code
- **pregnancy_description** (string): Pregnancy condition description
- **comorbidity_icd10** (string): ICD-10 comorbidity code
- **comorbidity_description** (string): Comorbidity description
- **weeks_pregnant** (integer): Weeks of pregnancy (1-42)
- **address** (string): Patient address
- **zip_code** (string): ZIP code
- **phone_number** (string): Phone number
- **email** (string): Email address

### Backward Compatibility

The system supports old fields for backward compatibility:
- **conditions_icd10** (array): Array of ICD-10 codes
- **trimester** (integer): Pregnancy trimester (1-3)

Trimester is automatically calculated from `weeks_pregnant`:
- 1-12 weeks = 1st trimester
- 13-24 weeks = 2nd trimester  
- 25-42 weeks = 3rd trimester

## Risk Assessment Factors

The system evaluates risk based on:

1. **Age Factor**:
   - 17-20 years: High risk
   - 21-30 years: Medium risk
   - 31-35 years: High risk

2. **Trimester Factor**:
   - 1st trimester: Medium risk
   - 2nd trimester: Low risk
   - 3rd trimester: High risk

3. **Geographic/Location Factor**:
   - Heat wave conditions: High risk
   - Temperature > 30°C: Medium risk
   - Normal conditions: Low risk

4. **Medical Conditions (ICD10)**:
   - Multiple high-risk conditions: High risk
   - Single high-risk condition: Medium risk
   - No high-risk conditions: Low risk

## API Endpoints

### Patient Management
- `POST /api/patients` - Create new patient
- `GET /api/patients/{id}` - Get patient by ID
- `PUT /api/patients/{id}` - Update patient
- `DELETE /api/patients/{id}` - Delete patient
- `GET /api/patients` - Get all patients (paginated)

### Risk Assessment
- `POST /api/assess-risk/{patient_id}` - Assess patient risk
- `GET /api/risk/{patient_id}` - Get latest risk assessment
- `GET /api/risk/{patient_id}/history` - Get risk assessment history

### Notifications
- `GET /api/notifications/{patient_id}` - Get patient notifications
- `POST /api/notifications/mark-read/{id}` - Mark notification as read
- `POST /api/notifications/{patient_id}/mark-all-read` - Mark all as read

### System
- `GET /api/health` - Health check
- `GET /api/weather/{zip_code}` - Get weather data

## Installation and Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**:
   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

3. **Create MySQL database**:
   ```sql
   CREATE DATABASE health_notifier;
   ```

4. **Run the application**:
   ```bash
   python main.py
   ```

## Environment Variables

Create a `.env` file with the following variables:

```env
# Database settings
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=health_notifier

# External APIs
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.0-flash-exp
WEATHER_API_KEY=your_weather_key

# Application settings
FLASK_ENV=development
SECRET_KEY=your_secret_key
FLASK_DEBUG=True
```

### How to get API keys:

1. **Gemini API Key**:
   - Go to https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy the key to `GEMINI_API_KEY` variable

2. **Gemini Model Configuration**:
   - Set `GEMINI_MODEL` to choose the AI model:
     - `gemini-2.0-flash-exp` (default) - Latest experimental model
     - `gemini-1.5-pro` - Pro model with advanced capabilities
     - `gemini-1.5-flash` - Fast model for quick responses
     - `gemini-pro` - Standard model (legacy)

3. **Weather API Key**:
   - Register at https://openweathermap.org/api
   - Get a free API key
   - Copy the key to `WEATHER_API_KEY` variable

## Usage Examples

### Creating a patient with new fields

```bash
curl -X POST http://localhost:5000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Anna Petrova",
    "age": 28,
    "pregnancy_icd10": "O24.4",
    "pregnancy_description": "Gestational diabetes mellitus",
    "comorbidity_icd10": "I10",
    "comorbidity_description": "Essential hypertension",
    "weeks_pregnant": 20,
    "address": "123 Main St, Moscow",
    "zip_code": "101000",
    "phone_number": "+7-999-123-45-67",
    "email": "anna@example.com"
  }'
```

### CSV data import

```bash
# Import 1000 patients from CSV file
python import_patients.py

# Or specify a file
python import_patients.py synthetic_pregnant_patients_1000.csv
```

### Existing database migration

```bash
# Update schema for existing databases
python migrate_patient_schema.py
```

## Database Schema

### Patients Table
- `id` - Primary key
- `name` - Patient name
- `age` - Patient age (17-45)
- `pregnancy_icd10` - ICD-10 code for pregnancy condition
- `pregnancy_description` - Description of pregnancy condition
- `comorbidity_icd10` - ICD-10 code for comorbidity
- `comorbidity_description` - Description of comorbidity
- `weeks_pregnant` - Weeks of pregnancy (1-42)
- `address` - Patient address
- `zip_code` - ZIP code for weather data
- `phone_number` - Phone number
- `email` - Email address
- `created_at` - Record creation timestamp
- `updated_at` - Record update timestamp

### Risk Assessments Table
- `id` - Primary key
- `patient_id` - Foreign key to patients
- `risk_level` - Risk level (low, medium, high)
- `heat_wave_risk` - Boolean heat wave risk
- `risk_factors` - JSON object of risk factors
- `risk_score` - Numeric risk score
- `weather_data` - JSON object of weather data
- `assessment_date` - Assessment timestamp

### Notifications Table
- `id` - Primary key
- `patient_id` - Foreign key to patients
- `message` - Notification message
- `risk_level` - Associated risk level
- `notification_type` - Type of notification
- `sent_at` - Sent timestamp
- `read_status` - Read status
- `read_at` - Read timestamp

## Example Usage

### Create a Patient
```bash
curl -X POST http://localhost:5000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Maria Ivanova",
    "age": 28,
    "geo_location": "Moscow",
    "zip_code": "101000",
    "conditions_icd10": ["O24.4", "O13"],
    "trimester": 2,
    "phone_number": "+7-999-123-45-67",
    "email": "maria@example.com"
  }'
```

### Assess Risk
```bash
curl -X POST http://localhost:5000/api/assess-risk/1
```

### Get Notifications
```bash
curl http://localhost:5000/api/notifications/1
```

## External API Integration

### Weather API (OpenWeatherMap)
- Real-time weather data by ZIP code
- Heat wave detection
- Temperature and humidity monitoring

### Gemini API
- Personalized health messages in Russian
- Context-aware recommendations
- Risk-specific advice generation

## High-Risk ICD10 Codes

The system recognizes the following high-risk pregnancy-related ICD10 codes:
- O24.4 - Gestational diabetes mellitus
- O13 - Gestational hypertension
- O14 - Pre-eclampsia
- O15 - Eclampsia
- And many more pregnancy-related conditions

## Development

### Running in Development Mode
```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python main.py
```

### Database Migrations
```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Description"

# Apply migration
flask db upgrade
```

## Testing

Test the API endpoints using curl or any REST client:

```bash
# Health check
curl http://localhost:5000/api/health

# Weather data
curl http://localhost:5000/api/weather/101000
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions, please contact the development team or create an issue in the repository.

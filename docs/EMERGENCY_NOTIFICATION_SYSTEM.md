# 🚨 Emergency Notification System with Three Risk Levels

## 📋 Overview

The Health Notifier system now supports three risk levels with automatic actions:

- **🟢 Low Risk**: Standard patient notifications
- **🟡 Medium Risk**: Enhanced notifications with recommendations
- **🔴 High Risk**: Automatic doctor call + emergency notifications

## 🎯 Three Risk Levels

### 🟢 Low Risk
**Criteria:**
- Age: 21-30 years
- Trimester: 2nd trimester
- Medical conditions: None or low risk

**Actions:**
- Standard patient notification
- General health recommendations
- Condition monitoring

### 🟡 Medium Risk
**Criteria:**
- Age: 25-30 years OR 1st trimester
- Medical conditions: One medium-risk condition

**Actions:**
- Enhanced patient notification
- Clinic visit recommendations
- Enhanced monitoring

### 🔴 High Risk
**Criteria:**
- Age: ≤20 years OR ≥35 years
- Trimester: 3rd trimester
- Medical conditions: High risk (O24, O13, O14, O10, O99.4)

**Actions:**
- **Automatic doctor call** 🚨
- Emergency notification to nearest hospital
- Patient notification about urgent consultation need
- Priority service

## 🏥 Medical Facility Integration

### Facility Types
- **HOSP**: Hospitals
- **NH**: Nursing homes
- **DTC**: Diagnostic centers
- **HOSP-EC**: Hospital clinics

### Automatic Search
- **High risk**: Search for nearest hospital
- **Medium risk**: Search for nearest clinic
- **Low risk**: Standard recommendations

## 🌐 API Endpoints

### Medical Facility Management
- `GET /api/health-facilities` - Get all facilities
- `GET /api/health-facilities/{id}` - Get facility by ID
- `GET /api/health-facilities/search?q=term` - Search facilities
- `GET /api/health-facilities/nearest?zip_code=12345` - Nearest facilities
- `GET /api/health-facilities/types` - Facility types

### Emergency Notifications
- `POST /api/emergency-notifications` - Create emergency notification
- `GET /api/emergency-notifications` - Get notifications
- `GET /api/emergency-notifications/{id}` - Get notification by ID
- `PUT /api/emergency-notifications/{id}/update` - Update status
- `POST /api/emergency-notifications/patient/{id}/assess` - Assess patient risk
- `GET /api/emergency-notifications/stats` - Notification statistics
- `GET /api/emergency-notifications/pending` - Pending notifications

## 📊 Usage Examples

### 1. Creating a High-Risk Patient

```bash
curl -X POST http://localhost:5000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "High Risk Patient",
    "age": 18,
    "pregnancy_icd10": "O24.4",
    "pregnancy_description": "Gestational diabetes mellitus",
    "comorbidity_icd10": "I10",
    "comorbidity_description": "Essential hypertension",
    "weeks_pregnant": 35,
    "address": "123 High Risk Street, Risk City",
    "zip_code": "10001",
    "phone_number": "+7-999-111-11-11",
    "email": "highrisk@example.com"
  }'
```

### 2. Risk Assessment and Notification Creation

```bash
curl -X POST http://localhost:5000/api/emergency-notifications/patient/1/assess
```

**Response for High Risk:**
```json
{
  "success": true,
  "risk_level": "high",
  "action_taken": "doctor_called",
  "hospital": {
    "id": 1,
    "facility_name": "Metropolitan Hospital Center",
    "facility_phone_number": "2124238993",
    "facility_address_1": "1901 First Avenue",
    "facility_city": "New York",
    "facility_state": "New York"
  },
  "emergency_notification_id": 1,
  "patient_message": "🚨 ATTENTION! You have high risk..."
}
```

### 3. Getting Notification Statistics

```bash
curl http://localhost:5000/api/emergency-notifications/stats
```

**Response:**
```json
{
  "success": true,
  "stats": {
    "status_counts": {
      "pending": 5,
      "sent": 12,
      "delivered": 8,
      "failed": 1
    },
    "risk_level_counts": {
      "low": 10,
      "medium": 8,
      "high": 3
    },
    "type_counts": {
      "patient_notification": 15,
      "doctor_call": 3,
      "emergency_alert": 2
    },
    "recent_notifications_24h": 5,
    "total_notifications": 20
  }
}
```

## 🔧 Setup and Deployment

### 1. Import Medical Facilities

```bash
# Import facilities from CSV
python import_health_facilities.py

# Or specify a file
python import_health_facilities.py Health_Facility_General_Information_20250920.csv
```

### 2. Import Patients

```bash
# Import patients from CSV
python import_patients.py
```

### 3. System Testing

```bash
# Test emergency notifications
python test_emergency_notifications.py

# Test new patient fields
python test_new_patient_fields.py
```

## 📈 Monitoring and Statistics

### Key Metrics
- **Number of notifications by risk level**
- **Notification delivery status**
- **Medical facility response time**
- **Early warning system effectiveness**

### Dashboard
- Total patients by risk level
- Active emergency notifications
- Medical facility statistics
- Trends and analytics

## 🚨 Emergency Notification Process

### High Risk - Automatic Doctor Call

1. **High Risk Detection**
   - System analyzes patient data
   - Determines high risk level
   - Initiates emergency notification

2. **Find Nearest Hospital**
   - Search by patient ZIP code
   - Filter by facility type (HOSP)
   - Select facility with working phone

3. **Create Emergency Notification**
   - Generate detailed message
   - Set priority to "critical"
   - Link with patient and hospital

4. **Send Notification**
   - Call hospital
   - SMS/Email notification
   - Log all actions

5. **Track Status**
   - Mark delivery
   - Get response from hospital
   - Update patient status

## 🔒 Security and Privacy

### Data Protection
- Personal data encryption
- Secure notification transmission
- Action logging
- HIPAA compliance (if needed)

### Access Control
- User roles
- Notification access rights
- Action auditing
- Backup

## 📞 Integrations

### External Services
- **SMS Gateway**: SMS notifications
- **Email Service**: Email notifications
- **Voice API**: Automatic calls
- **Hospital Systems**: Hospital system integration

### API Integrations
- **Emergency Services**: Emergency services
- **Weather API**: Weather data
- **Geolocation API**: Location detection
- **Notification Services**: Notification services

## 🎯 System Benefits

### For Patients
- **Early warning** about risks
- **Personalized recommendations**
- **Quick help** for high risk
- **Continuous monitoring**

### For Medical Facilities
- **Automatic notifications** about critical cases
- **Detailed information** about patients
- **Prioritization** of requests
- **Integration** with existing systems

### For Healthcare System
- **Reduction** in complications
- **Improvement** in medical care quality
- **Resource optimization**
- **Analytics** and reporting

---

**🚨 System ready for use! Start with data import and API endpoint testing.**

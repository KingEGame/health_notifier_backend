# 🔄 Migration Guide - Patient Fields Update

## Changes Overview

The `Patient` model has been updated to support more detailed medical data in accordance with the `synthetic_pregnant_patients_1000.csv` file.

### New Fields

| Field | Type | Description |
|------|-----|----------|
| `pregnancy_icd10` | VARCHAR(20) | ICD-10 pregnancy code |
| `pregnancy_description` | TEXT | Pregnancy condition description |
| `comorbidity_icd10` | VARCHAR(20) | ICD-10 comorbidity code |
| `comorbidity_description` | TEXT | Comorbidity description |
| `weeks_pregnant` | INT | Weeks of pregnancy (1-42) |
| `address` | TEXT | Patient address |

### Removed Fields

| Field | Replacement |
|------|--------|
| `geo_location` | `address` |
| `conditions_icd10` | `pregnancy_icd10` + `comorbidity_icd10` |
| `trimester` | Automatically calculated from `weeks_pregnant` |

## Existing Data Migration

### 1. Automatic Schema Migration

```bash
# Run migration script
python migrate_patient_schema.py
```

This script will:
- Add new columns to the `patients` table
- Create necessary indexes
- Preserve existing data

### 2. Manual Data Migration

If you have existing data that needs to be migrated:

```python
# Example script for data migration
from app import create_app, db
from app.models.patient import Patient

app = create_app()
with app.app_context():
    patients = Patient.query.all()
    
    for patient in patients:
        # Migrate geo_location to address
        if hasattr(patient, 'geo_location') and patient.geo_location:
            patient.address = patient.geo_location
        
        # Migrate conditions_icd10
        if hasattr(patient, 'conditions_icd10') and patient.conditions_icd10:
            conditions = patient.get_conditions()
            if conditions:
                patient.pregnancy_icd10 = conditions[0] if len(conditions) > 0 else None
                patient.comorbidity_icd10 = conditions[1] if len(conditions) > 1 else None
        
        # Calculate weeks_pregnant from trimester
        if hasattr(patient, 'trimester') and patient.trimester:
            if patient.trimester == 1:
                patient.weeks_pregnant = 8  # Average value for 1st trimester
            elif patient.trimester == 2:
                patient.weeks_pregnant = 18  # Average value for 2nd trimester
            elif patient.trimester == 3:
                patient.weeks_pregnant = 32  # Average value for 3rd trimester
    
    db.session.commit()
```

## New Data Import

### 1. CSV File Import

```bash
# Import 1000 patients from CSV
python import_patients.py

# Or specify a file
python import_patients.py synthetic_pregnant_patients_1000.csv
```

### 2. Creating New Patients via API

```bash
# New format
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
    "zip_code": "101000"
  }'
```

## Backward Compatibility

The system supports old fields for backward compatibility:

### API Endpoints

- `conditions_icd10` - automatically converted to `pregnancy_icd10` + `comorbidity_icd10`
- `trimester` - automatically calculated from `weeks_pregnant`

### Examples

```bash
# Old format (still works)
curl -X POST http://localhost:5000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Elena Smirnova",
    "age": 32,
    "zip_code": "190000",
    "conditions_icd10": ["O13", "I10"],
    "trimester": 3
  }'
```

## Testing

### 1. Test New Fields

```bash
python test_new_patient_fields.py
```

### 2. Test Backward Compatibility

```bash
python test_simple.py
```

## Code Updates

### 1. Patient Model

```python
# New methods
patient.get_trimester()  # Calculates trimester from weeks_pregnant
patient.get_conditions()  # Returns array of all ICD-10 codes
```

### 2. API Responses

```json
{
  "id": 1,
  "name": "Anna Petrova",
  "age": 28,
  "pregnancy_icd10": "O24.4",
  "pregnancy_description": "Gestational diabetes mellitus",
  "comorbidity_icd10": "I10",
  "comorbidity_description": "Essential hypertension",
  "weeks_pregnant": 20,
  "address": "123 Main St, Moscow",
  "zip_code": "101000",
  "trimester": 2,  // Automatically calculated
  "conditions_icd10": ["O24.4", "I10"]  // For backward compatibility
}
```

## Migration Verification

### 1. Database Schema Check

```sql
DESCRIBE patients;
```

### 2. Data Check

```python
from app import create_app, db
from app.models.patient import Patient

app = create_app()
with app.app_context():
    patients = Patient.query.limit(5).all()
    for patient in patients:
        print(f"Patient: {patient.name}")
        print(f"  Pregnancy: {patient.pregnancy_icd10} - {patient.pregnancy_description}")
        print(f"  Comorbidity: {patient.comorbidity_icd10} - {patient.comorbidity_description}")
        print(f"  Weeks: {patient.weeks_pregnant}, Trimester: {patient.get_trimester()}")
        print()
```

## Rollback Changes

If you need to rollback changes:

```sql
-- Remove new columns
ALTER TABLE patients DROP COLUMN pregnancy_icd10;
ALTER TABLE patients DROP COLUMN pregnancy_description;
ALTER TABLE patients DROP COLUMN comorbidity_icd10;
ALTER TABLE patients DROP COLUMN comorbidity_description;
ALTER TABLE patients DROP COLUMN weeks_pregnant;
ALTER TABLE patients DROP COLUMN address;

-- Restore old columns
ALTER TABLE patients ADD COLUMN geo_location VARCHAR(100);
ALTER TABLE patients ADD COLUMN conditions_icd10 TEXT;
ALTER TABLE patients ADD COLUMN trimester INT;
```

## Support

If you encounter migration issues:

1. Check application logs
2. Ensure database is accessible
3. Check database access permissions
4. Create an issue in the project repository

---

**Important**: Make a database backup before migration!

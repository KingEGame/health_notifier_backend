#!/usr/bin/env python3
"""
Script to import patient data from CSV file with medications and NDC codes
"""

import os
import sys
import pandas as pd
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from health_notifier.app import create_app, db
from health_notifier.app.models.patient import Patient

def import_patients_from_csv(csv_file_path):
    """Import patients from CSV file with medications and NDC codes"""
    
    # Create Flask app context
    app = create_app()
    
    with app.app_context():
        # Create tables if they don't exist
        db.create_all()
        
        # Read CSV file
        try:
            df = pd.read_csv(csv_file_path)
            print(f"Successfully loaded CSV file: {csv_file_path}")
            print(f"Total rows: {len(df)}")
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            return
        
        # Check required columns
        required_columns = [
            'Name', 'Age', 'Pregnancy ICD-10', 'Pregnancy Description',
            'Comorbidity ICD-10', 'Comorbidity Description', 'Weeks Pregnant',
            'Address', 'ZIP Code', 'Medications', 'Medication Notes',
            'NDC Codes', 'Between 17-35'
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"Missing required columns: {missing_columns}")
            return
        
        # Import patients
        imported_count = 0
        error_count = 0
        
        for index, row in df.iterrows():
            try:
                # Create patient object
                patient = Patient(
                    name=row['Name'],
                    age=int(row['Age']),
                    pregnancy_icd10=row['Pregnancy ICD-10'] if pd.notna(row['Pregnancy ICD-10']) else None,
                    pregnancy_description=row['Pregnancy Description'] if pd.notna(row['Pregnancy Description']) else None,
                    comorbidity_icd10=row['Comorbidity ICD-10'] if pd.notna(row['Comorbidity ICD-10']) else None,
                    comorbidity_description=row['Comorbidity Description'] if pd.notna(row['Comorbidity Description']) else None,
                    weeks_pregnant=int(row['Weeks Pregnant']) if pd.notna(row['Weeks Pregnant']) else None,
                    address=row['Address'] if pd.notna(row['Address']) else None,
                    zip_code=str(row['ZIP Code']),
                    medications=row['Medications'] if pd.notna(row['Medications']) else None,
                    medication_notes=row['Medication Notes'] if pd.notna(row['Medication Notes']) else None,
                    ndc_codes=row['NDC Codes'] if pd.notna(row['NDC Codes']) else None,
                    between_17_35=bool(row['Between 17-35']) if pd.notna(row['Between 17-35']) else False
                )
                
                # Add to database
                db.session.add(patient)
                imported_count += 1
                
                # Commit every 100 patients
                if imported_count % 100 == 0:
                    db.session.commit()
                    print(f"Imported {imported_count} patients...")
                    
            except Exception as e:
                print(f"Error importing patient {index + 1}: {e}")
                error_count += 1
                continue
        
        # Final commit
        try:
            db.session.commit()
            print(f"\nImport completed!")
            print(f"Successfully imported: {imported_count} patients")
            print(f"Errors: {error_count} patients")
            
            # Show some statistics
            print(f"\nStatistics:")
            print(f"Total patients in database: {Patient.query.count()}")
            
            # Age distribution
            age_stats = db.session.query(
                db.func.min(Patient.age).label('min_age'),
                db.func.max(Patient.age).label('max_age'),
                db.func.avg(Patient.age).label('avg_age')
            ).first()
            print(f"Age range: {age_stats.min_age} - {age_stats.max_age} (avg: {age_stats.avg_age:.1f})")
            
            # Risk age distribution
            high_risk_age_count = Patient.query.filter(Patient.between_17_35 == False).count()
            optimal_age_count = Patient.query.filter(Patient.between_17_35 == True).count()
            print(f"High-risk age (outside 17-35): {high_risk_age_count} patients")
            print(f"Optimal age (17-35): {optimal_age_count} patients")
            
            # Medications statistics
            patients_with_meds = Patient.query.filter(Patient.medications.isnot(None)).count()
            print(f"Patients with medications: {patients_with_meds} patients")
            
        except Exception as e:
            print(f"Error committing to database: {e}")
            db.session.rollback()

def main():
    """Main function"""
    csv_file = 'synthetic_pregnant_patients_1000_with_meds_ndc.csv'
    
    if not os.path.exists(csv_file):
        print(f"CSV file not found: {csv_file}")
        print("Please make sure the file is in the current directory")
        return
    
    print("Starting patient import with medications and NDC codes...")
    print(f"CSV file: {csv_file}")
    
    import_patients_from_csv(csv_file)

if __name__ == '__main__':
    main()
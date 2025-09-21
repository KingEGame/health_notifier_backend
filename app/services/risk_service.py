from app.services.weather_service import WeatherService
from app.utils.exceptions import ExternalAPIException

class RiskAssessmentService:
    """Service for risk assessment logic"""
    
    # ICD10 codes that increase pregnancy risk (based on real data analysis)
    HIGH_RISK_PREGNANCY_CODES = {
        'O24.4': 'Gestational diabetes mellitus',
        'O13': 'Gestational hypertension', 
        'O14': 'Pre-eclampsia',
        'O15': 'Eclampsia',
        'O16': 'Unspecified maternal hypertension',
        'O26.2': 'Pregnancy care for abnormal findings',
        'O26.9': 'Pregnancy-related condition, unspecified',
        'O36.5': 'Maternal care for poor fetal growth',
        'O09.3': 'Supervision of high-risk pregnancy, multigravida',
        'O09.5': 'Supervision of elderly primigravida'
    }
    
    # High-risk comorbidity codes (based on real data analysis)
    HIGH_RISK_COMORBIDITY_CODES = {
        'I10': 'Essential hypertension',
        'E11.9': 'Type 2 diabetes mellitus without complications',
        'E03.9': 'Hypothyroidism, unspecified',
        'J45.9': 'Asthma, unspecified',
        'D50.9': 'Iron deficiency anemia, unspecified',
        'E66.9': 'Obesity, unspecified'
    }
    
    # Medium-risk comorbidity codes
    MEDIUM_RISK_COMORBIDITY_CODES = {
        'E66.0': 'Obesity due to excess calories',
        'E66.01': 'Morbid obesity due to excess calories',
        'E66.09': 'Other obesity due to excess calories',
        'D50.0': 'Iron deficiency anemia secondary to blood loss',
        'D50.8': 'Other iron deficiency anemias',
        'J45.0': 'Predominantly allergic asthma',
        'J45.1': 'Nonallergic asthma',
        'J45.8': 'Mixed asthma',
        'J45.9': 'Unspecified asthma'
    }
    
    # High-risk medications (require close monitoring)
    HIGH_RISK_MEDICATIONS = {
        'Insulin': 'Diabetes management - requires close monitoring',
        'Labetalol': 'Hypertension management - blood pressure monitoring needed',
        'Metformin': 'Diabetes management - kidney function monitoring',
        'Warfarin': 'Anticoagulant - bleeding risk',
        'Phenytoin': 'Antiepileptic - teratogenic risk',
        'Lithium': 'Mood stabilizer - teratogenic risk',
        'ACE inhibitors': 'Hypertension - contraindicated in pregnancy',
        'ARBs': 'Hypertension - contraindicated in pregnancy'
    }
    
    # Medium-risk medications
    MEDIUM_RISK_MEDICATIONS = {
        'Levothyroxine': 'Thyroid hormone - requires dose adjustment',
        'Ferrous sulfate': 'Iron supplementation - GI side effects',
        'Folic acid': 'Prenatal vitamin - generally safe',
        'Calcium': 'Mineral supplement - generally safe',
        'Vitamin D': 'Vitamin supplement - generally safe'
    }
    
    @staticmethod
    def assess_risk(patient):
        """Assess risk for a patient based on multiple factors"""
        risk_score = 0
        factors = {}
        
        # Age factor
        age_risk = RiskAssessmentService._calculate_age_risk(patient.age)
        risk_score += age_risk['score']
        factors['age_risk'] = age_risk['level']
        
        # Trimester factor
        trimester_risk = RiskAssessmentService._calculate_trimester_risk(patient._calculate_trimester())
        risk_score += trimester_risk['score']
        factors['trimester_risk'] = trimester_risk['level']
        
        # Location factor (weather)
        try:
            weather_data = WeatherService.get_weather_data(patient.zip_code)
            location_risk = RiskAssessmentService._calculate_location_risk(weather_data)
            risk_score += location_risk['score']
            factors['location_risk'] = location_risk['level']
            factors['heat_wave'] = weather_data['is_heat_wave']
        except ExternalAPIException:
            # If weather service is unavailable, use medium risk
            risk_score += 1
            factors['location_risk'] = 'medium'
            factors['heat_wave'] = False
            weather_data = {
                'temperature': 25,
                'feels_like': 25,
                'humidity': 50,
                'pressure': 1013,
                'description': 'Unknown',
                'is_heat_wave': False,
                'heat_index': 25
            }
        
        # Conditions factor
        conditions_risk = RiskAssessmentService._calculate_conditions_risk(patient)
        risk_score += conditions_risk['score']
        factors['conditions_risk'] = conditions_risk['level']
        factors['conditions_details'] = conditions_risk['details']
        
        # Medications factor
        medications_risk = RiskAssessmentService._calculate_medications_risk(patient)
        risk_score += medications_risk['score']
        factors['medications_risk'] = medications_risk['level']
        factors['medications_details'] = medications_risk['details']
        
        # Age group factor (using between_17_35 flag)
        if hasattr(patient, 'between_17_35') and patient.between_17_35 is not None:
            age_group_risk = RiskAssessmentService._calculate_age_group_risk(patient.between_17_35)
            risk_score += age_group_risk['score']
            factors['age_group_risk'] = age_group_risk['level']
        
        # Determine final risk level (adjusted thresholds)
        if risk_score <= 3:
            risk_level = 'low'
        elif risk_score <= 5:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        return {
            'risk_level': risk_level,
            'risk_score': risk_score,
            'factors': factors,
            'heat_wave_risk': factors.get('heat_wave', False),
            'weather_data': weather_data
        }
    
    @staticmethod
    def _calculate_age_risk(age):
        """Calculate age-based risk score"""
        if 17 <= age <= 20 or 31 <= age <= 35:
            return {'score': 2, 'level': 'high'}
        elif 21 <= age <= 30:
            return {'score': 1, 'level': 'medium'}
        else:
            return {'score': 0, 'level': 'low'}
    
    @staticmethod
    def _calculate_trimester_risk(trimester):
        """Calculate trimester-based risk score"""
        if trimester == 3:
            return {'score': 2, 'level': 'high'}
        elif trimester == 1:
            return {'score': 1, 'level': 'medium'}
        else:  # trimester == 2
            return {'score': 0, 'level': 'low'}
    
    @staticmethod
    def _calculate_location_risk(weather_data):
        """Calculate location-based risk score with enhanced weather analysis"""
        temperature = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 50)
        heat_index = weather_data.get('heat_index', temperature)
        uv_index = weather_data.get('uv_index', 0)
        wind_speed = weather_data.get('wind_speed', 0)
        is_heat_wave = weather_data.get('is_heat_wave', False)
        
        risk_score = 0
        risk_details = []
        
        # Heat wave risk (highest priority)
        if is_heat_wave:
            risk_score += 3
            risk_details.append("Extreme heat wave conditions")
        elif temperature > 35:
            risk_score += 2
            risk_details.append("High temperature risk")
        elif temperature > 30:
            risk_score += 1
            risk_details.append("Moderate temperature risk")
        
        # Heat index risk
        if heat_index > 40:
            risk_score += 2
            risk_details.append("Dangerous heat index")
        elif heat_index > 35:
            risk_score += 1
            risk_details.append("Elevated heat index")
        
        # Humidity risk
        if humidity > 80:
            risk_score += 1
            risk_details.append("High humidity increases heat stress")
        elif humidity < 30:
            risk_score += 1
            risk_details.append("Low humidity may cause dehydration")
        
        # UV index risk
        if uv_index > 8:
            risk_score += 1
            risk_details.append("Very high UV exposure risk")
        elif uv_index > 6:
            risk_score += 0.5
            risk_details.append("High UV exposure risk")
        
        # Wind conditions (can help or hurt)
        if wind_speed > 15:  # Strong winds can be dangerous
            risk_score += 0.5
            risk_details.append("Strong winds may pose safety risk")
        elif wind_speed < 2 and temperature > 30:  # No wind relief in heat
            risk_score += 0.5
            risk_details.append("No wind relief from heat")
        
        # Determine risk level
        if risk_score >= 4:
            level = 'high'
        elif risk_score >= 2:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'score': risk_score,
            'level': level,
            'details': risk_details,
            'weather_factors': {
                'temperature': temperature,
                'heat_index': heat_index,
                'humidity': humidity,
                'uv_index': uv_index,
                'wind_speed': wind_speed,
                'is_heat_wave': is_heat_wave
            }
        }
    
    @staticmethod
    def get_comprehensive_risk_assessment(patient):
        """Get comprehensive risk assessment with detailed analysis"""
        try:
            # Get basic risk assessment
            risk_data = RiskAssessmentService.assess_risk(patient)
            
            # Get weather data
            weather_data = WeatherService.get_weather_data(patient.zip_code)
            
            # Calculate additional risk factors
            additional_factors = RiskAssessmentService._calculate_additional_risk_factors(patient, weather_data)
            
            # Combine all risk data
            comprehensive_risk = {
                'patient_id': patient.id,
                'patient_name': patient.name,
                'basic_risk': risk_data,
                'weather_analysis': {
                    'current_conditions': weather_data,
                    'risk_level': additional_factors['weather_risk']['level'],
                    'recommendations': additional_factors['weather_recommendations']
                },
                'overall_assessment': {
                    'risk_level': risk_data['risk_level'],
                    'risk_score': risk_data['risk_score'],
                    'priority_level': RiskAssessmentService._determine_priority_level(risk_data),
                    'immediate_concerns': additional_factors['immediate_concerns'],
                    'monitoring_needs': additional_factors['monitoring_needs']
                },
                'recommendations': additional_factors['general_recommendations']
            }
            
            return comprehensive_risk
            
        except Exception as e:
            logger.error(f"Error in comprehensive risk assessment: {e}")
            # Return basic assessment if comprehensive fails
            return {
                'patient_id': patient.id,
                'patient_name': patient.name,
                'basic_risk': RiskAssessmentService.assess_risk(patient),
                'error': 'Comprehensive assessment unavailable'
            }
    
    @staticmethod
    def _calculate_additional_risk_factors(patient, weather_data):
        """Calculate additional risk factors beyond basic assessment"""
        factors = {
            'weather_risk': {'level': 'low', 'score': 0},
            'weather_recommendations': [],
            'immediate_concerns': [],
            'monitoring_needs': [],
            'general_recommendations': []
        }
        
        # Weather-specific analysis
        temperature = weather_data.get('temperature', 25)
        humidity = weather_data.get('humidity', 50)
        is_heat_wave = weather_data.get('is_heat_wave', False)
        
        if is_heat_wave:
            factors['weather_risk'] = {'level': 'high', 'score': 3}
            factors['immediate_concerns'].append("Extreme heat wave conditions")
            factors['weather_recommendations'].extend([
                "Stay indoors with air conditioning",
                "Drink plenty of water",
                "Avoid outdoor activities",
                "Monitor for heat exhaustion symptoms"
            ])
        elif temperature > 35:
            factors['weather_risk'] = {'level': 'high', 'score': 2}
            factors['immediate_concerns'].append("High temperature risk")
            factors['weather_recommendations'].extend([
                "Limit outdoor exposure",
                "Stay hydrated",
                "Wear light, loose clothing"
            ])
        elif temperature > 30:
            factors['weather_risk'] = {'level': 'medium', 'score': 1}
            factors['weather_recommendations'].extend([
                "Take breaks in cool areas",
                "Stay hydrated",
                "Monitor for overheating"
            ])
        
        # Humidity considerations
        if humidity > 80:
            factors['weather_recommendations'].append("High humidity increases heat stress - take extra precautions")
        elif humidity < 30:
            factors['weather_recommendations'].append("Low humidity - ensure adequate hydration")
        
        # Patient-specific considerations
        if patient.weeks_pregnant:
            if patient.weeks_pregnant > 28:  # Third trimester
                factors['monitoring_needs'].append("Increased monitoring due to third trimester")
                factors['general_recommendations'].append("More frequent prenatal check-ups recommended")
            elif patient.weeks_pregnant < 12:  # First trimester
                factors['monitoring_needs'].append("Early pregnancy monitoring important")
                factors['general_recommendations'].append("Avoid extreme temperatures during early pregnancy")
        
        # Age considerations
        if patient.age < 18 or patient.age > 35:
            factors['monitoring_needs'].append("Age-related risk factors require closer monitoring")
            factors['general_recommendations'].append("Consider additional prenatal care due to age")
        
        # Medical conditions
        if patient.pregnancy_icd10 or patient.comorbidity_icd10:
            factors['monitoring_needs'].append("Medical conditions require specialized monitoring")
            factors['general_recommendations'].append("Follow medical provider's specific instructions")
        
        return factors
    
    @staticmethod
    def _determine_priority_level(risk_data):
        """Determine priority level for medical attention"""
        risk_score = risk_data.get('risk_score', 0)
        risk_level = risk_data.get('risk_level', 'low')
        heat_wave_risk = risk_data.get('heat_wave_risk', False)
        
        if risk_level == 'high' or heat_wave_risk or risk_score >= 6:
            return 'high'
        elif risk_level == 'medium' or risk_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    @staticmethod
    def _calculate_conditions_risk(patient):
        """Calculate risk based on pregnancy and comorbidity ICD10 conditions"""
        pregnancy_codes = []
        comorbidity_codes = []
        
        # Get pregnancy and comorbidity codes separately
        if hasattr(patient, 'pregnancy_icd10') and patient.pregnancy_icd10:
            pregnancy_codes.append(patient.pregnancy_icd10)
        if hasattr(patient, 'comorbidity_icd10') and patient.comorbidity_icd10:
            comorbidity_codes.append(patient.comorbidity_icd10)
        
        # Also check legacy conditions_icd10 for backward compatibility
        legacy_codes = patient.get_conditions() if hasattr(patient, 'get_conditions') else []
        for code in legacy_codes:
            if code.startswith('O'):
                pregnancy_codes.append(code)
            else:
                comorbidity_codes.append(code)
        
        risk_score = 0
        risk_details = []
        
        # Check pregnancy conditions
        for code in pregnancy_codes:
            if code in RiskAssessmentService.HIGH_RISK_PREGNANCY_CODES:
                risk_score += 2
                risk_details.append(f"High-risk pregnancy: {code}")
            elif code.startswith('O'):
                risk_score += 1
                risk_details.append(f"Pregnancy condition: {code}")
        
        # Check comorbidity conditions
        for code in comorbidity_codes:
            if code in RiskAssessmentService.HIGH_RISK_COMORBIDITY_CODES:
                risk_score += 2
                risk_details.append(f"High-risk comorbidity: {code}")
            elif code in RiskAssessmentService.MEDIUM_RISK_COMORBIDITY_CODES:
                risk_score += 1
                risk_details.append(f"Medium-risk comorbidity: {code}")
        
        # Determine risk level (adjusted thresholds for realistic distribution)
        if risk_score >= 6:
            level = 'high'
        elif risk_score >= 3:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'score': risk_score,
            'level': level,
            'details': risk_details,
            'pregnancy_codes': pregnancy_codes,
            'comorbidity_codes': comorbidity_codes
        }
    
    @staticmethod
    def _calculate_medications_risk(patient):
        """Calculate risk based on medications"""
        medications = []
        if hasattr(patient, 'get_medications_list'):
            medications = patient.get_medications_list()
        elif hasattr(patient, 'medications') and patient.medications:
            medications = [med.strip() for med in patient.medications.split(';') if med.strip()]
        
        risk_score = 0
        risk_details = []
        
        for medication in medications:
            # Check for high-risk medications
            for high_risk_med, description in RiskAssessmentService.HIGH_RISK_MEDICATIONS.items():
                if high_risk_med.lower() in medication.lower():
                    risk_score += 2
                    risk_details.append(f"High-risk medication: {medication} - {description}")
                    break
            else:
                # Check for medium-risk medications
                for medium_risk_med, description in RiskAssessmentService.MEDIUM_RISK_MEDICATIONS.items():
                    if medium_risk_med.lower() in medication.lower():
                        risk_score += 1
                        risk_details.append(f"Medium-risk medication: {medication} - {description}")
                        break
        
        # Determine risk level
        if risk_score >= 4:
            level = 'high'
        elif risk_score >= 2:
            level = 'medium'
        else:
            level = 'low'
        
        return {
            'score': risk_score,
            'level': level,
            'details': risk_details,
            'medications': medications
        }
    
    @staticmethod
    def _calculate_age_group_risk(between_17_35):
        """Calculate risk based on age group flag (17-35 years)"""
        if between_17_35:
            # Patient is in the optimal age range (17-35)
            return {
                'score': 0,
                'level': 'low',
                'details': ['Optimal age range (17-35 years)']
            }
        else:
            # Patient is outside optimal age range
            return {
                'score': 2,
                'level': 'high',
                'details': ['Outside optimal age range (17-35 years)']
            }

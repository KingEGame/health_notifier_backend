import re
from typing import List, Dict, Any

def validate_zip_code(zip_code: str) -> bool:
    """Validate zip code format"""
    us_zip_pattern = r'^\d{5}(-\d{4})?$'
    return bool(re.match(us_zip_pattern, zip_code))

def validate_email(email: str) -> bool:
    """Validate email format"""
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_pattern, email))

def validate_phone_number(phone: str) -> bool:
    """Validate phone number format"""
    digits_only = re.sub(r'\D', '', phone)
    return len(digits_only) in [10, 11]

def validate_icd10_code(code: str) -> bool:
    """Validate ICD10 code format"""
    icd10_pattern = r'^[A-Z]\d{2}(\.\d+)?$'
    return bool(re.match(icd10_pattern, code))

def validate_patient_data(data: Dict[str, Any]) -> List[str]:
    """Validate patient data and return list of errors"""
    errors = []
    
    # Required fields
    required_fields = ['name', 'age', 'geo_location', 'zip_code', 'trimester']
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f'Missing required field: {field}')
    
    # Validate age
    if 'age' in data:
        try:
            age = int(data['age'])
            if age < 15 or age > 50:
                errors.append('Age must be between 15 and 50')
        except (ValueError, TypeError):
            errors.append('Age must be a valid number')
    
    # Validate trimester
    if 'trimester' in data:
        try:
            trimester = int(data['trimester'])
            if trimester not in [1, 2, 3]:
                errors.append('Trimester must be 1, 2, or 3')
        except (ValueError, TypeError):
            errors.append('Trimester must be a valid number (1, 2, or 3)')
    
    # Validate zip code
    if 'zip_code' in data and not validate_zip_code(data['zip_code']):
        errors.append('Invalid zip code format')
    
    # Validate email
    if 'email' in data and data['email'] and not validate_email(data['email']):
        errors.append('Invalid email format')
    
    # Validate phone number
    if 'phone_number' in data and data['phone_number'] and not validate_phone_number(data['phone_number']):
        errors.append('Invalid phone number format')
    
    # Validate ICD10 codes
    if 'conditions_icd10' in data and data['conditions_icd10']:
        if not isinstance(data['conditions_icd10'], list):
            errors.append('ICD10 conditions must be a list')
        else:
            for code in data['conditions_icd10']:
                if not validate_icd10_code(code):
                    errors.append(f'Invalid ICD10 code format: {code}')
    
    return errors

def format_risk_level(risk_level: str) -> str:
    """Format risk level for display"""
    risk_levels = {
        'low': 'Низкий',
        'medium': 'Средний',
        'high': 'Высокий'
    }
    return risk_levels.get(risk_level, risk_level)

def format_trimester(trimester: int) -> str:
    """Format trimester for display"""
    trimesters = {
        1: 'Первый триместр',
        2: 'Второй триместр',
        3: 'Третий триместр'
    }
    return trimesters.get(trimester, f'Триместр {trimester}')

def calculate_risk_percentage(risk_score: int, max_score: int = 8) -> int:
    """Calculate risk percentage from score"""
    return min(int((risk_score / max_score) * 100), 100)

def get_risk_recommendations(risk_level: str, heat_wave: bool = False) -> List[str]:
    """Get recommendations based on risk level"""
    recommendations = []
    
    if risk_level == 'high':
        recommendations.extend([
            'Регулярно консультируйтесь с врачом',
            'Следите за артериальным давлением',
            'Отслеживайте движения плода',
            'Избегайте стрессовых ситуаций'
        ])
    elif risk_level == 'medium':
        recommendations.extend([
            'Планируйте регулярные визиты к врачу',
            'Ведите здоровый образ жизни',
            'Следите за питанием'
        ])
    else:
        recommendations.extend([
            'Продолжайте регулярные визиты к врачу',
            'Ведите активный образ жизни',
            'Следите за общим самочувствием'
        ])
    
    if heat_wave:
        recommendations.extend([
            'Оставайтесь в прохладном месте',
            'Пейте больше воды',
            'Избегайте прямых солнечных лучей',
            'Немедленно обратитесь к врачу при ухудшении самочувствия'
        ])
    
    return recommendations

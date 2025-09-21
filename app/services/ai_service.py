import google.generativeai as genai
from flask import current_app
from app.utils.exceptions import ExternalAPIException
import logging

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered recommendations using Google Gemini"""
    
    @staticmethod
    def get_risk_recommendations(patient, risk_data):
        """Get AI-powered risk recommendations for a patient"""
        try:
            # Configure Gemini API
            api_key = current_app.config.get('GEMINI_API_KEY')
            if not api_key:
                raise ExternalAPIException("Gemini API key not configured")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            # Prepare patient context
            patient_context = AIService._prepare_patient_context(patient, risk_data)
            
            # Create prompt for AI
            prompt = AIService._create_risk_assessment_prompt(patient_context, risk_data)
            
            # Get AI response
            response = model.generate_content(prompt)
            
            # Parse and structure the response
            recommendations = AIService._parse_ai_response(response.text)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting AI recommendations: {e}")
            raise ExternalAPIException(f"AI service error: {str(e)}")
    
    @staticmethod
    def get_weather_risk_analysis(weather_data, patient_count):
        """Get AI analysis of weather-related risks"""
        try:
            api_key = current_app.config.get('GEMINI_API_KEY')
            if not api_key:
                raise ExternalAPIException("Gemini API key not configured")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            
            prompt = f"""
            Analyze the following weather conditions for pregnant women health risks:
            
            Temperature: {weather_data.get('temperature', 'N/A')}°C
            Feels like: {weather_data.get('feels_like', 'N/A')}°C
            Humidity: {weather_data.get('humidity', 'N/A')}%
            Heat Index: {weather_data.get('heat_index', 'N/A')}°C
            Is Heat Wave: {weather_data.get('is_heat_wave', False)}
            Description: {weather_data.get('description', 'N/A')}
            Affected Patients: {patient_count}
            
            Provide:
            1. Risk level assessment (Low/Medium/High)
            2. Specific health concerns for pregnant women
            3. Immediate recommendations
            4. Preventive measures
            5. Emergency actions if needed
            
            Format as JSON with keys: risk_level, health_concerns, immediate_recommendations, preventive_measures, emergency_actions
            """
            
            response = model.generate_content(prompt)
            return AIService._parse_weather_analysis(response.text)
            
        except Exception as e:
            logger.error(f"Error getting weather risk analysis: {e}")
            raise ExternalAPIException(f"Weather AI analysis error: {str(e)}")
    
    @staticmethod
    def get_patient_health_advice(patient, risk_data, specific_concern=None):
        """Get personalized health advice for a patient"""
        try:
            api_key = current_app.config.get('GEMINI_API_KEY')
            if not api_key:
                raise ExternalAPIException("Gemini API key not configured")
            
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            patient_context = AIService._prepare_patient_context(patient, risk_data)
            
            prompt = f"""
            Provide personalized health advice for this pregnant patient:
            
            Patient Information:
            - Age: {patient_context['age']}
            - Pregnancy weeks: {patient_context['pregnancy_weeks']}
            - Risk level: {risk_data['risk_level']}
            - Risk score: {risk_data['risk_score']}
            - Conditions: {patient_context['conditions']}
            - Medications: {patient_context['medications']}
            - Weather conditions: {patient_context['weather_conditions']}
            
            Specific concern: {specific_concern or 'General health advice'}
            
            Provide:
            1. Personalized recommendations
            2. Lifestyle modifications
            3. Warning signs to watch for
            4. When to seek medical help
            5. Daily care routine suggestions
            
            Format as JSON with keys: recommendations, lifestyle_modifications, warning_signs, seek_help_when, daily_routine
            """
            
            response = model.generate_content(prompt)
            return AIService._parse_health_advice(response.text)
            
        except Exception as e:
            logger.error(f"Error getting health advice: {e}")
            raise ExternalAPIException(f"Health advice AI error: {str(e)}")
    
    @staticmethod
    def _prepare_patient_context(patient, risk_data):
        """Prepare patient context for AI analysis"""
        return {
            'age': patient.age,
            'pregnancy_weeks': patient.weeks_pregnant,
            'zip_code': patient.zip_code,
            'conditions': patient.get_conditions() if hasattr(patient, 'get_conditions') else [],
            'medications': patient.get_medications_list() if hasattr(patient, 'get_medications_list') else [],
            'pregnancy_icd10': patient.pregnancy_icd10,
            'comorbidity_icd10': patient.comorbidity_icd10,
            'weather_conditions': risk_data.get('weather_data', {}),
            'risk_factors': risk_data.get('factors', {})
        }
    
    @staticmethod
    def _create_risk_assessment_prompt(patient_context, risk_data):
        """Create prompt for risk assessment"""
        return f"""
        As a medical AI assistant, analyze this pregnant patient's risk profile and provide recommendations:
        
        Patient Profile:
        - Age: {patient_context['age']} years
        - Pregnancy: {patient_context['pregnancy_weeks']} weeks
        - Location: {patient_context['zip_code']}
        - Current Risk Level: {risk_data['risk_level']}
        - Risk Score: {risk_data['risk_score']}
        
        Medical Conditions:
        - Pregnancy ICD10: {patient_context['pregnancy_icd10'] or 'None'}
        - Comorbidity ICD10: {patient_context['comorbidity_icd10'] or 'None'}
        - Other conditions: {', '.join(patient_context['conditions']) if patient_context['conditions'] else 'None'}
        
        Medications:
        {', '.join(patient_context['medications']) if patient_context['medications'] else 'None'}
        
        Weather Conditions:
        - Temperature: {patient_context['weather_conditions'].get('temperature', 'N/A')}°C
        - Heat wave risk: {patient_context['weather_conditions'].get('is_heat_wave', False)}
        - Humidity: {patient_context['weather_conditions'].get('humidity', 'N/A')}%
        
        Risk Factors:
        {AIService._format_risk_factors(risk_data.get('factors', {}))}
        
        Provide comprehensive recommendations in JSON format with these keys:
        - immediate_actions: List of immediate actions needed
        - medical_recommendations: Medical care recommendations
        - lifestyle_changes: Lifestyle modifications
        - monitoring_guidelines: What to monitor and how often
        - emergency_signs: Warning signs requiring immediate medical attention
        - weather_precautions: Weather-specific precautions
        - follow_up_schedule: Recommended follow-up schedule
        - priority_level: High/Medium/Low priority for medical attention
        """
    
    @staticmethod
    def _format_risk_factors(factors):
        """Format risk factors for AI prompt"""
        formatted = []
        for factor, value in factors.items():
            if isinstance(value, dict):
                formatted.append(f"- {factor}: {value.get('level', 'unknown')}")
            else:
                formatted.append(f"- {factor}: {value}")
        return '\n'.join(formatted) if formatted else 'None identified'
    
    @staticmethod
    def _parse_ai_response(response_text):
        """Parse AI response and return structured recommendations"""
        try:
            import json
            # Try to extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                # Fallback to text parsing
                return AIService._parse_text_response(response_text)
                
        except Exception as e:
            logger.warning(f"Error parsing AI response: {e}")
            return AIService._parse_text_response(response_text)
    
    @staticmethod
    def _parse_text_response(response_text):
        """Parse text response when JSON parsing fails"""
        return {
            'immediate_actions': ['Review with healthcare provider'],
            'medical_recommendations': ['Regular prenatal care'],
            'lifestyle_changes': ['Maintain healthy diet and exercise'],
            'monitoring_guidelines': ['Regular check-ups as scheduled'],
            'emergency_signs': ['Severe pain, bleeding, or unusual symptoms'],
            'weather_precautions': ['Stay hydrated and avoid extreme temperatures'],
            'follow_up_schedule': ['As recommended by healthcare provider'],
            'priority_level': 'Medium',
            'raw_response': response_text
        }
    
    @staticmethod
    def _parse_weather_analysis(response_text):
        """Parse weather analysis response"""
        try:
            import json
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {
                    'risk_level': 'Medium',
                    'health_concerns': ['Heat-related complications'],
                    'immediate_recommendations': ['Stay hydrated and cool'],
                    'preventive_measures': ['Avoid outdoor activities during peak heat'],
                    'emergency_actions': ['Seek medical help if symptoms worsen'],
                    'raw_response': response_text
                }
        except Exception as e:
            logger.warning(f"Error parsing weather analysis: {e}")
            return {
                'risk_level': 'Medium',
                'health_concerns': ['Heat-related complications'],
                'immediate_recommendations': ['Stay hydrated and cool'],
                'preventive_measures': ['Avoid outdoor activities during peak heat'],
                'emergency_actions': ['Seek medical help if symptoms worsen']
            }
    
    @staticmethod
    def _parse_health_advice(response_text):
        """Parse health advice response"""
        try:
            import json
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            
            if start_idx != -1 and end_idx > start_idx:
                json_str = response_text[start_idx:end_idx]
                return json.loads(json_str)
            else:
                return {
                    'recommendations': ['Follow healthcare provider guidance'],
                    'lifestyle_modifications': ['Maintain healthy lifestyle'],
                    'warning_signs': ['Monitor for unusual symptoms'],
                    'seek_help_when': ['Symptoms worsen or new concerns arise'],
                    'daily_routine': ['Regular meals, hydration, and rest'],
                    'raw_response': response_text
                }
        except Exception as e:
            logger.warning(f"Error parsing health advice: {e}")
            return {
                'recommendations': ['Follow healthcare provider guidance'],
                'lifestyle_modifications': ['Maintain healthy lifestyle'],
                'warning_signs': ['Monitor for unusual symptoms'],
                'seek_help_when': ['Symptoms worsen or new concerns arise'],
                'daily_routine': ['Regular meals, hydration, and rest']
            }

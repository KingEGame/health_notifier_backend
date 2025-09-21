import google.generativeai as genai
from flask import current_app
from app.utils.exceptions import ExternalAPIException

class MessageService:
    """Service for generating and managing notifications"""
    
    @staticmethod
    def generate_personalized_message(patient, risk_assessment):
        """Generate personalized message using Gemini"""
        try:
            genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
            model = genai.GenerativeModel('gemini-pro')
            
            # Prepare context for AI
            context = {
                'patient_name': patient.name,
                'age': patient.age,
                'trimester': risk_assessment['trimester_risk'],
                'risk_level': risk_assessment['risk_level'],
                'heat_wave': risk_assessment['heat_wave_risk'],
                'temperature': risk_assessment['weather_data']['temperature'],
                'conditions': patient.get_conditions()
            }
            
            prompt = f"""
            Generate a personalized health notification for a pregnant woman with the following details:
            - Name: {context['patient_name']}
            - Age: {context['age']} years
            - Trimester: {context['trimester']} (risk level: {context['trimester_risk']})
            - Overall risk level: {context['risk_level']}
            - Heat wave warning: {context['heat_wave']}
            - Current temperature: {context['temperature']}°C
            - Medical conditions: {', '.join(context['conditions']) if context['conditions'] else 'None'}
            
            The message should be:
            - Warm and supportive
            - Specific to her risk level and conditions
            - Include practical advice
            - Be in Russian language
            - Maximum 200 words
            - Professional but caring tone
            """
            
            response = model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            current_app.logger.error(f"Gemini API error: {e}")
            return MessageService._get_default_message(patient, risk_assessment)
    
    @staticmethod
    def _get_default_message(patient, risk_assessment):
        """Generate default message if Gemini fails"""
        risk_level = risk_assessment['risk_level']
        heat_wave = risk_assessment['heat_wave_risk']
        temp = risk_assessment['weather_data']['temperature']
        patient_name = patient.name.split()[0] if patient.name else 'Уважаемая'
        
        if risk_level == 'high':
            if heat_wave:
                return f"Уважаемая {patient_name}, в вашем регионе ожидается жаркая погода ({temp}°C). Учитывая ваш высокий риск, пожалуйста, оставайтесь в прохладном месте, пейте больше воды и немедленно обратитесь к врачу при любых тревожных симптомах."
            else:
                return f"Уважаемая {patient_name}, ваш уровень риска повышен. Пожалуйста, регулярно посещайте врача и следите за своим состоянием."
        elif risk_level == 'medium':
            return f"Уважаемая {patient_name}, следите за своим здоровьем и регулярно консультируйтесь с врачом. При ухудшении самочувствия не откладывайте визит к специалисту."
        else:
            return f"Уважаемая {patient_name}, продолжайте следить за своим здоровьем и регулярно посещайте врача. Все идет хорошо!"

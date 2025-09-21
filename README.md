# Система уведомлений о здоровье для беременных женщин

Комплексная система мониторинга здоровья беременных женщин с интеграцией климатических данных, оценки рисков и персонализированных уведомлений.

## Основные возможности

- **Управление пациентами**: Полные CRUD операции для записей пациентов с детальными медицинскими данными
- **Оценка рисков**: ИИ-оценка рисков на основе множественных факторов
- **Интеграция погоды**: Данные о погоде в реальном времени и обнаружение тепловых волн
- **Персонализированные уведомления**: ИИ-генерируемые советы по здоровью на русском языке
- **REST API**: Полный RESTful API для всех операций
- **Поддержка базы данных**: MySQL база данных
- **Импорт данных**: Массовый импорт пациентов из CSV файлов

## Структура данных пациентов

### Новые поля (обновленная модель)

- **name** (string): Имя пациента
- **age** (integer): Возраст (17-45 лет)
- **pregnancy_icd10** (string): ICD-10 код беременности
- **pregnancy_description** (string): Описание состояния беременности
- **comorbidity_icd10** (string): ICD-10 код сопутствующих заболеваний
- **comorbidity_description** (string): Описание сопутствующих заболеваний
- **weeks_pregnant** (integer): Недели беременности (1-42)
- **address** (string): Адрес пациента
- **zip_code** (string): Почтовый индекс
- **phone_number** (string): Номер телефона
- **email** (string): Email адрес

### Обратная совместимость

Система поддерживает старые поля для обратной совместимости:
- **conditions_icd10** (array): Массив ICD-10 кодов
- **trimester** (integer): Триместр беременности (1-3)

Триместр автоматически рассчитывается из `weeks_pregnant`:
- 1-12 недель = 1 триместр
- 13-24 недели = 2 триместр  
- 25-42 недели = 3 триместр

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

## Установка и запуск

1. **Установите зависимости**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Настройте переменные окружения**:
   ```bash
   cp env.example .env
   # Отредактируйте .env с вашими настройками
   ```

3. **Создайте базу данных MySQL**:
   ```sql
   CREATE DATABASE health_notifier;
   ```

4. **Запустите приложение**:
   ```bash
   python main.py
   ```

## Переменные окружения

Создайте файл `.env` со следующими переменными:

```env
# Настройки базы данных
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=health_notifier

# Внешние API
GEMINI_API_KEY=your_gemini_api_key
WEATHER_API_KEY=your_weather_key

# Настройки приложения
FLASK_ENV=development
SECRET_KEY=your_secret_key
FLASK_DEBUG=True
```

### Как получить API ключи:

1. **Gemini API Key**:
   - Перейдите на https://makersuite.google.com/app/apikey
   - Создайте новый API ключ
   - Скопируйте ключ в переменную `GEMINI_API_KEY`

2. **Weather API Key**:
   - Зарегистрируйтесь на https://openweathermap.org/api
   - Получите бесплатный API ключ
   - Скопируйте ключ в переменную `WEATHER_API_KEY`

## Примеры использования

### Создание пациента с новыми полями

```bash
curl -X POST http://localhost:5000/api/patients \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Анна Петрова",
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

### Импорт данных из CSV

```bash
# Импорт 1000 пациентов из CSV файла
python import_patients.py

# Или с указанием файла
python import_patients.py synthetic_pregnant_patients_1000.csv
```

### Миграция существующей базы данных

```bash
# Обновление схемы для существующих баз данных
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
    "name": "Мария Иванова",
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

### OpenAI API
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
python run.py
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

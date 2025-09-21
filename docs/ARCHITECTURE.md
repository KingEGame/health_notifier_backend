# 🏗️ Health Notification System Architecture

## Architecture Overview

The project is built on **Clean Architecture** and **Application Factory Pattern** for Flask, providing:

- ✅ **Modularity** - each component has clear responsibilities
- ✅ **Testability** - easy to write unit and integration tests
- ✅ **Scalability** - simple addition of new features
- ✅ **Maintainability** - clear code structure

## 📁 Project Structure

```
health_notifier/
├── main.py                    # 🚀 Development entry point
├── wsgi.py                    # 🌐 Production WSGI
├── config.py                  # ⚙️ Environment-specific configurations
├── requirements.txt           # 📦 Production dependencies
├── requirements-dev.txt       # 🛠️ Development dependencies
├── .env.example              # 🔑 Environment variables template
├── .gitignore                # 🚫 Ignored files
│
├── app/                      # 🏠 Main application
│   ├── __init__.py           # 🏭 Application Factory
│   ├── extensions.py         # 🔌 Flask extensions initialization
│   │
│   ├── models/               # 🗄️ Data layer
│   │   ├── __init__.py
│   │   ├── patient.py        # Patient model
│   │   ├── risk_assessment.py # RiskAssessment model
│   │   └── notification.py   # Notification model
│   │
│   ├── api/                  # 🌐 API layer (Controllers)
│   │   ├── __init__.py       # Blueprint registration
│   │   ├── patients.py       # Patient CRUD operations
│   │   ├── assessments.py    # Risk assessment
│   │   ├── notifications.py  # Notification management
│   │   └── health.py         # Health checks and system endpoints
│   │
│   ├── services/             # 🤖 Business logic (Services)
│   │   ├── __init__.py
│   │   ├── weather_service.py    # Weather API integration
│   │   ├── risk_service.py       # Risk assessment algorithms
│   │   └── message_service.py    # Notification generation (Gemini)
│   │
│   ├── schemas/              # ✅ Data validation (DTOs)
│   │   ├── __init__.py
│   │   ├── patient_schema.py     # Patient data validation
│   │   ├── assessment_schema.py  # Risk assessment validation
│   │   └── notification_schema.py # Notification validation
│   │
│   ├── utils/                # 🛠️ Utilities and helpers
│   │   ├── __init__.py
│   │   ├── exceptions.py     # Custom exceptions
│   │   └── helpers.py        # Helper functions
│   │
│   └── errors/               # ❌ Error handling
│       ├── __init__.py
│       └── handlers.py       # Global error handlers
│
├── tests/                    # 🧪 Tests
│   ├── __init__.py
│   └── test_basic.py         # Basic tests
│
├── migrations/               # 🗃️ Database migrations
│   └── versions/
│
└── instance/                 # 📁 Instance-specific data
```

## 🔄 Data Flow

### 1. Patient Creation
```
Client → API (patients.py) → Schema Validation → Model (Patient) → Database
```

### 2. Risk Assessment
```
Client → API (assessments.py) → RiskService → WeatherService + Patient Data → RiskAssessment Model → Database
```

### 3. Notification Generation
```
RiskAssessment → MessageService → Gemini API → Notification Model → Database
```

## 🏗️ Architecture Principles

### 1. **Separation of Concerns**
- **Models** - data handling
- **Services** - business logic
- **API** - HTTP endpoints
- **Schemas** - data validation

### 2. **Dependency Injection**
- Flask extensions initialized in `extensions.py`
- Services receive dependencies through Flask context

### 3. **Error Handling**
- Centralized error handling in `errors/handlers.py`
- Custom exceptions in `utils/exceptions.py`

### 4. **Configuration Management**
- Different configurations for different environments (dev, prod, test)
- Environment variables through `.env`

## 🔌 Integrations

### External APIs
- **OpenWeatherMap** - weather data
- **Google Gemini** - personalized message generation

### Database
- **MySQL** - main database
- **SQLAlchemy** - ORM
- **Flask-Migrate** - migrations

## 🧪 Testing

### Test Structure
- **Unit tests** - testing individual components
- **Integration tests** - testing component interactions
- **API tests** - testing HTTP endpoints

### Running Tests
```bash
# All tests
pytest

# With code coverage
pytest --cov=app

# Specific test
pytest tests/test_basic.py::test_health_check
```

## 🚀 Deployment

### Development
```bash
python main.py
```

### Production
```bash
# With Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application

# With Docker
docker build -t health-notifier .
docker run -p 5000:5000 health-notifier
```

## 📊 Monitoring

### Health Checks
- `/api/health` - basic check
- `/api/health/detailed` - detailed component check

### Logging
- Structured logs through Python logging
- Different levels for different environments

## 🔧 Configuration

### Environment Variables
```env
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=health_notifier

# API keys
GEMINI_API_KEY=your_gemini_key
WEATHER_API_KEY=your_weather_key

# Application settings
FLASK_ENV=development
SECRET_KEY=your_secret_key
```

### Environment-specific Configurations
- **Development** - debugging enabled, local database
- **Production** - optimized for production
- **Testing** - in-memory SQLite for tests

## 🎯 Architecture Benefits

### ✅ **Modularity**
- Each component has clear responsibilities
- Easy to add new features
- Simple testing of individual modules

### ✅ **Scalability**
- Horizontal scaling through Blueprints
- Easy addition of new API endpoints
- Possibility of splitting into microservices

### ✅ **Maintainability**
- Clear code structure
- Centralized error handling
- Consistent patterns throughout the project

### ✅ **Testability**
- Isolated components
- Mock objects for external dependencies
- Automated testing

## 🔮 Extension Possibilities

### New Features
1. **Add new API endpoint** - create file in `app/api/`
2. **Add new model** - create file in `app/models/`
3. **Add new service** - create file in `app/services/`

### Integrations
1. **New external API** - add service in `app/services/`
2. **New database** - configure in `config.py`
3. **New notification type** - extend `Notification` model

This architecture provides a solid foundation for project development and easily adapts to new requirements! 🚀

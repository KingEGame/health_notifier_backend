# 🚀 Quick Start

## 1. Install Dependencies
```bash
pip install -r requirements.txt
```

## 2. Configure Environment Variables
```bash
# Copy the example file
cp env.example .env

# Edit .env file and add your API keys:
```

### In the .env file specify:
```env
# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=health_notifier

# API keys
GEMINI_API_KEY=your_gemini_api_key_here
WEATHER_API_KEY=your_weather_api_key_here

# Settings
FLASK_ENV=development
SECRET_KEY=your_secret_key
FLASK_DEBUG=True
```

## 3. Getting API Keys

### Gemini API Key (Google AI Studio):
1. Go to https://makersuite.google.com/app/apikey
2. Sign in to Google account
3. Click "Create API Key"
4. Copy the key to .env file

### Weather API Key (OpenWeatherMap):
1. Go to https://openweathermap.org/api
2. Register (free)
3. Go to "My API Keys"
4. Copy the key to .env file

## 4. Create Database
```sql
CREATE DATABASE health_notifier;
```

## 5. Run Application
```bash
python main.py
```

## 6. Testing
```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Or simple test
python test_simple.py
```

## 7. Check Operation
Open browser: http://localhost:5000/api/health

---

## 📋 Main API Endpoints:

- `POST /api/patients` - Create patient
- `GET /api/patients/{id}` - Get patient  
- `POST /api/assess-risk/{id}` - Assess risk
- `GET /api/notifications/{id}` - Get notifications
- `GET /api/health` - System check

## 🔧 Project Structure:
```
health_notifier/
├── main.py              # 🚀 Application startup
├── wsgi.py              # 🌐 Production WSGI
├── config.py            # ⚙️ Configuration
├── requirements.txt     # 📦 Dependencies
├── requirements-dev.txt # 🛠️ Dev dependencies
├── env.example          # 🔑 Environment variables example
├── test_simple.py       # 🧪 Simple tests
├── app/
│   ├── __init__.py      # 🏭 Application Factory
│   ├── extensions.py    # 🔌 Flask extensions
│   ├── models/          # 🗄️ Database models
│   ├── api/             # 🌐 API endpoints
│   ├── services/        # 🤖 Business logic
│   ├── schemas/         # ✅ Data validation
│   ├── utils/           # 🛠️ Utilities
│   └── errors/          # ❌ Error handling
├── tests/               # 🧪 Tests
└── README.md            # 📖 Documentation
```

## ❗ Important:
- Make sure MySQL is running
- Check API keys are correct
- Tables will be created automatically on first run

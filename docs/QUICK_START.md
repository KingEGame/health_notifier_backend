# 🚀 Быстрый старт

## 1. Установка зависимостей
```bash
pip install -r requirements.txt
```

## 2. Настройка переменных окружения
```bash
# Скопируйте файл с примером
cp env.example .env

# Отредактируйте .env файл и добавьте ваши API ключи:
```

### В файле .env укажите:
```env
# База данных
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=health_notifier

# API ключи
GEMINI_API_KEY=your_gemini_api_key_here
WEATHER_API_KEY=your_weather_api_key_here

# Настройки
FLASK_ENV=development
SECRET_KEY=your_secret_key
FLASK_DEBUG=True
```

## 3. Получение API ключей

### Gemini API Key (Google AI Studio):
1. Перейдите на https://makersuite.google.com/app/apikey
2. Войдите в Google аккаунт
3. Нажмите "Create API Key"
4. Скопируйте ключ в .env файл

### Weather API Key (OpenWeatherMap):
1. Перейдите на https://openweathermap.org/api
2. Зарегистрируйтесь (бесплатно)
3. Перейдите в "My API Keys"
4. Скопируйте ключ в .env файл

## 4. Создание базы данных
```sql
CREATE DATABASE health_notifier;
```

## 5. Запуск приложения
```bash
python main.py
```

## 6. Тестирование
```bash
# Установите dev зависимости
pip install -r requirements-dev.txt

# Запустите тесты
pytest

# Или простой тест
python test_simple.py
```

## 7. Проверка работы
Откройте браузер: http://localhost:5000/api/health

---

## 📋 Основные API endpoints:

- `POST /api/patients` - Создать пациента
- `GET /api/patients/{id}` - Получить пациента  
- `POST /api/assess-risk/{id}` - Оценить риск
- `GET /api/notifications/{id}` - Получить уведомления
- `GET /api/health` - Проверка системы

## 🔧 Структура проекта:
```
health_notifier/
├── main.py              # 🚀 Запуск приложения
├── wsgi.py              # 🌐 Production WSGI
├── config.py            # ⚙️ Конфигурация
├── requirements.txt     # 📦 Зависимости
├── requirements-dev.txt # 🛠️ Dev зависимости
├── env.example          # 🔑 Пример переменных
├── test_simple.py       # 🧪 Простые тесты
├── app/
│   ├── __init__.py      # 🏭 Application Factory
│   ├── extensions.py    # 🔌 Расширения Flask
│   ├── models/          # 🗄️ Модели базы данных
│   ├── api/             # 🌐 API endpoints
│   ├── services/        # 🤖 Бизнес-логика
│   ├── schemas/         # ✅ Валидация данных
│   ├── utils/           # 🛠️ Утилиты
│   └── errors/          # ❌ Обработка ошибок
├── tests/               # 🧪 Тесты
└── README.md            # 📖 Документация
```

## ❗ Важно:
- Убедитесь, что MySQL запущен
- Проверьте правильность API ключей
- При первом запуске создадутся таблицы автоматически

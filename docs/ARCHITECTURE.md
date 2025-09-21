# 🏗️ Архитектура Health Notification System

## Обзор архитектуры

Проект построен по принципам **Clean Architecture** и **Application Factory Pattern** для Flask, что обеспечивает:

- ✅ **Модульность** - каждый компонент имеет четкую ответственность
- ✅ **Тестируемость** - легко писать unit и integration тесты
- ✅ **Масштабируемость** - простое добавление новых функций
- ✅ **Поддерживаемость** - понятная структура кода

## 📁 Структура проекта

```
health_notifier/
├── main.py                    # 🚀 Точка входа для разработки
├── wsgi.py                    # 🌐 WSGI для production
├── config.py                  # ⚙️ Конфигурации для разных сред
├── requirements.txt           # 📦 Production зависимости
├── requirements-dev.txt       # 🛠️ Development зависимости
├── .env.example              # 🔑 Шаблон переменных окружения
├── .gitignore                # 🚫 Игнорируемые файлы
│
├── app/                      # 🏠 Основное приложение
│   ├── __init__.py           # 🏭 Application Factory
│   ├── extensions.py         # 🔌 Инициализация расширений Flask
│   │
│   ├── models/               # 🗄️ Слой данных
│   │   ├── __init__.py
│   │   ├── patient.py        # Модель Patient
│   │   ├── risk_assessment.py # Модель RiskAssessment
│   │   └── notification.py   # Модель Notification
│   │
│   ├── api/                  # 🌐 Слой API (Controllers)
│   │   ├── __init__.py       # Регистрация Blueprint
│   │   ├── patients.py       # CRUD операции с пациентами
│   │   ├── assessments.py    # Оценка рисков
│   │   ├── notifications.py  # Управление уведомлениями
│   │   └── health.py         # Health checks и системные endpoints
│   │
│   ├── services/             # 🤖 Бизнес-логика (Services)
│   │   ├── __init__.py
│   │   ├── weather_service.py    # Интеграция с погодными API
│   │   ├── risk_service.py       # Алгоритмы оценки рисков
│   │   └── message_service.py    # Генерация уведомлений (Gemini)
│   │
│   ├── schemas/              # ✅ Валидация данных (DTOs)
│   │   ├── __init__.py
│   │   ├── patient_schema.py     # Валидация данных пациентов
│   │   ├── assessment_schema.py  # Валидация оценок риска
│   │   └── notification_schema.py # Валидация уведомлений
│   │
│   ├── utils/                # 🛠️ Утилиты и хелперы
│   │   ├── __init__.py
│   │   ├── exceptions.py     # Кастомные исключения
│   │   └── helpers.py        # Вспомогательные функции
│   │
│   └── errors/               # ❌ Обработка ошибок
│       ├── __init__.py
│       └── handlers.py       # Глобальные обработчики ошибок
│
├── tests/                    # 🧪 Тесты
│   ├── __init__.py
│   └── test_basic.py         # Базовые тесты
│
├── migrations/               # 🗃️ Миграции базы данных
│   └── versions/
│
└── instance/                 # 📁 Instance-specific данные
```

## 🔄 Поток данных

### 1. Создание пациента
```
Client → API (patients.py) → Schema Validation → Model (Patient) → Database
```

### 2. Оценка риска
```
Client → API (assessments.py) → RiskService → WeatherService + Patient Data → RiskAssessment Model → Database
```

### 3. Генерация уведомления
```
RiskAssessment → MessageService → Gemini API → Notification Model → Database
```

## 🏗️ Принципы архитектуры

### 1. **Separation of Concerns**
- **Models** - работа с данными
- **Services** - бизнес-логика
- **API** - HTTP endpoints
- **Schemas** - валидация данных

### 2. **Dependency Injection**
- Расширения Flask инициализируются в `extensions.py`
- Сервисы получают зависимости через Flask context

### 3. **Error Handling**
- Централизованная обработка ошибок в `errors/handlers.py`
- Кастомные исключения в `utils/exceptions.py`

### 4. **Configuration Management**
- Разные конфигурации для разных сред (dev, prod, test)
- Переменные окружения через `.env`

## 🔌 Интеграции

### Внешние API
- **OpenWeatherMap** - данные о погоде
- **Google Gemini** - генерация персонализированных сообщений

### База данных
- **MySQL** - основная база данных
- **SQLAlchemy** - ORM
- **Flask-Migrate** - миграции

## 🧪 Тестирование

### Структура тестов
- **Unit тесты** - тестирование отдельных компонентов
- **Integration тесты** - тестирование взаимодействия компонентов
- **API тесты** - тестирование HTTP endpoints

### Запуск тестов
```bash
# Все тесты
pytest

# С покрытием кода
pytest --cov=app

# Конкретный тест
pytest tests/test_basic.py::test_health_check
```

## 🚀 Развертывание

### Development
```bash
python main.py
```

### Production
```bash
# С Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:application

# С Docker
docker build -t health-notifier .
docker run -p 5000:5000 health-notifier
```

## 📊 Мониторинг

### Health Checks
- `/api/health` - базовая проверка
- `/api/health/detailed` - детальная проверка компонентов

### Логирование
- Структурированные логи через Python logging
- Разные уровни для разных сред

## 🔧 Конфигурация

### Переменные окружения
```env
# База данных
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=password
DB_NAME=health_notifier

# API ключи
GEMINI_API_KEY=your_gemini_key
WEATHER_API_KEY=your_weather_key

# Настройки приложения
FLASK_ENV=development
SECRET_KEY=your_secret_key
```

### Конфигурации по средам
- **Development** - отладка включена, локальная БД
- **Production** - оптимизировано для продакшена
- **Testing** - SQLite в памяти для тестов

## 🎯 Преимущества архитектуры

### ✅ **Модульность**
- Каждый компонент имеет четкую ответственность
- Легко добавлять новые функции
- Простое тестирование отдельных модулей

### ✅ **Масштабируемость**
- Горизонтальное масштабирование через Blueprints
- Легкое добавление новых API endpoints
- Возможность разделения на микросервисы

### ✅ **Поддерживаемость**
- Понятная структура кода
- Централизованная обработка ошибок
- Консистентные паттерны во всем проекте

### ✅ **Тестируемость**
- Изолированные компоненты
- Mock-объекты для внешних зависимостей
- Автоматизированное тестирование

## 🔮 Возможности расширения

### Новые функции
1. **Добавить новый API endpoint** - создать файл в `app/api/`
2. **Добавить новую модель** - создать файл в `app/models/`
3. **Добавить новый сервис** - создать файл в `app/services/`

### Интеграции
1. **Новый внешний API** - добавить сервис в `app/services/`
2. **Новая база данных** - настроить в `config.py`
3. **Новый тип уведомлений** - расширить `Notification` модель

Эта архитектура обеспечивает надежную основу для развития проекта и легко адаптируется под новые требования! 🚀

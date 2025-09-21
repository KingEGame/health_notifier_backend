# 🏥 Health Notifier System - Полная документация

## 📋 Обзор

Health Notifier System - это комплексная система мониторинга здоровья беременных женщин с интеграцией климатических данных, оценки рисков и персонализированных уведомлений на основе ИИ.

## ✨ Основные возможности

- **📊 Детальное управление пациентами**: Полные CRUD операции с детальными медицинскими данными
- **🤖 ИИ-оценка рисков**: Многофакторная оценка рисков на основе возраста, триместра, погоды и медицинских состояний
- **🌤️ Интеграция погоды**: Данные о погоде в реальном времени и обнаружение тепловых волн
- **💬 Персонализированные уведомления**: ИИ-генерируемые советы по здоровью на русском языке (Gemini AI)
- **🌐 REST API**: Полный RESTful API для всех операций
- **🗄️ База данных**: MySQL с поддержкой миграций
- **📥 Импорт данных**: Массовый импорт пациентов из CSV файлов
- **🐳 Docker**: Полная контейнеризация для легкого развертывания
- **☁️ AWS**: Готовые шаблоны для развертывания на AWS

## 🏗️ Архитектура

```
health_notifier/
├── main.py                    # 🚀 Локальный запуск
├── wsgi.py                    # 🌐 Production WSGI
├── Dockerfile                 # 🐳 Docker образ
├── docker-compose.yml         # 🐳 Docker Compose
├── app/                       # 🏠 Основное приложение
│   ├── models/                # 🗄️ Модели базы данных
│   ├── api/                   # 🌐 API endpoints
│   ├── services/              # 🤖 Бизнес-логика
│   ├── schemas/               # ✅ Валидация данных
│   ├── utils/                 # 🛠️ Утилиты
│   └── errors/                # ❌ Обработка ошибок
├── deployment/                # 🚀 Развертывание
│   ├── quick-deploy.sh        # ⚡ Быстрое развертывание
│   ├── setup-ec2.sh          # ⚙️ Настройка EC2
│   ├── cloudformation-template.yaml # ☁️ AWS CloudFormation
│   └── aws-deployment-guide.md # 📚 AWS руководство
├── tests/                     # 🧪 Тесты
├── docs/                      # 📚 Документация
└── README.md                  # 📖 Главная документация
```

## 🚀 Быстрый старт

### 1. Локальная разработка (5 минут)

```bash
# Клонирование
git clone https://github.com/yourusername/health-notifier.git
cd health_notifier

# Установка зависимостей
pip install -r requirements.txt

# Настройка переменных
cp env.example .env
# Отредактируйте .env файл

# Создание базы данных
mysql -u root -p -e "CREATE DATABASE health_notifier;"

# Запуск
python main.py
```

### 2. Docker развертывание (10 минут)

```bash
# Установка переменных
export GEMINI_API_KEY=your-gemini-key
export WEATHER_API_KEY=your-weather-key

# Быстрое развертывание
./deployment/quick-deploy.sh
```

### 3. AWS развертывание (30 минут)

```bash
# CloudFormation
aws cloudformation create-stack \
    --stack-name health-notifier \
    --template-body file://deployment/cloudformation-template.yaml

# Или ручное развертывание
./deployment/setup-ec2.sh
```

## 📊 Структура данных пациентов

### Новые поля (обновленная модель)

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | VARCHAR(100) | Имя пациента |
| `age` | INT | Возраст (17-45 лет) |
| `pregnancy_icd10` | VARCHAR(20) | ICD-10 код беременности |
| `pregnancy_description` | TEXT | Описание состояния беременности |
| `comorbidity_icd10` | VARCHAR(20) | ICD-10 код сопутствующих заболеваний |
| `comorbidity_description` | TEXT | Описание сопутствующих заболеваний |
| `weeks_pregnant` | INT | Недели беременности (1-42) |
| `address` | TEXT | Адрес пациента |
| `zip_code` | VARCHAR(20) | Почтовый индекс |
| `phone_number` | VARCHAR(20) | Номер телефона |
| `email` | VARCHAR(100) | Email адрес |

### Обратная совместимость

- `conditions_icd10` - автоматически преобразуется в `pregnancy_icd10` + `comorbidity_icd10`
- `trimester` - автоматически рассчитывается из `weeks_pregnant`

## 🌐 API Endpoints

### Управление пациентами
- `POST /api/patients` - Создать пациента
- `GET /api/patients/{id}` - Получить пациента
- `PUT /api/patients/{id}` - Обновить пациента
- `DELETE /api/patients/{id}` - Удалить пациента
- `GET /api/patients` - Получить всех пациентов

### Оценка рисков
- `POST /api/assess-risk/{patient_id}` - Оценить риск
- `GET /api/risk/{patient_id}` - Получить оценку риска
- `GET /api/risk/{patient_id}/history` - История оценок

### Уведомления
- `GET /api/notifications/{patient_id}` - Получить уведомления
- `POST /api/notifications/mark-read/{id}` - Отметить как прочитанное
- `GET /api/notifications/unread-count/{patient_id}` - Количество непрочитанных

### Система
- `GET /api/health` - Проверка здоровья
- `GET /api/health/detailed` - Детальная проверка
- `GET /api/weather/{zip_code}` - Данные о погоде

## 📝 Примеры использования

### Создание пациента

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
# Импорт 1000 пациентов
python import_patients.py

# Или с указанием файла
python import_patients.py synthetic_pregnant_patients_1000.csv
```

### Оценка риска

```bash
curl -X POST http://localhost:5000/api/assess-risk/1
```

## 🔧 Конфигурация

### Переменные окружения

```env
# База данных
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=health_notifier

# Внешние API
GEMINI_API_KEY=your_gemini_api_key
WEATHER_API_KEY=your_weather_api_key

# Настройки приложения
FLASK_ENV=development
SECRET_KEY=your_secret_key
```

### Получение API ключей

1. **Gemini API**: https://makersuite.google.com/app/apikey
2. **Weather API**: https://openweathermap.org/api

## 🧪 Тестирование

### Базовые тесты

```bash
# Простые тесты
python test_simple.py

# Тесты новых полей
python test_new_patient_fields.py

# Pytest тесты
pytest tests/
```

### Тестирование API

```bash
# Health check
curl http://localhost:5000/api/health

# Создание пациента
curl -X POST http://localhost:5000/api/patients \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","age":25,"zip_code":"12345","weeks_pregnant":20}'
```

## 🐳 Docker

### Локальная разработка

```bash
# Запуск с Docker Compose
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### Production

```bash
# Сборка образа
docker build -t health-notifier .

# Запуск контейнера
docker run -d \
  --name health-notifier \
  -p 5000:5000 \
  -e GEMINI_API_KEY=your-key \
  -e WEATHER_API_KEY=your-key \
  health-notifier
```

## ☁️ AWS развертывание

### CloudFormation (Автоматическое)

```bash
aws cloudformation create-stack \
    --stack-name health-notifier \
    --template-body file://deployment/cloudformation-template.yaml \
    --parameters ParameterKey=DBPassword,ParameterValue=YourPassword123
```

### Ручное развертывание

```bash
# 1. Создайте EC2 instance
# 2. Скопируйте скрипт настройки
scp -i your-key.pem deployment/setup-ec2.sh ec2-user@your-ec2-ip:~/

# 3. Запустите настройку
ssh -i your-key.pem ec2-user@your-ec2-ip
sudo ./setup-ec2.sh

# 4. Настройте .env файл
sudo nano /home/appuser/health-notifier/.env

# 5. Запустите приложение
sudo systemctl start health-notifier
```

## 📊 Мониторинг

### Health Checks

- **Basic**: `GET /api/health`
- **Detailed**: `GET /api/health/detailed`

### Логирование

```bash
# Docker
docker-compose logs -f

# Systemd
sudo journalctl -u health-notifier -f

# Nginx
sudo tail -f /var/log/nginx/access.log
```

## 💾 Резервное копирование

### Автоматические бэкапы

```bash
# Настройка переменных
export DB_HOST=your-db-host
export DB_PASS=your-password
export S3_BUCKET=your-backup-bucket

# Запуск бэкапа
./deployment/backup-db.sh

# Настройка cron
echo "0 2 * * * /path/to/backup-db.sh" | crontab -
```

## 🔒 Безопасность

### SSL/HTTPS

```bash
# Let's Encrypt
sudo certbot --nginx -d yourdomain.com
```

### Firewall

```bash
# UFW (Ubuntu)
sudo ufw allow 22
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

## 📈 Масштабирование

### Горизонтальное
- Load Balancer
- Auto Scaling Group
- Multiple EC2 instances

### Вертикальное
- Увеличение instance types
- Увеличение RDS instance class
- Увеличение storage

## 💰 Стоимость

### Минимальная конфигурация
- **EC2**: t2.micro (Free Tier)
- **RDS**: db.t3.micro (20GB)
- **Estimated**: $15-25/месяц

### Production конфигурация
- **EC2**: t3.small
- **RDS**: db.t3.small
- **Load Balancer**: ALB
- **Estimated**: $50-100/месяц

## 🛠️ Устранение неполадок

### Общие проблемы

1. **Приложение не запускается**:
   ```bash
   # Проверьте логи
   docker-compose logs app
   sudo journalctl -u health-notifier
   ```

2. **База данных недоступна**:
   ```bash
   # Проверьте подключение
   mysql -h your-db-host -u username -p
   ```

3. **API ключи не работают**:
   ```bash
   # Проверьте переменные
   env | grep API_KEY
   ```

## 📚 Документация

- [Архитектура системы](docs/ARCHITECTURE.md)
- [Руководство по развертыванию](docs/DEPLOYMENT_OVERVIEW.md)
- [Быстрый старт](docs/QUICK_START.md)
- [AWS развертывание](deployment/aws-deployment-guide.md)
- [Руководство по миграции](MIGRATION_GUIDE.md)

## 🤝 Поддержка

Если у вас возникли проблемы:

1. Проверьте логи приложения
2. Убедитесь, что все переменные настроены
3. Проверьте подключение к базе данных
4. Создайте issue в репозитории

## 📄 Лицензия

MIT License - см. файл LICENSE для деталей.

---

**🎉 Готово к использованию! Выберите подходящий вариант развертывания и следуйте инструкциям!**

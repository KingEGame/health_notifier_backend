# 🚀 Health Notifier - Полное руководство по развертыванию

## 📋 Обзор развертывания

Health Notifier System поддерживает множество способов развертывания - от локальной разработки до production на AWS. Выберите подходящий вариант для ваших нужд.

## 🎯 Варианты развертывания

### 1. 🏠 Локальная разработка
**Время настройки**: 5 минут  
**Сложность**: ⭐  
**Стоимость**: Бесплатно

```bash
# Быстрый старт
git clone <repository>
cd health_notifier
pip install -r requirements.txt
python main.py
```

### 2. 🐳 Docker (Рекомендуется)
**Время настройки**: 10 минут  
**Сложность**: ⭐⭐  
**Стоимость**: Бесплатно

```bash
# Быстрое развертывание
export GEMINI_API_KEY=your-key
export WEATHER_API_KEY=your-key
./deployment/quick-deploy.sh
```

### 3. ☁️ AWS EC2
**Время настройки**: 30 минут  
**Сложность**: ⭐⭐⭐  
**Стоимость**: ~$15-25/месяц

```bash
# Создание инфраструктуры
aws cloudformation create-stack \
    --stack-name health-notifier \
    --template-body file://deployment/cloudformation-template.yaml
```

### 4. 🏢 Production AWS
**Время настройки**: 1 час  
**Сложность**: ⭐⭐⭐⭐  
**Стоимость**: ~$50-100/месяц

## 🚀 Быстрый старт (5 минут)

### Шаг 1: Клонирование
```bash
git clone https://github.com/yourusername/health-notifier.git
cd health_notifier
```

### Шаг 2: Установка зависимостей
```bash
pip install -r requirements.txt
```

### Шаг 3: Настройка переменных
```bash
cp env.example .env
# Отредактируйте .env файл
```

### Шаг 4: Создание базы данных
```sql
CREATE DATABASE health_notifier;
```

### Шаг 5: Запуск
```bash
python main.py
```

## 🐳 Docker развертывание

### Простое развертывание
```bash
# Установите переменные окружения
export GEMINI_API_KEY=your-gemini-key
export WEATHER_API_KEY=your-weather-key

# Запустите быстрое развертывание
./deployment/quick-deploy.sh
```

### Ручное развертывание
```bash
# Сборка и запуск
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

## ☁️ AWS развертывание

### 1. CloudFormation (Автоматическое)
```bash
# Создание стека
aws cloudformation create-stack \
    --stack-name health-notifier \
    --template-body file://deployment/cloudformation-template.yaml \
    --parameters ParameterKey=DBPassword,ParameterValue=YourPassword123

# Ожидание завершения
aws cloudformation wait stack-create-complete \
    --stack-name health-notifier
```

### 2. Ручное развертывание на EC2
```bash
# 1. Создайте EC2 instance (Amazon Linux 2)
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

### 3. Автоматическое развертывание
```bash
# Настройте переменные
export INSTANCE_IP=your-ec2-ip
export KEY_PATH=~/.ssh/your-key.pem

# Запустите развертывание
./deployment/deploy.sh
```

## 🔧 Конфигурация

### Обязательные переменные окружения

```env
# API ключи
GEMINI_API_KEY=your-gemini-api-key
WEATHER_API_KEY=your-weather-api-key

# База данных
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=health_notifier

# Настройки приложения
FLASK_ENV=production
SECRET_KEY=your-secret-key
```

### Получение API ключей

1. **Gemini API**:
   - https://makersuite.google.com/app/apikey
   - Создайте API ключ
   - Скопируйте в `GEMINI_API_KEY`

2. **Weather API**:
   - https://openweathermap.org/api
   - Зарегистрируйтесь (бесплатно)
   - Скопируйте в `WEATHER_API_KEY`

## 📊 Мониторинг и логи

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
- **Storage**: 20GB
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

### Полезные команды

```bash
# Перезапуск сервисов
sudo systemctl restart health-notifier
docker-compose restart

# Проверка статуса
sudo systemctl status health-notifier
docker-compose ps

# Тестирование API
curl http://localhost:5000/api/health
```

## 📚 Дополнительные ресурсы

- [Архитектура системы](ARCHITECTURE.md)
- [Быстрый старт](QUICK_START.md)
- [AWS руководство](deployment/aws-deployment-guide.md)
- [Docker руководство](deployment/README.md)

## 🆘 Поддержка

Если у вас возникли проблемы:

1. Проверьте логи приложения
2. Убедитесь, что все переменные настроены
3. Проверьте подключение к базе данных
4. Создайте issue в репозитории

---

**Выберите подходящий вариант развертывания и следуйте инструкциям!** 🚀

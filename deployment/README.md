# 🚀 Health Notifier - Deployment Guide

Этот каталог содержит все необходимые файлы и скрипты для развертывания Health Notifier System на различных платформах.

## 📁 Структура deployment/

```
deployment/
├── aws-deployment-guide.md    # 📚 Полное руководство по AWS
├── cloudformation-template.yaml # ☁️ CloudFormation шаблон
├── deploy.sh                   # 🚀 Скрипт развертывания на EC2
├── setup-ec2.sh               # ⚙️ Настройка EC2 instance
├── backup-db.sh               # 💾 Скрипт резервного копирования
├── quick-deploy.sh            # ⚡ Быстрое развертывание с Docker
├── nginx.conf                 # 🌐 Конфигурация Nginx
├── init-db.sql               # 🗄️ Инициализация базы данных
└── README.md                 # 📖 Этот файл
```

## 🚀 Быстрый старт

### 1. Локальное развертывание с Docker

```bash
# Клонируйте репозиторий
git clone https://github.com/yourusername/health-notifier.git
cd health-notifier

# Установите переменные окружения
export GEMINI_API_KEY=your-gemini-api-key
export WEATHER_API_KEY=your-weather-api-key

# Запустите быстрое развертывание
chmod +x deployment/quick-deploy.sh
./deployment/quick-deploy.sh
```

### 2. Развертывание на AWS EC2

```bash
# 1. Создайте EC2 instance (Amazon Linux 2)
# 2. Скопируйте скрипт настройки
scp -i your-key.pem deployment/setup-ec2.sh ec2-user@your-ec2-ip:~/

# 3. Подключитесь к instance и запустите настройку
ssh -i your-key.pem ec2-user@your-ec2-ip
chmod +x setup-ec2.sh
sudo ./setup-ec2.sh

# 4. Настройте .env файл
sudo nano /home/appuser/health-notifier/.env

# 5. Запустите приложение
sudo systemctl start health-notifier
```

### 3. Развертывание с CloudFormation

```bash
# Создайте стек CloudFormation
aws cloudformation create-stack \
    --stack-name health-notifier \
    --template-body file://deployment/cloudformation-template.yaml \
    --parameters ParameterKey=DBPassword,ParameterValue=YourSecurePassword123 \
                 ParameterKey=KeyPairName,ParameterValue=your-key-pair
```

## 🔧 Конфигурация

### Переменные окружения

Создайте файл `.env` со следующими переменными:

```env
# Database Configuration
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=health_notifier

# External APIs
GEMINI_API_KEY=your_gemini_api_key
WEATHER_API_KEY=your_weather_key

# App Settings
FLASK_ENV=production
SECRET_KEY=your_secret_key
```

### Получение API ключей

1. **Gemini API Key**:
   - Перейдите на https://makersuite.google.com/app/apikey
   - Создайте новый API ключ
   - Скопируйте ключ в переменную `GEMINI_API_KEY`

2. **Weather API Key**:
   - Зарегистрируйтесь на https://openweathermap.org/api
   - Получите бесплатный API ключ
   - Скопируйте ключ в переменную `WEATHER_API_KEY`

## 🐳 Docker развертывание

### Локальная разработка

```bash
# Запуск с Docker Compose
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка
docker-compose down
```

### Production с Docker

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

### 1. RDS MySQL Database

```bash
# Создание RDS instance
aws rds create-db-instance \
    --db-instance-identifier health-notifier-db \
    --db-instance-class db.t3.micro \
    --engine mysql \
    --master-username admin \
    --master-user-password YourSecurePassword123 \
    --allocated-storage 20 \
    --db-name health_notifier
```

### 2. EC2 Instance

```bash
# Запуск EC2 instance
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --instance-type t2.micro \
    --key-name your-key-pair \
    --security-group-ids sg-xxxxxxxxx
```

### 3. Автоматическое развертывание

```bash
# Настройка переменных
export INSTANCE_IP=your-ec2-public-ip
export KEY_PATH=~/.ssh/your-key.pem

# Запуск развертывания
chmod +x deployment/deploy.sh
./deployment/deploy.sh
```

## 🔒 Безопасность

### Security Groups

**EC2 Security Group:**
- Port 22 (SSH): Your IP only
- Port 80 (HTTP): 0.0.0.0/0
- Port 443 (HTTPS): 0.0.0.0/0

**RDS Security Group:**
- Port 3306 (MySQL): EC2 Security Group only

### SSL/HTTPS

```bash
# Установка Let's Encrypt
sudo yum install certbot python3-certbot-nginx -y

# Получение сертификата
sudo certbot --nginx -d yourdomain.com
```

## 📊 Мониторинг

### Health Checks

- **Basic**: `GET /api/health`
- **Detailed**: `GET /api/health/detailed`

### Логирование

```bash
# Просмотр логов приложения
sudo journalctl -u health-notifier -f

# Просмотр логов Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### CloudWatch (AWS)

```bash
# Установка CloudWatch agent
sudo yum install amazon-cloudwatch-agent -y

# Конфигурация
sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-config-wizard
```

## 💾 Резервное копирование

### Автоматические бэкапы

```bash
# Настройка переменных
export DB_HOST=your-rds-endpoint
export DB_PASS=your-password
export S3_BUCKET=your-backup-bucket

# Запуск бэкапа
chmod +x deployment/backup-db.sh
./deployment/backup-db.sh

# Настройка cron для автоматических бэкапов
echo "0 2 * * * /path/to/backup-db.sh" | crontab -
```

## 🔧 Устранение неполадок

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
   # Проверьте переменные окружения
   env | grep API_KEY
   ```

### Полезные команды

```bash
# Перезапуск сервисов
sudo systemctl restart health-notifier
sudo systemctl restart nginx

# Проверка статуса
sudo systemctl status health-notifier
sudo systemctl status nginx

# Тестирование API
curl http://localhost:5000/api/health
curl -X POST http://localhost:5000/api/patients -H "Content-Type: application/json" -d '{"name":"Test","age":25,"geo_location":"Test","zip_code":"12345","trimester":2}'
```

## 📈 Масштабирование

### Горизонтальное масштабирование

1. **Load Balancer**: Настройте Application Load Balancer
2. **Auto Scaling**: Создайте Auto Scaling Group
3. **Database**: Используйте Read Replicas

### Вертикальное масштабирование

1. **EC2**: Увеличьте instance type
2. **RDS**: Увеличьте DB instance class
3. **Storage**: Увеличьте allocated storage

## 💰 Оптимизация затрат

### Минимальная конфигурация
- **EC2**: t2.micro (Free Tier)
- **RDS**: db.t3.micro (20GB)
- **Estimated Cost**: ~$15-25/месяц

### Оптимизация
- Используйте Spot Instances для dev/test
- Настройте автоматическое масштабирование
- Используйте S3 для статических файлов
- Настройте CloudWatch для мониторинга

## 📞 Поддержка

Если у вас возникли проблемы с развертыванием:

1. Проверьте логи приложения
2. Убедитесь, что все переменные окружения настроены
3. Проверьте подключение к базе данных
4. Проверьте статус сервисов

Для получения помощи создайте issue в репозитории проекта.

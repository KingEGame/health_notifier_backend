# AWS Deployment Guide - Health Notifier

## 1. AWS Services Setup

### RDS MySQL Database
```bash
# AWS CLI команды для создания RDS
aws rds create-db-instance \
    --db-instance-identifier health-notifier-db \
    --db-instance-class db.t3.micro \
    --engine mysql \
    --master-username admin \
    --master-user-password YourSecurePassword123 \
    --allocated-storage 20 \
    --db-name health_notifier \
    --vpc-security-group-ids sg-xxxxxxxxx \
    --backup-retention-period 7 \
    --storage-encrypted
```

### EC2 Instance Setup
```bash
# User Data script для автоматической настройки EC2
#!/bin/bash
yum update -y
yum install python3 python3-pip git nginx -y

# Создание пользователя для приложения
useradd -m appuser
su - appuser

# Клонирование репозитория (замените на ваш URL)
git clone https://github.com/yourusername/health-notifier.git /home/appuser/health-notifier
cd /home/appuser/health-notifier

# Создание виртуальной среды
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
pip install gunicorn

# Создание .env файла (будет настроен позже)
touch .env
chown appuser:appuser .env

# Systemd service файл
cat > /etc/systemd/system/health-notifier.service << EOF
[Unit]
Description=Health Notifier API
After=network.target

[Service]
User=appuser
Group=appuser
WorkingDirectory=/home/appuser/health-notifier
Environment=PATH=/home/appuser/health-notifier/venv/bin
EnvironmentFile=/home/appuser/health-notifier/.env
ExecStart=/home/appuser/health-notifier/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Nginx конфигурация
cat > /etc/nginx/conf.d/health-notifier.conf << EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# Запуск сервисов
systemctl enable nginx
systemctl start nginx
systemctl enable health-notifier
```

## 2. Environment Configuration для Production

### .env для AWS Production
```env
# Database (RDS)
DB_HOST=health-notifier-db.xxxxxxxxx.us-east-1.rds.amazonaws.com
DB_USER=admin
DB_PASSWORD=YourSecurePassword123
DB_NAME=health_notifier

# External APIs
GEMINI_API_KEY=your-production-gemini-key
WEATHER_API_KEY=your-production-weather-key

# App settings
FLASK_ENV=production
SECRET_KEY=your-very-secure-production-secret-key

# Security
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

## 3. Security Groups Configuration

### RDS Security Group
```json
{
  "GroupName": "health-notifier-rds-sg",
  "Description": "Security group for Health Notifier RDS",
  "SecurityGroupRules": [
    {
      "IpProtocol": "tcp",
      "FromPort": 3306,
      "ToPort": 3306,
      "ReferencedGroupInfo": {
        "GroupId": "sg-ec2-security-group-id"
      }
    }
  ]
}
```

### EC2 Security Group
```json
{
  "GroupName": "health-notifier-ec2-sg", 
  "Description": "Security group for Health Notifier EC2",
  "SecurityGroupRules": [
    {
      "IpProtocol": "tcp",
      "FromPort": 80,
      "ToPort": 80,
      "CidrIp": "0.0.0.0/0"
    },
    {
      "IpProtocol": "tcp", 
      "FromPort": 443,
      "ToPort": 443,
      "CidrIp": "0.0.0.0/0"
    },
    {
      "IpProtocol": "tcp",
      "FromPort": 22,
      "ToPort": 22,
      "CidrIp": "your-ip/32"
    }
  ]
}
```

## 4. CloudFormation Template

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Health Notifier Infrastructure'

Parameters:
  DBPassword:
    Type: String
    NoEcho: true
    Description: Password for RDS MySQL database

Resources:
  # VPC and Networking
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      EnableDnsSupport: true
      
  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true
      
  PrivateSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.2.0/24
      AvailabilityZone: !Select [1, !GetAZs '']
      
  # RDS Instance
  DBSubnetGroup:
    Type: AWS::RDS::DBSubnetGroup
    Properties:
      DBSubnetGroupDescription: Subnet group for Health Notifier RDS
      SubnetIds: [!Ref PublicSubnet, !Ref PrivateSubnet]
      
  HealthNotifierDB:
    Type: AWS::RDS::DBInstance
    Properties:
      DBInstanceIdentifier: health-notifier-db
      DBInstanceClass: db.t3.micro
      Engine: mysql
      MasterUsername: admin
      MasterUserPassword: !Ref DBPassword
      AllocatedStorage: 20
      DBName: health_notifier
      DBSubnetGroupName: !Ref DBSubnetGroup
      VPCSecurityGroups: [!Ref RDSSecurityGroup]
      
  # EC2 Instance
  HealthNotifierInstance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0abcdef1234567890  # Amazon Linux 2
      InstanceType: t2.micro
      SecurityGroupIds: [!Ref EC2SecurityGroup]
      SubnetId: !Ref PublicSubnet
      UserData: !Base64 |
        #!/bin/bash
        # User data script здесь
        
Outputs:
  DatabaseEndpoint:
    Description: RDS MySQL endpoint
    Value: !GetAtt HealthNotifierDB.Endpoint.Address
    
  InstancePublicIP:
    Description: EC2 instance public IP
    Value: !GetAtt HealthNotifierInstance.PublicIp
```

## 5. Deployment Scripts

### deploy.sh
```bash
#!/bin/bash
set -e

echo "Starting deployment..."

# Variables
INSTANCE_IP="your-ec2-public-ip"
KEY_PATH="~/.ssh/your-key.pem"
REPO_URL="https://github.com/yourusername/health-notifier.git"

# SSH into instance and deploy
ssh -i $KEY_PATH ec2-user@$INSTANCE_IP << 'EOF'
    cd /home/appuser/health-notifier
    
    # Stop the service
    sudo systemctl stop health-notifier
    
    # Pull latest code
    git pull origin main
    
    # Activate virtual environment and update dependencies
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Restart the service
    sudo systemctl start health-notifier
    sudo systemctl status health-notifier
    
    echo "Deployment completed!"
EOF

# Test the deployment
echo "Testing deployment..."
curl -f http://$INSTANCE_IP/api/health || echo "Health check failed!"

echo "Deployment script finished!"
```

## 6. Monitoring and Logging

### CloudWatch Configuration
```python
# Добавить в config.py
import boto3

class ProductionConfig(Config):
    # CloudWatch Logs
    LOG_GROUP = '/aws/ec2/health-notifier'
    
    @staticmethod
    def setup_logging():
        import logging
        import watchtower
        
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)
        
        # CloudWatch handler
        cloudwatch_handler = watchtower.CloudWatchLogsHandler(
            log_group='/aws/ec2/health-notifier'
        )
        logger.addHandler(cloudwatch_handler)
```

### Health Check Endpoint для Load Balancer
```python
# Добавить в routes.py
@app.route('/health-detailed', methods=['GET'])
def health_check_detailed():
    """Детальная проверка состояния для мониторинга"""
    try:
        # Проверка подключения к БД
        db.session.execute('SELECT 1')
        
        # Проверка внешних API
        weather_status = "ok" if WeatherService.get_weather_data("10001") else "error"
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'weather_api': weather_status,
            'timestamp': datetime.utcnow().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503
```

## 7. SSL/HTTPS Setup с Let's Encrypt

```bash
# Установка Certbot
sudo yum install certbot python3-certbot-nginx -y

# Получение SSL сертификата
sudo certbot --nginx -d yourdomain.com

# Автоматическое обновление
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -
```

## 8. Backup Strategy

### Database Backup Script
```bash
#!/bin/bash
# backup_db.sh

DB_HOST="your-rds-endpoint"
DB_NAME="health_notifier"
DB_USER="admin"
DB_PASS="your-password"
BACKUP_DIR="/home/appuser/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Create database backup
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME > $BACKUP_DIR/health_notifier_$DATE.sql

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR/health_notifier_$DATE.sql s3://your-backup-bucket/database/

# Keep only last 7 days of backups locally
find $BACKUP_DIR -name "health_notifier_*.sql" -mtime +7 -delete

echo "Backup completed: health_notifier_$DATE.sql"
```

### Cron job для автоматических бэкапов
```bash
# Добавить в crontab
0 2 * * * /home/appuser/backup_db.sh >> /var/log/backup.log 2>&1
```

## 9. Production Checklist

- [ ] RDS instance создан с encrypted storage
- [ ] Security Groups настроены правильно
- [ ] SSL сертификат установлен
- [ ] Environment variables настроены для production
- [ ] Backup strategy реализована
- [ ] Monitoring и logging настроены
- [ ] Health checks работают
- [ ] Rate limiting добавлен (опционально)
- [ ] API documentation готова
- [ ] Load testing проведен

## 10. Cost Optimization

### AWS Resources Minimal Setup:
- **EC2**: t2.micro (Free Tier eligible)
- **RDS**: db.t3.micro (20GB storage)
- **Data Transfer**: Минимальный для API запросов
- **Estimated Monthly Cost**: ~$15-25

### Scaling Options:
1. **Горизонтальное**: Load Balancer + Auto Scaling Group
2. **Вертикальное**: Увеличение instance types
3. **Database**: Read replicas для read-heavy workloads

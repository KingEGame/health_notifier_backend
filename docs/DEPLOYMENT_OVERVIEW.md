# 🚀 Health Notifier - Complete Deployment Guide

## 📋 Deployment Overview

Health Notifier System supports multiple deployment methods - from local development to production on AWS. Choose the option that suits your needs.

## 🎯 Deployment Options

### 1. 🏠 Local Development
**Setup time**: 5 minutes  
**Complexity**: ⭐  
**Cost**: Free

```bash
# Quick start
git clone <repository>
cd health_notifier
pip install -r requirements.txt
python main.py
```

### 2. 🐳 Docker (Recommended)
**Setup time**: 10 minutes  
**Complexity**: ⭐⭐  
**Cost**: Free

```bash
# Quick deployment
export GEMINI_API_KEY=your-key
export WEATHER_API_KEY=your-key
./deployment/quick-deploy.sh
```

### 3. ☁️ AWS EC2
**Setup time**: 30 minutes  
**Complexity**: ⭐⭐⭐  
**Cost**: ~$15-25/month

```bash
# Create infrastructure
aws cloudformation create-stack \
    --stack-name health-notifier \
    --template-body file://deployment/cloudformation-template.yaml
```

### 4. 🏢 Production AWS
**Setup time**: 1 hour  
**Complexity**: ⭐⭐⭐⭐  
**Cost**: ~$50-100/month

## 🚀 Quick Start (5 minutes)

### Step 1: Clone
```bash
git clone https://github.com/yourusername/health-notifier.git
cd health_notifier
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Variables
```bash
cp env.example .env
# Edit .env file
```

### Step 4: Create Database
```sql
CREATE DATABASE health_notifier;
```

### Step 5: Run
```bash
python main.py
```

## 🐳 Docker Deployment

### Simple Deployment
```bash
# Set environment variables
export GEMINI_API_KEY=your-gemini-key
export WEATHER_API_KEY=your-weather-key

# Run quick deployment
./deployment/quick-deploy.sh
```

### Manual Deployment
```bash
# Build and run
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

## ☁️ AWS Deployment

### 1. CloudFormation (Automatic)
```bash
# Create stack
aws cloudformation create-stack \
    --stack-name health-notifier \
    --template-body file://deployment/cloudformation-template.yaml \
    --parameters ParameterKey=DBPassword,ParameterValue=YourPassword123

# Wait for completion
aws cloudformation wait stack-create-complete \
    --stack-name health-notifier
```

### 2. Manual EC2 Deployment
```bash
# 1. Create EC2 instance (Amazon Linux 2)
# 2. Copy setup script
scp -i your-key.pem deployment/setup-ec2.sh ec2-user@your-ec2-ip:~/

# 3. Run setup
ssh -i your-key.pem ec2-user@your-ec2-ip
sudo ./setup-ec2.sh

# 4. Configure .env file
sudo nano /home/appuser/health-notifier/.env

# 5. Start application
sudo systemctl start health-notifier
```

### 3. Automatic Deployment
```bash
# Set variables
export INSTANCE_IP=your-ec2-ip
export KEY_PATH=~/.ssh/your-key.pem

# Run deployment
./deployment/deploy.sh
```

## 🔧 Configuration

### Required Environment Variables

```env
# API keys
GEMINI_API_KEY=your-gemini-api-key
WEATHER_API_KEY=your-weather-api-key

# Database
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=health_notifier

# Application settings
FLASK_ENV=production
SECRET_KEY=your-secret-key
```

### Getting API Keys

1. **Gemini API**:
   - https://makersuite.google.com/app/apikey
   - Create API key
   - Copy to `GEMINI_API_KEY`

2. **Weather API**:
   - https://openweathermap.org/api
   - Register (free)
   - Copy to `WEATHER_API_KEY`

## 📊 Monitoring and Logs

### Health Checks
- **Basic**: `GET /api/health`
- **Detailed**: `GET /api/health/detailed`

### Logging
```bash
# Docker
docker-compose logs -f

# Systemd
sudo journalctl -u health-notifier -f

# Nginx
sudo tail -f /var/log/nginx/access.log
```

## 💾 Backup

### Automatic Backups
```bash
# Set variables
export DB_HOST=your-db-host
export DB_PASS=your-password
export S3_BUCKET=your-backup-bucket

# Run backup
./deployment/backup-db.sh

# Setup cron
echo "0 2 * * * /path/to/backup-db.sh" | crontab -
```

## 🔒 Security

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

## 📈 Scaling

### Horizontal
- Load Balancer
- Auto Scaling Group
- Multiple EC2 instances

### Vertical
- Increase instance types
- Increase RDS instance class
- Increase storage

## 💰 Cost

### Minimal Configuration
- **EC2**: t2.micro (Free Tier)
- **RDS**: db.t3.micro (20GB)
- **Storage**: 20GB
- **Estimated**: $15-25/month

### Production Configuration
- **EC2**: t3.small
- **RDS**: db.t3.small
- **Load Balancer**: ALB
- **Estimated**: $50-100/month

## 🛠️ Troubleshooting

### Common Issues

1. **Application won't start**:
   ```bash
   # Check logs
   docker-compose logs app
   sudo journalctl -u health-notifier
   ```

2. **Database unavailable**:
   ```bash
   # Check connection
   mysql -h your-db-host -u username -p
   ```

3. **API keys not working**:
   ```bash
   # Check variables
   env | grep API_KEY
   ```

### Useful Commands

```bash
# Restart services
sudo systemctl restart health-notifier
docker-compose restart

# Check status
sudo systemctl status health-notifier
docker-compose ps

# Test API
curl http://localhost:5000/api/health
```

## 📚 Additional Resources

- [System Architecture](ARCHITECTURE.md)
- [Quick Start](QUICK_START.md)
- [AWS Guide](deployment/aws-deployment-guide.md)
- [Docker Guide](deployment/README.md)

## 🆘 Support

If you encounter issues:

1. Check application logs
2. Ensure all variables are configured
3. Check database connection
4. Create an issue in the repository

---

**Choose the appropriate deployment option and follow the instructions!** 🚀

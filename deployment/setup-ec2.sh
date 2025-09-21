#!/bin/bash
set -e

echo "🏗️ Setting up EC2 instance for Health Notifier..."

# Update system
echo "📦 Updating system packages..."
sudo yum update -y

# Install required packages
echo "🔧 Installing required packages..."
sudo yum install python3 python3-pip git nginx mysql -y

# Create application user
echo "👤 Creating application user..."
sudo useradd -m appuser || echo "User appuser already exists"

# Switch to appuser and setup application
sudo -u appuser bash << 'EOF'
    echo "📁 Setting up application directory..."
    cd /home/appuser
    
    # Clone repository (replace with your actual repository URL)
    if [ ! -d "health-notifier" ]; then
        git clone https://github.com/yourusername/health-notifier.git health-notifier
    else
        echo "Repository already exists, updating..."
        cd health-notifier
        git pull origin main
        cd ..
    fi
    
    cd health-notifier
    
    # Create virtual environment
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    echo "📦 Installing Python dependencies..."
    pip install -r requirements.txt
    pip install gunicorn
    
    # Create .env file template
    echo "📝 Creating .env template..."
    cat > .env << 'ENVEOF'
# Database Configuration
DB_HOST=your-rds-endpoint.amazonaws.com
DB_USER=admin
DB_PASSWORD=your-secure-password
DB_NAME=health_notifier

# External APIs
GEMINI_API_KEY=your-gemini-api-key
WEATHER_API_KEY=your-weather-api-key

# App Settings
FLASK_ENV=production
SECRET_KEY=your-very-secure-secret-key
ENVEOF
    
    echo "✅ Application setup completed!"
EOF

# Create systemd service
echo "⚙️ Creating systemd service..."
sudo tee /etc/systemd/system/health-notifier.service > /dev/null << 'EOF'
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
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
echo "🌐 Configuring Nginx..."
sudo tee /etc/nginx/conf.d/health-notifier.conf > /dev/null << 'EOF'
server {
    listen 80;
    server_name _;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    
    location / {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }
    
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
    
    # Static files (if any)
    location /static {
        alias /home/appuser/health-notifier/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable and start services
echo "🚀 Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl enable health-notifier

# Configure firewall
echo "🔥 Configuring firewall..."
sudo systemctl enable firewalld
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --reload

# Create backup directory
echo "💾 Creating backup directory..."
sudo mkdir -p /home/appuser/backups
sudo chown appuser:appuser /home/appuser/backups

# Setup log rotation
echo "📋 Setting up log rotation..."
sudo tee /etc/logrotate.d/health-notifier > /dev/null << 'EOF'
/home/appuser/health-notifier/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 appuser appuser
    postrotate
        systemctl reload health-notifier
    endscript
}
EOF

echo "✅ EC2 setup completed!"
echo ""
echo "📋 Next steps:"
echo "1. Update /home/appuser/health-notifier/.env with your actual values"
echo "2. Start the service: sudo systemctl start health-notifier"
echo "3. Check status: sudo systemctl status health-notifier"
echo "4. Test: curl http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4)/api/health"

#!/bin/bash
set -e

echo "🚀 Starting Health Notifier deployment..."

# Configuration
INSTANCE_IP="${INSTANCE_IP:-your-ec2-public-ip}"
KEY_PATH="${KEY_PATH:-~/.ssh/your-key.pem}"
REPO_URL="${REPO_URL:-https://github.com/yourusername/health-notifier.git}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required variables are set
if [ "$INSTANCE_IP" = "your-ec2-public-ip" ]; then
    print_error "Please set INSTANCE_IP environment variable"
    exit 1
fi

if [ "$KEY_PATH" = "~/.ssh/your-key.pem" ]; then
    print_error "Please set KEY_PATH environment variable"
    exit 1
fi

print_status "Deploying to instance: $INSTANCE_IP"
print_status "Using key: $KEY_PATH"

# SSH into instance and deploy
ssh -i $KEY_PATH ec2-user@$INSTANCE_IP << 'EOF'
    set -e
    
    echo "🔧 Updating application..."
    
    # Navigate to application directory
    cd /home/appuser/health-notifier
    
    # Stop the service
    echo "⏹️ Stopping service..."
    sudo systemctl stop health-notifier || true
    
    # Pull latest code
    echo "📥 Pulling latest code..."
    git pull origin main
    
    # Activate virtual environment and update dependencies
    echo "📦 Updating dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Run database migrations (if any)
    echo "🗄️ Running database migrations..."
    python -c "
    from app import create_app, db
    app = create_app('production')
    with app.app_context():
        db.create_all()
        print('Database tables created/updated')
    " || echo "Migration failed, continuing..."
    
    # Restart the service
    echo "🔄 Starting service..."
    sudo systemctl start health-notifier
    sudo systemctl status health-notifier --no-pager
    
    echo "✅ Deployment completed!"
EOF

# Test the deployment
print_status "Testing deployment..."
if curl -f -s http://$INSTANCE_IP/api/health > /dev/null; then
    print_status "✅ Health check passed!"
else
    print_error "❌ Health check failed!"
    exit 1
fi

print_status "🎉 Deployment script finished successfully!"

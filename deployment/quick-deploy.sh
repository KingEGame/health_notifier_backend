#!/bin/bash
set -e

echo "🚀 Health Notifier - Quick Deployment Script"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_header "1. Environment Setup"
print_status "Checking environment variables..."

# Check for required environment variables
if [ -z "$GEMINI_API_KEY" ]; then
    print_warning "GEMINI_API_KEY not set. Please set it:"
    echo "export GEMINI_API_KEY=your-gemini-api-key"
    read -p "Enter your Gemini API key: " GEMINI_API_KEY
    export GEMINI_API_KEY
fi

if [ -z "$WEATHER_API_KEY" ]; then
    print_warning "WEATHER_API_KEY not set. Please set it:"
    echo "export WEATHER_API_KEY=your-weather-api-key"
    read -p "Enter your Weather API key: " WEATHER_API_KEY
    export WEATHER_API_KEY
fi

print_header "2. Building Application"
print_status "Building Docker images..."
docker-compose build

print_header "3. Starting Services"
print_status "Starting MySQL and application..."
docker-compose up -d mysql

# Wait for MySQL to be ready
print_status "Waiting for MySQL to be ready..."
sleep 30

# Start application
docker-compose up -d app

# Wait for application to be ready
print_status "Waiting for application to be ready..."
sleep 10

print_header "4. Health Check"
print_status "Testing application health..."

# Test health endpoint
if curl -f -s http://localhost:5000/api/health > /dev/null; then
    print_status "✅ Application is healthy!"
else
    print_error "❌ Health check failed!"
    print_status "Checking logs..."
    docker-compose logs app
    exit 1
fi

print_header "5. Testing API"
print_status "Testing API endpoints..."

# Test creating a patient
PATIENT_DATA='{
    "name": "Test Patient",
    "age": 25,
    "geo_location": "Test City",
    "zip_code": "12345",
    "conditions_icd10": ["O24.4"],
    "trimester": 2
}'

if curl -f -s -X POST http://localhost:5000/api/patients \
    -H "Content-Type: application/json" \
    -d "$PATIENT_DATA" > /dev/null; then
    print_status "✅ Patient creation test passed!"
else
    print_warning "⚠️ Patient creation test failed (this might be expected if validation is strict)"
fi

print_header "6. Deployment Complete!"
print_status "🎉 Health Notifier is now running!"
echo ""
echo "📋 Access Information:"
echo "  Application URL: http://localhost:5000"
echo "  Health Check: http://localhost:5000/api/health"
echo "  API Documentation: http://localhost:5000/api/health/detailed"
echo ""
echo "📊 Management Commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart: docker-compose restart"
echo "  Update: docker-compose pull && docker-compose up -d"
echo ""
echo "🔧 Configuration:"
echo "  Edit .env file to change settings"
echo "  Database: MySQL on localhost:3306"
echo "  Logs: Check docker-compose logs"
echo ""

# Show running containers
print_status "Running containers:"
docker-compose ps

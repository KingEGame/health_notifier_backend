#!/bin/bash
set -e

# Configuration
DB_HOST="${DB_HOST:-your-rds-endpoint.amazonaws.com}"
DB_NAME="${DB_NAME:-health_notifier}"
DB_USER="${DB_USER:-admin}"
DB_PASS="${DB_PASS:-your-password}"
BACKUP_DIR="${BACKUP_DIR:-/home/appuser/backups}"
S3_BUCKET="${S3_BUCKET:-your-backup-bucket}"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="health_notifier_${DATE}.sql"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if required variables are set
if [ "$DB_HOST" = "your-rds-endpoint.amazonaws.com" ]; then
    print_error "Please set DB_HOST environment variable"
    exit 1
fi

if [ "$DB_PASS" = "your-password" ]; then
    print_error "Please set DB_PASS environment variable"
    exit 1
fi

print_status "Starting database backup..."
print_status "Database: $DB_HOST"
print_status "Backup file: $BACKUP_FILE"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create database backup
print_status "Creating database dump..."
if mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME > $BACKUP_DIR/$BACKUP_FILE; then
    print_status "Database dump created successfully"
else
    print_error "Failed to create database dump"
    exit 1
fi

# Compress backup
print_status "Compressing backup..."
gzip $BACKUP_DIR/$BACKUP_FILE
BACKUP_FILE="${BACKUP_FILE}.gz"

# Upload to S3 (if S3_BUCKET is set)
if [ "$S3_BUCKET" != "your-backup-bucket" ]; then
    print_status "Uploading to S3..."
    if aws s3 cp $BACKUP_DIR/$BACKUP_FILE s3://$S3_BUCKET/database/; then
        print_status "Backup uploaded to S3 successfully"
    else
        print_warning "Failed to upload backup to S3"
    fi
else
    print_warning "S3_BUCKET not set, skipping S3 upload"
fi

# Keep only last 7 days of backups locally
print_status "Cleaning up old backups..."
find $BACKUP_DIR -name "health_notifier_*.sql.gz" -mtime +7 -delete

# Get backup size
BACKUP_SIZE=$(du -h $BACKUP_DIR/$BACKUP_FILE | cut -f1)
print_status "Backup completed: $BACKUP_FILE (Size: $BACKUP_SIZE)"

# Send notification (optional)
if command -v mail &> /dev/null; then
    echo "Health Notifier database backup completed successfully at $(date)" | \
    mail -s "Health Notifier Backup Success" admin@yourdomain.com
fi

print_status "✅ Backup process completed successfully!"

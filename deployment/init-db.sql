-- Initialize Health Notifier Database
-- This script runs when MySQL container starts for the first time

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS health_notifier CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Use the database
USE health_notifier;

-- Create patients table
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age INT NOT NULL,
    pregnancy_icd10 VARCHAR(20),
    pregnancy_description TEXT,
    comorbidity_icd10 VARCHAR(20),
    comorbidity_description TEXT,
    weeks_pregnant INT,
    address TEXT,
    zip_code VARCHAR(20) NOT NULL,
    phone_number VARCHAR(20),
    email VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_zip_code (zip_code),
    INDEX idx_weeks_pregnant (weeks_pregnant),
    INDEX idx_pregnancy_icd10 (pregnancy_icd10),
    INDEX idx_comorbidity_icd10 (comorbidity_icd10),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create risk assessments table
CREATE TABLE IF NOT EXISTS risk_assessments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    risk_level ENUM('low', 'medium', 'high') NOT NULL,
    heat_wave_risk BOOLEAN DEFAULT FALSE,
    risk_factors TEXT,
    risk_score INT DEFAULT 0,
    weather_data TEXT,
    assessment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_risk_level (risk_level),
    INDEX idx_assessment_date (assessment_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    message TEXT NOT NULL,
    risk_level ENUM('low', 'medium', 'high') NOT NULL,
    notification_type ENUM('heat_warning', 'general_health', 'appointment_reminder') DEFAULT 'general_health',
    sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    read_status BOOLEAN DEFAULT FALSE,
    read_at DATETIME NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_risk_level (risk_level),
    INDEX idx_read_status (read_status),
    INDEX idx_sent_at (sent_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create health facilities table
CREATE TABLE IF NOT EXISTS health_facilities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    facility_id VARCHAR(20) UNIQUE NOT NULL,
    facility_name VARCHAR(200) NOT NULL,
    short_description VARCHAR(50),
    description VARCHAR(200),
    facility_open_date DATE,
    facility_address_1 VARCHAR(200),
    facility_address_2 VARCHAR(200),
    facility_city VARCHAR(100),
    facility_state VARCHAR(50),
    facility_zip_code VARCHAR(20),
    facility_phone_number VARCHAR(20),
    facility_fax_number VARCHAR(20),
    facility_website VARCHAR(200),
    facility_county_code VARCHAR(10),
    facility_county VARCHAR(100),
    regional_office_id VARCHAR(10),
    regional_office VARCHAR(100),
    main_site_name VARCHAR(200),
    main_site_facility_id VARCHAR(20),
    operating_certificate_number VARCHAR(50),
    operator_name VARCHAR(200),
    operator_address_1 VARCHAR(200),
    operator_address_2 VARCHAR(200),
    operator_city VARCHAR(100),
    operator_state VARCHAR(50),
    operator_zip_code VARCHAR(20),
    cooperator_name VARCHAR(200),
    cooperator_address VARCHAR(200),
    cooperator_address_2 VARCHAR(200),
    cooperator_city VARCHAR(100),
    cooperator_state VARCHAR(50),
    cooperator_zip_code VARCHAR(20),
    ownership_type VARCHAR(100),
    facility_latitude FLOAT,
    facility_longitude FLOAT,
    facility_location VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_facility_id (facility_id),
    INDEX idx_short_description (short_description),
    INDEX idx_facility_city (facility_city),
    INDEX idx_facility_state (facility_state),
    INDEX idx_facility_county (facility_county),
    INDEX idx_facility_phone (facility_phone_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create emergency notifications table
CREATE TABLE IF NOT EXISTS emergency_notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    health_facility_id INT NOT NULL,
    risk_level ENUM('low', 'medium', 'high') NOT NULL,
    notification_type ENUM('patient_notification', 'doctor_call', 'emergency_alert') NOT NULL,
    message TEXT NOT NULL,
    status ENUM('pending', 'sent', 'delivered', 'failed') DEFAULT 'pending',
    priority ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    sent_at DATETIME NULL,
    delivered_at DATETIME NULL,
    response_received BOOLEAN DEFAULT FALSE,
    response_message TEXT,
    response_received_at DATETIME NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (health_facility_id) REFERENCES health_facilities(id) ON DELETE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_health_facility_id (health_facility_id),
    INDEX idx_risk_level (risk_level),
    INDEX idx_status (status),
    INDEX idx_priority (priority),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert sample data
INSERT INTO patients (name, age, pregnancy_icd10, pregnancy_description, comorbidity_icd10, comorbidity_description, weeks_pregnant, address, zip_code, phone_number, email) VALUES
('Анна Петрова', 25, 'O24.4', 'Gestational diabetes mellitus', 'I10', 'Essential hypertension', 20, '123 Main St, Moscow', '101000', '+7-999-111-22-33', 'anna@example.com'),
('Елена Смирнова', 32, 'O13', 'Gestational hypertension', 'E03.9', 'Hypothyroidism, unspecified', 28, '456 Oak Ave, St. Petersburg', '190000', '+7-999-444-55-66', 'elena@example.com'),
('Мария Козлова', 22, 'O26.9', 'Pregnancy-related condition, unspecified', NULL, NULL, 12, '789 Pine St, Novosibirsk', '630000', '+7-999-777-88-99', 'maria@example.com');

-- Create a user for the application
CREATE USER IF NOT EXISTS 'healthuser'@'%' IDENTIFIED BY 'healthpassword';
GRANT ALL PRIVILEGES ON health_notifier.* TO 'healthuser'@'%';
FLUSH PRIVILEGES;

-- Show tables
SHOW TABLES;

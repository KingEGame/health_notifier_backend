from flask import Flask
from app.extensions import db, migrate, cors
import sys
import os
import logging
from logging.handlers import RotatingFileHandler

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import config

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Configure logging
    configure_logging(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    
    # Register blueprints
    from app.api import api_bp
    from app.api.csv_risk_patients import csv_risk_patients_bp
    from app.api.health import health_bp
    from app.api.csv_patients import csv_patients_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(csv_risk_patients_bp, url_prefix='/api')
    app.register_blueprint(health_bp, url_prefix='/api')
    app.register_blueprint(csv_patients_bp, url_prefix='/api')
    
    # Register error handlers
    from app.errors import register_error_handlers
    register_error_handlers(app)
    
    return app

def configure_logging(app):
    """Configure logging for the application"""
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File handler with rotation
        file_handler = RotatingFileHandler(
            f'logs/{app.config["LOG_FILE"]}', 
            maxBytes=10240000,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
        file_handler.setLevel(getattr(logging, app.config['LOG_LEVEL'].upper()))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(app.config['LOG_FORMAT']))
        console_handler.setLevel(getattr(logging, app.config['LOG_LEVEL'].upper()))
        
        # Add handlers to app logger
        app.logger.addHandler(file_handler)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(getattr(logging, app.config['LOG_LEVEL'].upper()))
        
        # Set specific loggers
        logging.getLogger('werkzeug').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.engine').setLevel(logging.WARNING)
        
        app.logger.info('Health Notifier application started')
    else:
        # Development mode - simple console logging
        logging.basicConfig(
            level=getattr(logging, app.config['LOG_LEVEL'].upper()),
            format=app.config['LOG_FORMAT']
        )
        app.logger.info('Health Notifier application started in development mode')

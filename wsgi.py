#!/usr/bin/env python3
"""
WSGI entry point for production deployment
"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Create application instance
application = create_app(os.environ.get('FLASK_ENV', 'production'))

if __name__ == "__main__":
    application.run()

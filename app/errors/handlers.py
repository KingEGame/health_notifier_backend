from flask import jsonify
from marshmallow import ValidationError
from app.utils.exceptions import ValidationException, ExternalAPIException, DatabaseException

def register_error_handlers(app):
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({
            'error': 'Validation failed',
            'details': error.messages
        }), 400
    
    @app.errorhandler(ValidationException)
    def handle_custom_validation_error(error):
        return jsonify({
            'error': str(error),
            'details': error.errors
        }), 400
    
    @app.errorhandler(ExternalAPIException)
    def handle_external_api_error(error):
        return jsonify({
            'error': 'External service unavailable',
            'message': str(error)
        }), 503
    
    @app.errorhandler(DatabaseException)
    def handle_database_error(error):
        return jsonify({
            'error': 'Database error',
            'message': str(error)
        }), 500
    
    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'error': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        return jsonify({
            'error': 'Internal server error'
        }), 500

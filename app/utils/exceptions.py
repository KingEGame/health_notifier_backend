class HealthNotifierException(Exception):
    """Базовое исключение для Health Notifier"""
    pass

class ValidationException(HealthNotifierException):
    """Исключение для ошибок валидации"""
    def __init__(self, message, errors=None):
        super().__init__(message)
        self.errors = errors or {}

class ExternalAPIException(HealthNotifierException):
    """Исключение для ошибок внешних API"""
    pass

class DatabaseException(HealthNotifierException):
    """Исключение для ошибок базы данных"""
    pass

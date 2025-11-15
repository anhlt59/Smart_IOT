"""Base exception classes"""


class DomainException(Exception):
    """Base exception for domain layer"""

    def __init__(self, message: str, code: str = 'DOMAIN_ERROR'):
        self.message = message
        self.code = code
        super().__init__(self.message)


class InfrastructureException(Exception):
    """Base exception for infrastructure layer"""

    def __init__(self, message: str, code: str = 'INFRASTRUCTURE_ERROR'):
        self.message = message
        self.code = code
        super().__init__(self.message)


# Domain Exceptions
class DeviceNotFoundError(DomainException):
    """Device not found"""

    def __init__(self, device_id: str):
        super().__init__(f"Device {device_id} not found", "DEVICE_NOT_FOUND")


class AlertNotFoundError(DomainException):
    """Alert not found"""

    def __init__(self, alert_id: str):
        super().__init__(f"Alert {alert_id} not found", "ALERT_NOT_FOUND")


class UserNotFoundError(DomainException):
    """User not found"""

    def __init__(self, user_id: str):
        super().__init__(f"User {user_id} not found", "USER_NOT_FOUND")


class UnauthorizedError(DomainException):
    """Unauthorized access"""

    def __init__(self, message: str = "Unauthorized"):
        super().__init__(message, "UNAUTHORIZED")


class ValidationError(DomainException):
    """Validation error"""

    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, "VALIDATION_ERROR")


# Infrastructure Exceptions
class DatabaseError(InfrastructureException):
    """Database error"""

    def __init__(self, message: str):
        super().__init__(message, "DATABASE_ERROR")


class ExternalServiceError(InfrastructureException):
    """External service error"""

    def __init__(self, service: str, message: str):
        super().__init__(f"{service}: {message}", "EXTERNAL_SERVICE_ERROR")

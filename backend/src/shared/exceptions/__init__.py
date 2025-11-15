# Exceptions
from .base import (
    DomainException,
    InfrastructureException,
    DeviceNotFoundError,
    AlertNotFoundError,
    UserNotFoundError,
    UnauthorizedError,
    ValidationError,
    DatabaseError,
    ExternalServiceError
)

__all__ = [
    'DomainException',
    'InfrastructureException',
    'DeviceNotFoundError',
    'AlertNotFoundError',
    'UserNotFoundError',
    'UnauthorizedError',
    'ValidationError',
    'DatabaseError',
    'ExternalServiceError'
]

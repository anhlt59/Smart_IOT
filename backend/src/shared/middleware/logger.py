"""Structured logging for Lambda functions"""
import logging
import json
from datetime import datetime
from typing import Dict, Any


def setup_logger(name: str, level: str = 'INFO') -> logging.Logger:
    """Setup structured logger for Lambda"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))

    # Create console handler if not already present
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)

    return logger


class StructuredFormatter(logging.Formatter):
    """Structured JSON logging formatter"""

    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'message': record.getMessage(),
            'logger': record.name,
            'function': record.funcName,
            'line': record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, 'extra'):
            log_data.update(record.extra)

        return json.dumps(log_data)


# Default logger instance
logger = setup_logger('iot-monitoring')

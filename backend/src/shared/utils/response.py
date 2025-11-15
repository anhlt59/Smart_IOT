"""Response Utilities for Lambda Functions"""
import json
from datetime import datetime
from typing import Any, Dict, Optional


def success_response(
    data: Any,
    message: Optional[str] = None,
    status_code: int = 200
) -> Dict[str, Any]:
    """Create a successful API response"""
    body = {
        'success': True,
        'data': data,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

    if message:
        body['message'] = message

    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body)
    }


def error_response(
    code: str,
    message: str,
    details: Optional[Any] = None,
    status_code: int = 500
) -> Dict[str, Any]:
    """Create an error API response"""
    body = {
        'success': False,
        'error': {
            'code': code,
            'message': message
        },
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }

    if details:
        body['error']['details'] = details

    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,Authorization',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(body)
    }

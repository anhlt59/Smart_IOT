"""Get Device Lambda Handler"""
import json
from typing import Dict, Any

from ...shared.middleware.logger import logger
from ...shared.exceptions.base import DeviceNotFoundError, UnauthorizedError


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for GET /devices/{deviceId}"""
    try:
        # Extract deviceId from path parameters
        device_id = event.get('pathParameters', {}).get('deviceId')

        if not device_id:
            raise ValueError("Device ID is required")

        # Extract user context
        user_context = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        organization_id = user_context.get('custom:organizationId')

        # In production: fetch device from repository
        # device = device_repository.find_by_id(device_id)
        # Verify user has access to device's organization

        logger.info(f"Retrieved device: {device_id}")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'deviceId': device_id,
                'name': 'Sample Device',
                'status': 'online',
                'organizationId': organization_id
            })
        }

    except DeviceNotFoundError as e:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': {'code': e.code, 'message': e.message}})
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'}})
        }

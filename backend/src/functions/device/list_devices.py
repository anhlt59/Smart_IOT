"""List Devices Lambda Handler"""
import json
from typing import Dict, Any

from ...shared.middleware.logger import logger
from ...shared.config.settings import settings


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for GET /devices"""
    try:
        # Extract query parameters
        query_params = event.get('queryStringParameters') or {}
        page = int(query_params.get('page', 1))
        page_size = int(query_params.get('pageSize', settings.PAGE_SIZE_DEFAULT))

        # Extract user context
        user_context = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        organization_id = user_context.get('custom:organizationId')

        # In production: fetch devices from repository
        # devices = device_repository.find_by_organization(organization_id, filters, page, page_size)

        logger.info(f"Listed devices for organization: {organization_id}")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'items': [],
                'pagination': {
                    'page': page,
                    'pageSize': page_size,
                    'totalItems': 0,
                    'totalPages': 0,
                    'hasNext': False,
                    'hasPrevious': False
                }
            })
        }

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'}})
        }

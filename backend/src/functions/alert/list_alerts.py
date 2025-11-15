"""List Alerts Lambda Handler"""
import json
from typing import Dict, Any

from ...shared.middleware.logger import logger


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for GET /alerts"""
    try:
        # Extract query parameters
        query_params = event.get('queryStringParameters') or {}
        status = query_params.get('status')
        severity = query_params.get('severity')

        # Extract user context
        user_context = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        organization_id = user_context.get('custom:organizationId')

        # In production: fetch alerts from repository
        # alerts = alert_repository.find_alerts(organization_id, filters)

        logger.info(f"Listed alerts for organization: {organization_id}")

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({
                'items': [],
                'pagination': {
                    'page': 1,
                    'pageSize': 25,
                    'totalItems': 0,
                    'totalPages': 0
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

"""WebSocket Disconnect Handler"""
import json
from typing import Dict, Any

from ...shared.middleware.logger import logger


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle WebSocket disconnection

    Processing Steps:
    1. Remove connection from DynamoDB
    2. Clean up subscriptions
    3. Return success
    """
    try:
        connection_id = event.get('requestContext', {}).get('connectionId')

        # In production:
        # connections_table.delete_item(Key={'connectionId': connection_id})

        logger.info(f"WebSocket disconnected: {connection_id}")

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Disconnected'})
        }

    except Exception as e:
        logger.error(f"Disconnection error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to disconnect'})
        }

"""WebSocket Subscribe Handler"""
import json
from typing import Dict, Any

from ...shared.middleware.logger import logger


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Handle WebSocket subscription to device updates

    Message format:
    {
        "action": "subscribe",
        "deviceIds": ["dev-abc123", "dev-def456"]
    }
    """
    try:
        connection_id = event.get('requestContext', {}).get('connectionId')
        body = json.loads(event.get('body', '{}'))
        device_ids = body.get('deviceIds', [])

        # In production:
        # 1. Validate user has access to devices
        # 2. Update connection record with subscriptions
        # connections_table.update_item(
        #     Key={'connectionId': connection_id},
        #     UpdateExpression='SET subscribedDevices = :devices',
        #     ExpressionAttributeValues={':devices': device_ids}
        # )

        logger.info(f"Subscribed to devices: {device_ids}")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Subscribed',
                'deviceIds': device_ids
            })
        }

    except Exception as e:
        logger.error(f"Subscribe error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Failed to subscribe'})
        }

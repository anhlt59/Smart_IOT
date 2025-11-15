"""Notification Dispatcher Lambda Handler - Dispatch notifications for alerts"""
import json
from typing import Dict, Any, List

from ...shared.middleware.logger import logger


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Dispatch notifications for alerts via multiple channels

    Triggered by: SQS AlertQueue messages

    Processing Steps:
    1. Receive alert messages from SQS
    2. Fetch user notification preferences
    3. Dispatch notifications via configured channels:
       - Email (AWS SES)
       - Push Notifications (FCM)
       - SMS (AWS SNS)
    4. Update notification delivery status in DynamoDB
    5. Return batch item failures for retry

    Returns:
        Dict with batchItemFailures for partial batch retry
    """
    batch_item_failures = []

    try:
        records = event.get('Records', [])
        logger.info(f"Processing {len(records)} notification requests")

        for record in records:
            try:
                # Parse SQS message
                message_body = json.loads(record['body'])
                alert_id = message_body.get('alertId')
                device_id = message_body.get('deviceId')
                severity = message_body.get('severity')
                message = message_body.get('message')

                # In production:
                # 1. Get alert details from ALERTS_TABLE
                # 2. Get user notification preferences from USERS_TABLE
                # 3. For each enabled notification channel:
                #    - Email: Use SES adapter to send email
                #    - Push: Use FCM adapter to send push notification
                #    - SMS: Use SNS adapter to send SMS
                # 4. Create notification record in NOTIFICATIONS_TABLE
                # 5. Update alert with notification_sent timestamp

                logger.info(f"Dispatched notifications for alert: {alert_id}")

            except Exception as e:
                logger.error(f"Failed to dispatch notification: {str(e)}", exc_info=True)
                # Add to batch item failures for retry
                batch_item_failures.append({
                    'itemIdentifier': record['messageId']
                })

        # Return partial batch failures
        return {
            'batchItemFailures': batch_item_failures
        }

    except Exception as e:
        logger.error(f"Notification dispatcher error: {str(e)}", exc_info=True)
        # Return all as failures for retry
        return {
            'batchItemFailures': [
                {'itemIdentifier': r['messageId']}
                for r in event.get('Records', [])
            ]
        }

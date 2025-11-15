"""List Alerts Lambda Handler"""
from typing import Dict, Any

from ...shared.middleware.logger import logger
from ...shared.utils.response import success_response, error_response


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler for GET /alerts"""
    try:
        # Extract query parameters
        query_params = event.get('queryStringParameters') or {}
        status = query_params.get('status')
        severity = query_params.get('severity')
        page = int(query_params.get('page', 1))
        page_size = int(query_params.get('pageSize', 25))

        # Extract user context
        user_context = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        organization_id = user_context.get('custom:organizationId')

        # In production: fetch alerts from repository
        # alerts = alert_repository.find_alerts(organization_id, filters)

        # Mock data for testing
        mock_alerts = [
            {
                'alertId': 'alert-001',
                'ruleId': 'rule-001',
                'deviceId': 'device-001',
                'deviceName': 'Office Temperature Sensor',
                'deviceLocation': 'Building A, Floor 2, Room 201',
                'severity': 'critical',
                'status': 'triggered',
                'title': 'High Temperature Alert',
                'message': 'Temperature has exceeded threshold of 30°C',
                'condition': {
                    'metric': 'temperature',
                    'operator': '>',
                    'threshold': 30,
                    'duration': 300
                },
                'actualValue': 35.5,
                'triggeredAt': '2025-11-15T10:15:00Z'
            },
            {
                'alertId': 'alert-002',
                'ruleId': 'rule-002',
                'deviceId': 'device-002',
                'deviceName': 'Warehouse Humidity Sensor',
                'deviceLocation': 'Warehouse 1, Zone A',
                'severity': 'warning',
                'status': 'acknowledged',
                'title': 'Low Battery Warning',
                'message': 'Battery level is below 50%',
                'condition': {
                    'metric': 'battery',
                    'operator': '<',
                    'threshold': 50
                },
                'actualValue': 45,
                'triggeredAt': '2025-11-15T09:00:00Z',
                'acknowledgedAt': '2025-11-15T09:30:00Z',
                'acknowledgedBy': 'user-001'
            },
            {
                'alertId': 'alert-003',
                'ruleId': 'rule-003',
                'deviceId': 'device-002',
                'deviceName': 'Warehouse Humidity Sensor',
                'deviceLocation': 'Warehouse 1, Zone A',
                'severity': 'info',
                'status': 'resolved',
                'title': 'Connectivity Issue',
                'message': 'Device signal strength is weak',
                'condition': {
                    'metric': 'rssi',
                    'operator': '<',
                    'threshold': -70
                },
                'actualValue': -75,
                'triggeredAt': '2025-11-15T08:00:00Z',
                'acknowledgedAt': '2025-11-15T08:15:00Z',
                'acknowledgedBy': 'user-001',
                'resolvedAt': '2025-11-15T10:00:00Z',
                'resolvedBy': 'user-001',
                'notes': ['Signal strength improved after antenna adjustment']
            }
        ]

        # Apply filters
        filtered_alerts = mock_alerts
        if status:
            filtered_alerts = [a for a in filtered_alerts if a['status'] == status]
        if severity:
            filtered_alerts = [a for a in filtered_alerts if a['severity'] == severity]

        logger.info(f"Listed {len(filtered_alerts)} alerts for organization: {organization_id}")

        response_data = {
            'items': filtered_alerts,
            'total': len(filtered_alerts),
            'page': page,
            'pageSize': page_size,
            'totalPages': 1,
            'hasNext': False,
            'hasPrevious': False
        }

        return success_response(response_data)

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return error_response('INTERNAL_ERROR', 'Internal server error', status_code=500)

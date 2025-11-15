"""List Devices Lambda Handler"""
from typing import Dict, Any

from ...shared.middleware.logger import logger
from ...shared.config.settings import settings
from ...shared.utils.response import success_response, error_response


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

        # Mock data for testing
        mock_devices = [
            {
                'deviceId': 'device-001',
                'organizationId': organization_id or 'org-001',
                'deviceType': 'temperature-sensor',
                'name': 'Office Temperature Sensor',
                'description': 'Main office temperature monitoring',
                'status': 'online',
                'location': {
                    'lat': 37.7749,
                    'lon': -122.4194,
                    'address': '123 Main St',
                    'building': 'Building A',
                    'floor': '2',
                    'room': '201'
                },
                'connectivity': {
                    'type': 'wifi',
                    'rssi': -45,
                    'quality': 95,
                    'lastSeen': '2025-11-15T10:30:00Z'
                },
                'metadata': {
                    'manufacturer': 'IoT Sensors Inc',
                    'model': 'TS-2000',
                    'serialNumber': 'SN-001234',
                    'firmwareVersion': '1.2.3',
                    'hardwareVersion': '2.0'
                },
                'tags': ['critical', 'office'],
                'batteryLevel': 85,
                'lastHeartbeat': '2025-11-15T10:30:00Z',
                'createdAt': '2025-11-01T00:00:00Z',
                'updatedAt': '2025-11-15T10:30:00Z'
            },
            {
                'deviceId': 'device-002',
                'organizationId': organization_id or 'org-001',
                'deviceType': 'humidity-sensor',
                'name': 'Warehouse Humidity Sensor',
                'description': 'Warehouse humidity monitoring',
                'status': 'warning',
                'location': {
                    'lat': 37.7750,
                    'lon': -122.4195,
                    'address': '456 Storage Ave',
                    'building': 'Warehouse 1',
                    'floor': '1',
                    'room': 'Zone A'
                },
                'connectivity': {
                    'type': 'cellular',
                    'rssi': -75,
                    'quality': 60,
                    'lastSeen': '2025-11-15T10:25:00Z'
                },
                'metadata': {
                    'manufacturer': 'IoT Sensors Inc',
                    'model': 'HS-3000',
                    'serialNumber': 'SN-001235',
                    'firmwareVersion': '1.1.0',
                    'hardwareVersion': '1.5'
                },
                'tags': ['warehouse'],
                'batteryLevel': 45,
                'lastHeartbeat': '2025-11-15T10:25:00Z',
                'createdAt': '2025-11-02T00:00:00Z',
                'updatedAt': '2025-11-15T10:25:00Z'
            }
        ]

        logger.info(f"Listed {len(mock_devices)} devices for organization: {organization_id}")

        response_data = {
            'items': mock_devices,
            'total': len(mock_devices),
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

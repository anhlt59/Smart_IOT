"""Register Device Lambda Handler"""
import json
import uuid
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel, Field

from ...shared.middleware.logger import logger
from ...shared.exceptions.base import ValidationError, UnauthorizedError
from ...domain.entities.device import Device, DeviceLocation, Connectivity, DeviceStatus


# Request/Response Schemas
class RegisterDeviceRequest(BaseModel):
    """Request schema for device registration"""
    device_type: str = Field(..., alias='deviceType')
    name: str
    location: DeviceLocation
    connectivity: Connectivity
    metadata: Dict = Field(default_factory=dict)
    tags: list = Field(default_factory=list)

    class Config:
        populate_by_name = True


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Lambda handler for POST /devices - Register new IoT device

    Following hexagonal architecture:
    - This is an Adapter (API Handler - Driving Adapter)
    - Parses HTTP request
    - Calls Domain Service
    - Formats HTTP response
    """
    try:
        # 1. Parse and validate request
        body = json.loads(event.get('body', '{}'))
        request_data = RegisterDeviceRequest(**body)

        # 2. Extract user context from authorizer
        user_context = event.get('requestContext', {}).get('authorizer', {}).get('claims', {})
        user_id = user_context.get('sub')
        organization_id = user_context.get('custom:organizationId')

        if not organization_id:
            raise UnauthorizedError("Organization ID not found in token")

        # 3. Create Device Entity (Domain Layer)
        device = Device(
            deviceId=f"dev-{uuid.uuid4().hex[:12]}",
            organizationId=organization_id,
            deviceType=request_data.device_type,
            name=request_data.name,
            status=DeviceStatus.REGISTERED,
            location=request_data.location,
            connectivity=request_data.connectivity,
            metadata=request_data.metadata,
            tags=request_data.tags,
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow()
        )

        # 4. Save via Repository (would inject repository in production)
        # device_repository.save(device)
        # iot_core_provider.create_thing(device)
        # iot_core_provider.create_certificates(device)

        logger.info(f"Device registered successfully: {device.device_id}")

        # 5. Format HTTP Response
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                **device.model_dump(by_alias=True),
                'provisioningCredentials': {
                    'endpoint': 'a1b2c3d4e5.iot.us-east-1.amazonaws.com',
                    'certificateArn': f'arn:aws:iot:us-east-1:123456789012:cert/{uuid.uuid4()}',
                    # In production, return actual credentials
                }
            }, default=str)
        }

    except ValidationError as e:
        logger.warning(f"Validation error: {e.message}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': {'code': e.code, 'message': e.message}})
        }

    except UnauthorizedError as e:
        logger.warning(f"Unauthorized: {e.message}")
        return {
            'statusCode': 403,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': {'code': e.code, 'message': e.message}})
        }

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': {'code': 'INTERNAL_ERROR', 'message': 'Internal server error'}})
        }

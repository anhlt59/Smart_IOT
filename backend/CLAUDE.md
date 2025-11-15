# CLAUDE.md - Backend (Serverless Python)

**AI Assistant Guide for Smart_IOT Backend Development**

This document provides comprehensive guidance for AI assistants working on the Python serverless backend of the Smart_IOT platform. It covers hexagonal architecture, Lambda best practices, AWS service integration, and backend-specific workflows.

---

## Table of Contents

1. [Backend Overview](#backend-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Hexagonal Architecture](#hexagonal-architecture)
5. [Development Workflow](#development-workflow)
6. [Common Tasks](#common-tasks)
7. [Code Conventions](#code-conventions)
8. [Lambda Function Patterns](#lambda-function-patterns)
9. [AWS Service Integration](#aws-service-integration)
10. [Error Handling](#error-handling)
11. [Testing](#testing)
12. [Deployment](#deployment)
13. [Performance & Optimization](#performance--optimization)
14. [Troubleshooting](#troubleshooting)

---

## Backend Overview

### What We're Building

The Smart_IOT backend is a **serverless event-driven architecture** running on AWS Lambda that provides:
- RESTful API for device and alert management
- Real-time data ingestion from IoT devices
- Stream processing for sensor data
- Alert evaluation and notification dispatch
- Firmware update orchestration
- Analytics and reporting

### Architecture Style

**Hexagonal Architecture (Ports & Adapters)**
- Clear separation between business logic and infrastructure
- Easy to test (mock infrastructure)
- Easy to change infrastructure (e.g., DynamoDB → PostgreSQL)
- Technology-agnostic domain layer

### Current Status

**✅ Implemented:**
- Serverless Framework infrastructure
- Lambda functions for device and alert APIs
- Hexagonal architecture foundation
- Mock data repositories
- CORS-enabled API responses
- Logging middleware
- Error handling

**🚧 In Progress:**
- Real DynamoDB integration
- Timestream sensor data storage
- Kinesis stream processing
- Alert evaluation engine
- Notification dispatch (SES, FCM)

**📋 Planned:**
- WebSocket real-time updates
- Cognito authentication
- Firmware update orchestration
- Advanced analytics

---

## Tech Stack

### Core Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime language |
| Serverless Framework | 3.x+ | Infrastructure as Code |
| AWS Lambda | - | Serverless compute |

### Python Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| boto3 | 1.34.0 | AWS SDK for Python |
| pydantic | 2.5.0 | Data validation and settings |
| aws-xray-sdk | 2.12.0 | Distributed tracing |
| firebase-admin | 6.3.0 | Push notifications |

### Testing & Quality

| Tool | Version | Purpose |
|------|---------|---------|
| pytest | 7.4.3 | Testing framework |
| pytest-cov | 4.1.0 | Coverage reporting |
| pytest-mock | 3.12.0 | Mocking utilities |
| moto | 4.2.9 | AWS service mocking |
| black | 23.12.0 | Code formatting |
| flake8 | 6.1.0 | Linting |
| mypy | 1.7.1 | Type checking |

### AWS Services

| Service | Purpose |
|---------|---------|
| AWS Lambda | Serverless compute |
| API Gateway | REST API endpoints |
| DynamoDB | NoSQL database for metadata |
| Timestream | Time-series sensor data |
| Kinesis | Real-time data streaming |
| SQS | Asynchronous message queues |
| IoT Core | Device connectivity |
| S3 | Firmware and export storage |
| Cognito | User authentication |
| SES | Email notifications |
| CloudWatch | Logging and monitoring |
| X-Ray | Distributed tracing |

---

## Project Structure

```
backend/
├── src/
│   ├── domain/                          # CORE - Business logic (hexagon core)
│   │   ├── entities/                    # Domain entities
│   │   │   ├── device.py                # Device entity
│   │   │   ├── alert.py                 # Alert entity
│   │   │   ├── user.py                  # User entity
│   │   │   └── firmware.py              # Firmware entity
│   │   │
│   │   ├── value_objects/               # Immutable value objects
│   │   │   ├── device_location.py       # GPS coordinates, address
│   │   │   ├── alert_severity.py        # Severity levels
│   │   │   └── firmware_version.py      # Version numbering
│   │   │
│   │   ├── services/                    # Domain services (business rules)
│   │   │   ├── device_service.py        # Device business logic
│   │   │   ├── alert_service.py         # Alert evaluation logic
│   │   │   └── notification_service.py  # Notification rules
│   │   │
│   │   └── ports/                       # Interfaces (contracts)
│   │       ├── device_repository.py     # Device repository interface
│   │       ├── alert_repository.py      # Alert repository interface
│   │       └── notification_port.py     # Notification sender interface
│   │
│   ├── infrastructure/                  # ADAPTERS - External services
│   │   ├── repositories/                # Database implementations
│   │   │   ├── device_repository_impl.py        # DynamoDB device repo
│   │   │   ├── alert_repository_impl.py         # DynamoDB alert repo
│   │   │   └── sensor_data_repository_impl.py   # Timestream sensor data
│   │   │
│   │   ├── messaging/                   # Message queue clients
│   │   │   ├── sqs_client.py            # SQS wrapper
│   │   │   └── kinesis_client.py        # Kinesis wrapper
│   │   │
│   │   └── external_services/           # Third-party integrations
│   │       ├── ses_client.py            # Email via SES
│   │       ├── fcm_client.py            # Push notifications via FCM
│   │       └── s3_client.py             # File storage
│   │
│   ├── functions/                       # APPLICATION LAYER - Lambda handlers
│   │   ├── device/                      # Device management
│   │   │   ├── register_device.py       # POST /devices
│   │   │   ├── get_device.py            # GET /devices/{id}
│   │   │   ├── list_devices.py          # GET /devices
│   │   │   ├── update_device.py         # PUT /devices/{id}
│   │   │   ├── delete_device.py         # DELETE /devices/{id}
│   │   │   └── get_device_history.py    # GET /devices/{id}/history
│   │   │
│   │   ├── alert/                       # Alert management
│   │   │   ├── list_alerts.py           # GET /alerts
│   │   │   ├── get_alert.py             # GET /alerts/{id}
│   │   │   ├── acknowledge_alert.py     # POST /alerts/{id}/acknowledge
│   │   │   └── resolve_alert.py         # POST /alerts/{id}/resolve
│   │   │
│   │   ├── user/                        # User management
│   │   │   ├── get_profile.py           # GET /users/me
│   │   │   └── update_preferences.py    # PUT /users/me/preferences
│   │   │
│   │   ├── firmware/                    # Firmware updates (FOTA)
│   │   │   ├── upload_firmware.py       # POST /firmware/upload
│   │   │   ├── create_deployment.py     # POST /firmware/deployments
│   │   │   └── get_deployment_status.py # GET /firmware/deployments/{id}
│   │   │
│   │   ├── analytics/                   # Analytics and reports
│   │   │   ├── dashboard_stats.py       # GET /analytics/dashboard
│   │   │   └── query_sensor_data.py     # POST /analytics/query
│   │   │
│   │   ├── stream_processing/           # Event-driven processors
│   │   │   ├── kinesis_consumer.py      # Process sensor data stream
│   │   │   ├── alert_evaluator.py       # Evaluate alert rules
│   │   │   └── notification_dispatcher.py # Send notifications
│   │   │
│   │   └── websocket/                   # WebSocket handlers
│   │       ├── connect.py               # $connect
│   │       ├── disconnect.py            # $disconnect
│   │       └── subscribe.py             # Subscribe to updates
│   │
│   └── shared/                          # Cross-cutting concerns
│       ├── config/                      # Configuration
│       │   └── environment.py           # Environment variables
│       │
│       ├── middleware/                  # Middleware
│       │   └── logger.py                # Centralized logging
│       │
│       ├── utils/                       # Utilities
│       │   ├── response.py              # Response helpers
│       │   └── validation.py            # Input validation
│       │
│       └── exceptions/                  # Custom exceptions
│           └── custom_exceptions.py     # Domain exceptions
│
├── tests/                               # Test suites
│   ├── unit/                            # Unit tests
│   │   ├── domain/                      # Test domain logic
│   │   │   ├── test_device_service.py
│   │   │   └── test_alert_service.py
│   │   └── functions/                   # Test Lambda handlers
│   │       └── device/
│   │           └── test_get_device.py
│   │
│   ├── integration/                     # Integration tests
│   │   └── repositories/
│   │       └── test_device_repository.py
│   │
│   └── e2e/                             # End-to-end tests
│       └── test_device_api.py
│
├── serverless.yml                       # Infrastructure as Code
├── requirements.txt                     # Python dependencies
├── package.json                         # Serverless dependencies
└── CLAUDE.md                            # This file
```

---

## Hexagonal Architecture

### Layers and Dependencies

```
┌─────────────────────────────────────────────────────────────┐
│                   Application Layer                         │
│            (Lambda Handlers - functions/)                    │
│  - Receives HTTP/Event inputs                               │
│  - Orchestrates domain services                             │
│  - Returns responses                                        │
└────────────────────┬────────────────────────────────────────┘
                     │ depends on ↓
┌────────────────────▼────────────────────────────────────────┐
│                    Domain Layer (CORE)                       │
│              (domain/ - No external deps)                    │
│                                                              │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────┐       │
│  │  Entities    │  │   Services  │  │ Ports (I/F)  │       │
│  │ Device, Alert│  │Business Logic│ │ Repositories │       │
│  └──────────────┘  └─────────────┘  └──────────────┘       │
└─────────────────────────────────────────▲───────────────────┘
                                          │ implements
┌──────────────────────────────────────────┴──────────────────┐
│                Infrastructure Layer (ADAPTERS)               │
│              (infrastructure/ - External deps)               │
│                                                              │
│  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐  │
│  │ Repositories   │  │   Messaging    │  │   External   │  │
│  │ DynamoDB, etc. │  │  SQS, Kinesis  │  │  SES, FCM    │  │
│  └────────────────┘  └────────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Dependency Rule

**CRITICAL:** Dependencies always point **inward** (toward domain).

**✅ Allowed:**
- Application → Domain
- Infrastructure → Domain
- Application → Infrastructure

**❌ Forbidden:**
- Domain → Infrastructure
- Domain → Application

### Benefits

1. **Testability:** Test business logic without AWS
2. **Maintainability:** Change database without touching business logic
3. **Flexibility:** Swap implementations easily
4. **Independence:** Domain logic is technology-agnostic

### Example: Device Repository

**1. Define port (interface) in domain:**
```python
# src/domain/ports/device_repository.py
from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.device import Device

class DeviceRepository(ABC):
    """Port for device persistence"""

    @abstractmethod
    def find_by_id(self, device_id: str) -> Optional[Device]:
        """Find device by ID"""
        pass

    @abstractmethod
    def save(self, device: Device) -> None:
        """Save device"""
        pass

    @abstractmethod
    def list_all(self) -> List[Device]:
        """List all devices"""
        pass

    @abstractmethod
    def delete(self, device_id: str) -> None:
        """Delete device"""
        pass
```

**2. Implement adapter in infrastructure:**
```python
# src/infrastructure/repositories/device_repository_impl.py
import boto3
from typing import List, Optional
from ...domain.ports.device_repository import DeviceRepository
from ...domain.entities.device import Device
from ...shared.config.environment import get_env

class DeviceRepositoryImpl(DeviceRepository):
    """DynamoDB implementation of DeviceRepository"""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(get_env('DEVICES_TABLE'))

    def find_by_id(self, device_id: str) -> Optional[Device]:
        response = self.table.get_item(Key={'device_id': device_id})
        item = response.get('Item')
        return Device.from_dict(item) if item else None

    def save(self, device: Device) -> None:
        self.table.put_item(Item=device.to_dict())

    def list_all(self) -> List[Device]:
        response = self.table.scan()
        return [Device.from_dict(item) for item in response.get('Items', [])]

    def delete(self, device_id: str) -> None:
        self.table.delete_item(Key={'device_id': device_id})
```

**3. Use in Lambda handler (dependency injection):**
```python
# src/functions/device/get_device.py
from ...domain.services.device_service import DeviceService
from ...infrastructure.repositories.device_repository_impl import DeviceRepositoryImpl
from ...shared.utils.response import success_response, error_response
from ...shared.middleware.logger import logger

def lambda_handler(event, context):
    """Get device by ID"""
    try:
        device_id = event['pathParameters']['deviceId']
        logger.info(f"Getting device {device_id}")

        # Dependency injection
        device_repo = DeviceRepositoryImpl()
        device_service = DeviceService(device_repo)

        # Execute business logic
        device = device_service.get_device(device_id)

        if not device:
            return error_response(
                'DEVICE_NOT_FOUND',
                f'Device {device_id} not found',
                status_code=404
            )

        return success_response(device.to_dict())

    except Exception as e:
        logger.error(f"Error getting device: {str(e)}", exc_info=True)
        return error_response(
            'INTERNAL_ERROR',
            'Failed to retrieve device',
            status_code=500
        )
```

---

## Development Workflow

### 1. Local Development Setup

```bash
cd backend

# Install Node.js dependencies (Serverless CLI)
npm install

# Create Python virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# venv\Scripts\activate   # Windows

# Install Python dependencies
pip install -r requirements.txt

# Start local API
npm run dev  # Runs serverless-offline on port 3000
```

### 2. Test Local API

```bash
# List devices
curl http://localhost:3000/devices | jq

# Get specific device
curl http://localhost:3000/devices/device-001 | jq

# List alerts
curl http://localhost:3000/alerts | jq
```

### 3. Code Quality Checks

```bash
# Format code
black src/

# Lint code
flake8 src/

# Type check
mypy src/

# Run tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html
```

### 4. Environment Variables

**Local development** (auto-configured in `serverless.yml`):
```yaml
provider:
  environment:
    ENVIRONMENT: dev
    AWS_REGION: us-east-1
    DEVICES_TABLE: iot-devices-dev
    ALERTS_TABLE: iot-alerts-dev
    # ... more tables
```

**Access in code:**
```python
from ...shared.config.environment import get_env

devices_table = get_env('DEVICES_TABLE')
```

---

## Common Tasks

### Task 1: Add a New Lambda Function

**Scenario:** Add an endpoint to get device statistics

**1. Create domain service (if needed):**
```python
# src/domain/services/device_statistics_service.py
from typing import Dict, List
from ..entities.device import Device
from ..ports.device_repository import DeviceRepository

class DeviceStatisticsService:
    """Service for device statistics"""

    def __init__(self, device_repo: DeviceRepository):
        self.device_repo = device_repo

    def get_statistics(self) -> Dict:
        """Calculate device statistics"""
        devices = self.device_repo.list_all()

        stats = {
            'total': len(devices),
            'online': 0,
            'offline': 0,
            'warning': 0,
            'error': 0,
            'by_type': {}
        }

        for device in devices:
            # Count by status
            stats[device.status] = stats.get(device.status, 0) + 1

            # Count by type
            if device.type not in stats['by_type']:
                stats['by_type'][device.type] = 0
            stats['by_type'][device.type] += 1

        return stats
```

**2. Create Lambda handler:**
```python
# src/functions/device/get_statistics.py
from ...domain.services.device_statistics_service import DeviceStatisticsService
from ...infrastructure.repositories.device_repository_impl import DeviceRepositoryImpl
from ...shared.utils.response import success_response, error_response
from ...shared.middleware.logger import logger

def lambda_handler(event, context):
    """
    Get device statistics

    Returns:
        200: Statistics object
        500: Internal error
    """
    try:
        logger.info("Calculating device statistics")

        # Dependency injection
        device_repo = DeviceRepositoryImpl()
        service = DeviceStatisticsService(device_repo)

        # Execute business logic
        statistics = service.get_statistics()

        logger.info(f"Statistics: {statistics}")
        return success_response(statistics)

    except Exception as e:
        logger.error(f"Error calculating statistics: {str(e)}", exc_info=True)
        return error_response(
            'STATISTICS_ERROR',
            'Failed to calculate device statistics',
            status_code=500
        )
```

**3. Add to `serverless.yml`:**
```yaml
functions:
  getDeviceStatistics:
    handler: src/functions/device/get_statistics.lambda_handler
    description: Get device statistics
    memorySize: 512
    timeout: 30
    events:
      - http:
          path: devices/statistics
          method: get
          cors: true
    environment:
      DEVICES_TABLE: ${self:custom.tables.devices}
```

**4. Test locally:**
```bash
# Restart serverless-offline
npm run dev

# Test endpoint
curl http://localhost:3000/devices/statistics | jq
```

### Task 2: Add DynamoDB Integration

**Scenario:** Replace mock repository with real DynamoDB

**1. Ensure table exists in `serverless.yml`:**
```yaml
resources:
  Resources:
    DevicesTable:
      Type: AWS::DynamoDB::Table
      Properties:
        TableName: ${self:custom.tables.devices}
        BillingMode: PAY_PER_REQUEST
        AttributeDefinitions:
          - AttributeName: device_id
            AttributeType: S
          - AttributeName: organization_id
            AttributeType: S
        KeySchema:
          - AttributeName: device_id
            KeyType: HASH
        GlobalSecondaryIndexes:
          - IndexName: OrganizationIndex
            KeySchema:
              - AttributeName: organization_id
                KeyType: HASH
            Projection:
              ProjectionType: ALL
```

**2. Update entity with serialization:**
```python
# src/domain/entities/device.py
from dataclasses import dataclass, asdict
from typing import Dict, Optional
from datetime import datetime

@dataclass
class Device:
    device_id: str
    name: str
    type: str
    status: str
    organization_id: str
    created_at: str
    updated_at: str
    metadata: Optional[Dict] = None

    def to_dict(self) -> Dict:
        """Convert to DynamoDB item"""
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict) -> 'Device':
        """Create from DynamoDB item"""
        return cls(
            device_id=data['device_id'],
            name=data['name'],
            type=data['type'],
            status=data['status'],
            organization_id=data['organization_id'],
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            metadata=data.get('metadata')
        )
```

**3. Implement repository:**
```python
# src/infrastructure/repositories/device_repository_impl.py
import boto3
from boto3.dynamodb.conditions import Key
from typing import List, Optional
from ...domain.ports.device_repository import DeviceRepository
from ...domain.entities.device import Device
from ...shared.config.environment import get_env
from ...shared.middleware.logger import logger

class DeviceRepositoryImpl(DeviceRepository):
    """DynamoDB implementation of DeviceRepository"""

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table_name = get_env('DEVICES_TABLE')
        self.table = self.dynamodb.Table(self.table_name)

    def find_by_id(self, device_id: str) -> Optional[Device]:
        """Find device by ID"""
        try:
            response = self.table.get_item(Key={'device_id': device_id})
            item = response.get('Item')
            return Device.from_dict(item) if item else None
        except Exception as e:
            logger.error(f"Error finding device {device_id}: {str(e)}")
            raise

    def save(self, device: Device) -> None:
        """Save device"""
        try:
            self.table.put_item(Item=device.to_dict())
            logger.info(f"Saved device {device.device_id}")
        except Exception as e:
            logger.error(f"Error saving device {device.device_id}: {str(e)}")
            raise

    def list_by_organization(self, organization_id: str) -> List[Device]:
        """List devices by organization"""
        try:
            response = self.table.query(
                IndexName='OrganizationIndex',
                KeyConditionExpression=Key('organization_id').eq(organization_id)
            )
            return [Device.from_dict(item) for item in response.get('Items', [])]
        except Exception as e:
            logger.error(f"Error listing devices for org {organization_id}: {str(e)}")
            raise

    def delete(self, device_id: str) -> None:
        """Delete device"""
        try:
            self.table.delete_item(Key={'device_id': device_id})
            logger.info(f"Deleted device {device_id}")
        except Exception as e:
            logger.error(f"Error deleting device {device_id}: {str(e)}")
            raise
```

**4. Ensure Lambda has IAM permissions:**
```yaml
# serverless.yml
provider:
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:Query
            - dynamodb:Scan
            - dynamodb:GetItem
            - dynamodb:PutItem
            - dynamodb:UpdateItem
            - dynamodb:DeleteItem
          Resource:
            - !GetAtt DevicesTable.Arn
            - !Sub '${DevicesTable.Arn}/index/*'
```

### Task 3: Add Stream Processing

**Scenario:** Process IoT device data from Kinesis stream

**1. Create stream processor:**
```python
# src/functions/stream_processing/kinesis_consumer.py
import json
import base64
from typing import Dict, List
from ...domain.services.sensor_data_service import SensorDataService
from ...infrastructure.repositories.sensor_data_repository_impl import SensorDataRepositoryImpl
from ...shared.middleware.logger import logger

def lambda_handler(event, context):
    """
    Process sensor data from Kinesis stream

    Event structure:
    {
        "Records": [
            {
                "kinesis": {
                    "data": "base64-encoded-json",
                    "partitionKey": "device-id"
                }
            }
        ]
    }
    """
    try:
        # Initialize dependencies
        sensor_repo = SensorDataRepositoryImpl()
        sensor_service = SensorDataService(sensor_repo)

        # Process records
        processed = 0
        failed = 0

        for record in event['Records']:
            try:
                # Decode data
                payload = json.loads(base64.b64decode(record['kinesis']['data']))
                device_id = record['kinesis']['partitionKey']

                logger.info(f"Processing data for device {device_id}")

                # Validate and process
                sensor_service.process_sensor_reading(device_id, payload)
                processed += 1

            except Exception as e:
                logger.error(f"Error processing record: {str(e)}", exc_info=True)
                failed += 1

        logger.info(f"Processed {processed} records, {failed} failed")

        return {
            'statusCode': 200,
            'body': {
                'processed': processed,
                'failed': failed
            }
        }

    except Exception as e:
        logger.error(f"Stream processing error: {str(e)}", exc_info=True)
        raise
```

**2. Add to `serverless.yml`:**
```yaml
functions:
  kinesisConsumer:
    handler: src/functions/stream_processing/kinesis_consumer.lambda_handler
    description: Process sensor data from Kinesis
    memorySize: 1024
    timeout: 300
    reservedConcurrency: 10  # Limit concurrent executions
    events:
      - stream:
          type: kinesis
          arn: !GetAtt SensorDataStream.Arn
          batchSize: 100
          startingPosition: LATEST
          maximumRetryAttempts: 3
```

---

## Code Conventions

### Python Style

**Follow PEP 8 and type hints:**
```python
# ✅ Good
from typing import List, Optional, Dict
from dataclasses import dataclass

@dataclass
class Device:
    device_id: str
    name: str
    status: str

def get_device(device_id: str) -> Optional[Device]:
    """Get device by ID"""
    # Implementation
    pass

def list_devices(organization_id: str, limit: int = 100) -> List[Device]:
    """List devices for organization"""
    # Implementation
    pass

# ❌ Bad
def get_device(device_id):  # No type hints
    pass

def list_devices(organization_id, limit=100):  # No type hints
    pass
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | snake_case | `device_service.py` |
| Classes | PascalCase | `DeviceService`, `DeviceRepository` |
| Functions/Methods | snake_case | `get_device()`, `list_all()` |
| Variables | snake_case | `device_id`, `sensor_data` |
| Constants | UPPER_SNAKE_CASE | `MAX_RETRIES`, `DEFAULT_TIMEOUT` |
| Private methods | _snake_case | `_validate_data()` |

### Docstrings

**Use Google-style docstrings:**
```python
def get_device(device_id: str, include_history: bool = False) -> Optional[Device]:
    """
    Get device by ID.

    Args:
        device_id: Unique device identifier
        include_history: Include sensor data history

    Returns:
        Device object if found, None otherwise

    Raises:
        ValueError: If device_id is invalid
        RepositoryError: If database operation fails
    """
    pass
```

### Error Handling

**Use custom exceptions:**
```python
# src/shared/exceptions/custom_exceptions.py
class DomainException(Exception):
    """Base domain exception"""
    pass

class DeviceNotFoundException(DomainException):
    """Device not found"""
    pass

class InvalidDeviceDataException(DomainException):
    """Invalid device data"""
    pass

# Usage
from ...shared.exceptions.custom_exceptions import DeviceNotFoundException

def get_device(device_id: str) -> Device:
    device = self.device_repo.find_by_id(device_id)
    if not device:
        raise DeviceNotFoundException(f"Device {device_id} not found")
    return device
```

---

## Lambda Function Patterns

### Standard Lambda Handler Structure

```python
from ...shared.utils.response import success_response, error_response
from ...shared.middleware.logger import logger
from ...shared.exceptions.custom_exceptions import DomainException

def lambda_handler(event, context):
    """
    Lambda handler description.

    Event structure:
    {
        "pathParameters": {"id": "..."},
        "queryStringParameters": {"filter": "..."},
        "body": "{...}"
    }

    Returns:
        200: Success response
        400: Bad request
        404: Not found
        500: Internal error
    """
    try:
        # 1. Extract input
        path_params = event.get('pathParameters', {})
        query_params = event.get('queryStringParameters', {})

        # 2. Validate input (if needed)
        # validate_input(...)

        # 3. Initialize dependencies
        repo = RepositoryImpl()
        service = DomainService(repo)

        # 4. Execute business logic
        result = service.do_something(path_params, query_params)

        # 5. Return success
        return success_response(result)

    except DomainException as e:
        # Known domain errors
        logger.warning(f"Domain error: {str(e)}")
        return error_response('DOMAIN_ERROR', str(e), status_code=400)

    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return error_response(
            'INTERNAL_ERROR',
            'An unexpected error occurred',
            status_code=500
        )
```

### Response Helpers

**`src/shared/utils/response.py`:**
```python
import json
from typing import Any, Dict, Optional

def success_response(
    data: Any,
    status_code: int = 200,
    headers: Optional[Dict] = None
) -> Dict:
    """Create success response"""
    default_headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Credentials': True
    }

    if headers:
        default_headers.update(headers)

    return {
        'statusCode': status_code,
        'headers': default_headers,
        'body': json.dumps({
            'success': True,
            'data': data
        })
    }

def error_response(
    error_code: str,
    message: str,
    status_code: int = 400,
    details: Optional[Dict] = None
) -> Dict:
    """Create error response"""
    body = {
        'success': False,
        'error': {
            'code': error_code,
            'message': message
        }
    }

    if details:
        body['error']['details'] = details

    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True
        },
        'body': json.dumps(body)
    }
```

### Logging

**`src/shared/middleware/logger.py`:**
```python
import logging
import json
from typing import Any

# Configure logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_event(event: dict) -> None:
    """Log Lambda event (redact sensitive data)"""
    sanitized = {k: v for k, v in event.items() if k != 'headers'}
    logger.info(f"Event: {json.dumps(sanitized)}")

# Usage in Lambda
from ...shared.middleware.logger import logger

logger.info(f"Processing device {device_id}")
logger.warning(f"Device {device_id} not found")
logger.error(f"Error processing device: {str(e)}", exc_info=True)
```

---

## AWS Service Integration

### DynamoDB Best Practices

**1. Use batch operations:**
```python
def batch_save_devices(devices: List[Device]) -> None:
    """Save multiple devices in batches"""
    with self.table.batch_writer() as batch:
        for device in devices:
            batch.put_item(Item=device.to_dict())
```

**2. Use query instead of scan:**
```python
# ✅ Good - Query with partition key
response = self.table.query(
    KeyConditionExpression=Key('organization_id').eq(org_id)
)

# ❌ Bad - Scan entire table
response = self.table.scan(
    FilterExpression=Attr('organization_id').eq(org_id)
)
```

**3. Handle pagination:**
```python
def list_all_devices(self, organization_id: str) -> List[Device]:
    """List all devices with pagination"""
    devices = []
    last_evaluated_key = None

    while True:
        params = {
            'IndexName': 'OrganizationIndex',
            'KeyConditionExpression': Key('organization_id').eq(organization_id)
        }

        if last_evaluated_key:
            params['ExclusiveStartKey'] = last_evaluated_key

        response = self.table.query(**params)
        devices.extend([Device.from_dict(item) for item in response['Items']])

        last_evaluated_key = response.get('LastEvaluatedKey')
        if not last_evaluated_key:
            break

    return devices
```

### Timestream (Time-Series Data)

```python
# src/infrastructure/repositories/sensor_data_repository_impl.py
import boto3
from datetime import datetime
from typing import List, Dict

class SensorDataRepositoryImpl:
    """Timestream implementation for sensor data"""

    def __init__(self):
        self.client = boto3.client('timestream-write')
        self.query_client = boto3.client('timestream-query')
        self.database = get_env('TIMESTREAM_DATABASE')
        self.table = get_env('TIMESTREAM_TABLE')

    def write_sensor_reading(self, device_id: str, readings: Dict) -> None:
        """Write sensor data to Timestream"""
        current_time = str(int(datetime.now().timestamp() * 1000))

        records = []
        for metric_name, value in readings.items():
            records.append({
                'Dimensions': [
                    {'Name': 'device_id', 'Value': device_id}
                ],
                'MeasureName': metric_name,
                'MeasureValue': str(value),
                'MeasureValueType': 'DOUBLE',
                'Time': current_time,
                'TimeUnit': 'MILLISECONDS'
            })

        self.client.write_records(
            DatabaseName=self.database,
            TableName=self.table,
            Records=records
        )

    def query_sensor_history(
        self,
        device_id: str,
        start_time: str,
        end_time: str
    ) -> List[Dict]:
        """Query sensor history"""
        query = f"""
            SELECT *
            FROM "{self.database}"."{self.table}"
            WHERE device_id = '{device_id}'
            AND time BETWEEN from_iso8601_timestamp('{start_time}')
                        AND from_iso8601_timestamp('{end_time}')
            ORDER BY time DESC
        """

        response = self.query_client.query(QueryString=query)
        return self._parse_query_result(response)

    def _parse_query_result(self, response: Dict) -> List[Dict]:
        """Parse Timestream query result"""
        # Implementation to parse rows
        pass
```

### SQS (Message Queues)

```python
# src/infrastructure/messaging/sqs_client.py
import boto3
import json
from typing import Dict

class SQSClient:
    """SQS message queue client"""

    def __init__(self, queue_url: str):
        self.client = boto3.client('sqs')
        self.queue_url = queue_url

    def send_message(self, message: Dict) -> None:
        """Send message to queue"""
        self.client.send_message(
            QueueUrl=self.queue_url,
            MessageBody=json.dumps(message)
        )

    def send_batch(self, messages: List[Dict]) -> None:
        """Send multiple messages"""
        entries = [
            {
                'Id': str(i),
                'MessageBody': json.dumps(msg)
            }
            for i, msg in enumerate(messages)
        ]

        self.client.send_message_batch(
            QueueUrl=self.queue_url,
            Entries=entries
        )
```

---

## Error Handling

### Exception Hierarchy

```python
# src/shared/exceptions/custom_exceptions.py

class DomainException(Exception):
    """Base exception for domain errors"""
    pass

class ValidationException(DomainException):
    """Invalid input data"""
    pass

class NotFoundException(DomainException):
    """Resource not found"""
    pass

class DeviceNotFoundException(NotFoundException):
    """Device not found"""
    pass

class AlertNotFoundException(NotFoundException):
    """Alert not found"""
    pass

class RepositoryException(Exception):
    """Database operation failed"""
    pass
```

### Error Handling Pattern

```python
from ...shared.exceptions.custom_exceptions import (
    ValidationException,
    DeviceNotFoundException,
    RepositoryException
)

def lambda_handler(event, context):
    try:
        # Business logic
        pass

    except ValidationException as e:
        return error_response('VALIDATION_ERROR', str(e), status_code=400)

    except DeviceNotFoundException as e:
        return error_response('DEVICE_NOT_FOUND', str(e), status_code=404)

    except RepositoryException as e:
        logger.error(f"Repository error: {str(e)}", exc_info=True)
        return error_response('DATABASE_ERROR', 'Database operation failed', status_code=500)

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return error_response('INTERNAL_ERROR', 'An unexpected error occurred', status_code=500)
```

---

## Testing

### Unit Tests (Domain Logic)

```python
# tests/unit/domain/test_device_service.py
import pytest
from unittest.mock import Mock, MagicMock
from src.domain.services.device_service import DeviceService
from src.domain.entities.device import Device
from src.shared.exceptions.custom_exceptions import DeviceNotFoundException

@pytest.fixture
def mock_device_repo():
    """Mock device repository"""
    return Mock()

@pytest.fixture
def device_service(mock_device_repo):
    """Device service with mocked repository"""
    return DeviceService(mock_device_repo)

def test_get_device_success(device_service, mock_device_repo):
    """Test getting device successfully"""
    # Arrange
    expected_device = Device(
        device_id='123',
        name='Test Device',
        type='sensor',
        status='online',
        organization_id='org-1',
        created_at='2025-01-01T00:00:00Z',
        updated_at='2025-01-01T00:00:00Z'
    )
    mock_device_repo.find_by_id.return_value = expected_device

    # Act
    device = device_service.get_device('123')

    # Assert
    assert device == expected_device
    mock_device_repo.find_by_id.assert_called_once_with('123')

def test_get_device_not_found(device_service, mock_device_repo):
    """Test getting non-existent device"""
    # Arrange
    mock_device_repo.find_by_id.return_value = None

    # Act & Assert
    with pytest.raises(DeviceNotFoundException):
        device_service.get_device('nonexistent')
```

### Integration Tests (With AWS Mocks)

```python
# tests/integration/repositories/test_device_repository.py
import pytest
import boto3
from moto import mock_dynamodb
from src.infrastructure.repositories.device_repository_impl import DeviceRepositoryImpl
from src.domain.entities.device import Device

@pytest.fixture
def dynamodb_table():
    """Create mock DynamoDB table"""
    with mock_dynamodb():
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
        table = dynamodb.create_table(
            TableName='test-devices',
            KeySchema=[
                {'AttributeName': 'device_id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'device_id', 'AttributeType': 'S'}
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        yield table

def test_save_and_find_device(dynamodb_table, monkeypatch):
    """Test saving and retrieving device"""
    # Arrange
    monkeypatch.setenv('DEVICES_TABLE', 'test-devices')
    repo = DeviceRepositoryImpl()

    device = Device(
        device_id='123',
        name='Test Device',
        type='sensor',
        status='online',
        organization_id='org-1',
        created_at='2025-01-01T00:00:00Z',
        updated_at='2025-01-01T00:00:00Z'
    )

    # Act
    repo.save(device)
    found_device = repo.find_by_id('123')

    # Assert
    assert found_device is not None
    assert found_device.device_id == '123'
    assert found_device.name == 'Test Device'
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/unit/domain/test_device_service.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run with verbose output
pytest -v

# Run only unit tests
pytest tests/unit/

# Run only integration tests
pytest tests/integration/
```

---

## Deployment

### Deploy to AWS

```bash
# Deploy to dev environment
npm run deploy:dev

# Deploy to production
npm run deploy:prod

# Deploy single function (faster)
serverless deploy function -f getDevice --stage prod

# Remove infrastructure
npm run remove:prod
```

### Deployment Checklist

**Before deploying:**
- [ ] Run tests: `pytest`
- [ ] Check type hints: `mypy src/`
- [ ] Format code: `black src/`
- [ ] Lint code: `flake8 src/`
- [ ] Review `serverless.yml` changes
- [ ] Update environment variables if needed
- [ ] Test locally with `npm run dev`

**After deploying:**
- [ ] Check CloudWatch logs for errors
- [ ] Test API endpoints
- [ ] Monitor X-Ray for performance issues
- [ ] Verify DynamoDB tables created
- [ ] Check IAM permissions

---

## Performance & Optimization

### Lambda Performance Tips

**1. Minimize cold starts:**
```python
# Initialize clients outside handler
import boto3

# ✅ Good - Reused across invocations
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('devices')

def lambda_handler(event, context):
    # Use initialized clients
    pass

# ❌ Bad - Recreated every time
def lambda_handler(event, context):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('devices')
```

**2. Use connection pooling:**
```python
import os

# Set connection pool size
os.environ['BOTO_MAX_POOL_CONNECTIONS'] = '50'
```

**3. Optimize memory/timeout:**
```yaml
# serverless.yml
functions:
  heavyProcessor:
    memorySize: 1024  # More memory = faster CPU
    timeout: 60       # Adjust based on needs
```

**4. Use Lambda Layers for dependencies:**
```yaml
# serverless.yml
layers:
  pythonLibs:
    path: layers/python-libs
    compatibleRuntimes:
      - python3.11

functions:
  myFunction:
    layers:
      - !Ref PythonLibsLambdaLayer
```

---

## Troubleshooting

### Common Issues

**1. Import errors**
```
Problem: ModuleNotFoundError: No module named 'src'
Solution: Ensure PYTHONPATH is set correctly or use relative imports
```

**2. DynamoDB permission errors**
```
Problem: AccessDeniedException when accessing DynamoDB
Solution: Check IAM permissions in serverless.yml
```

**3. Lambda timeout**
```
Problem: Lambda times out after 30 seconds
Solution: Increase timeout in serverless.yml or optimize code
```

**4. Environment variable not found**
```
Problem: KeyError when accessing environment variable
Solution: Add to serverless.yml under provider.environment or function.environment
```

### Debug Locally

**Enable debug logging:**
```python
import logging

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
```

**Test Lambda handler directly:**
```python
# test_local.py
from src.functions.device.get_device import lambda_handler

event = {
    'pathParameters': {'deviceId': '123'},
    'queryStringParameters': None
}

result = lambda_handler(event, None)
print(result)
```

**Use serverless-offline logs:**
```bash
# Start with verbose logging
npm run dev -- --verbose
```

---

**Last Updated:** 2025-11-15
**Maintainer:** AI Assistant (Claude)

**See also:**
- Main CLAUDE.md in root directory
- frontend/CLAUDE.md for frontend development
- docs/02-ARCHITECTURE-DESIGN.md for architecture details
- docs/05-BACKEND-SERVICES-DESIGN.md for API specifications

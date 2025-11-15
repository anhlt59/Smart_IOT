# Backend Services Design - IoT Monitoring Application

## 1. Overview

The backend is built using a **serverless architecture** on AWS, implemented with the **Serverless Framework** and **Python 3.11**. The design follows **Hexagonal Architecture** principles to ensure modularity, testability, and maintainability.

### 1.1 Technology Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Programming language | 3.11+ |
| **Serverless Framework** | Infrastructure as Code | 3.x+ |
| **AWS Lambda** | Serverless compute | - |
| **boto3** | AWS SDK for Python | Latest |
| **Pydantic** | Data validation | 2.x+ |
| **pytest** | Testing framework | Latest |
| **mypy** | Static type checking | Latest |

### 1.2 Design Principles

1. **Single Responsibility**: Each Lambda function has one clear purpose
2. **Domain-Driven Design**: Core business logic separated from infrastructure
3. **Dependency Inversion**: Depend on abstractions, not concretions
4. **Fail Fast**: Validate inputs early
5. **Idempotency**: Operations are safe to retry
6. **Observability**: Comprehensive logging and tracing

## 2. Lambda Functions Architecture

### 2.1 Function Categories

```
Lambda Functions (50+ functions)
├── API Functions (REST)          # HTTP API endpoints
├── Stream Processing Functions   # Event-driven data processing
├── WebSocket Functions          # Real-time communication
├── Scheduled Functions          # Cron jobs
└── Event-Driven Functions       # S3, IoT, EventBridge triggers
```

## 3. API Functions (REST API)

### 3.1 Device Management API

#### 3.1.1 Register Device

**Function:** `register_device`

**Trigger:** API Gateway POST `/devices`

**Purpose:** Register a new IoT device in the system

**Input:**
```json
{
  "deviceType": "temperature-sensor-v2",
  "name": "Office-Temp-Sensor-1",
  "location": {
    "lat": 37.7749,
    "lon": -122.4194,
    "address": "Office 301, Building A"
  },
  "connectivity": {
    "type": "cellular",
    "simId": "sim-123456"
  },
  "metadata": {
    "manufacturer": "SensorCorp",
    "model": "TSv2-001",
    "serialNumber": "SN123456789"
  },
  "tags": ["office", "building-a"]
}
```

**Processing Steps:**
1. Validate request payload (Pydantic schema)
2. Check user permissions (organization access)
3. Generate unique deviceId
4. Create device entity (domain layer)
5. Save to DynamoDB via repository
6. Create IoT Thing in AWS IoT Core
7. Generate device certificates
8. Return device details + provisioning credentials

**Output:**
```json
{
  "deviceId": "dev-abc123",
  "name": "Office-Temp-Sensor-1",
  "status": "registered",
  "provisioningCredentials": {
    "certificateArn": "arn:aws:iot:...",
    "certificatePem": "-----BEGIN CERTIFICATE-----...",
    "privateKey": "-----BEGIN RSA PRIVATE KEY-----...",
    "endpoint": "a1b2c3d4e5.iot.us-east-1.amazonaws.com"
  },
  "createdAt": "2025-11-15T10:00:00Z"
}
```

**Error Handling:**
- 400: Invalid input
- 403: Unauthorized (wrong organization)
- 409: Device already exists
- 500: Internal server error

**Hexagonal Layer Mapping:**
```python
# Adapter (API Handler)
def lambda_handler(event, context):
    # Parse HTTP request
    # Call domain service
    # Format HTTP response

# Domain Service
class DeviceService:
    def register_device(self, device_data: DeviceCreateDTO) -> Device:
        # Business logic

# Repository (Infrastructure)
class DynamoDBDeviceRepository:
    def save(self, device: Device) -> Device:
        # DynamoDB operations
```

---

#### 3.1.2 Get Device

**Function:** `get_device`

**Trigger:** API Gateway GET `/devices/{deviceId}`

**Purpose:** Retrieve device details

**Processing Steps:**
1. Extract deviceId from path parameters
2. Validate user access to device
3. Fetch from DynamoDB
4. Fetch latest sensor data from Timestream (last reading)
5. Enrich with real-time status (from IoT Core shadow)
6. Return aggregated device info

**Output:**
```json
{
  "deviceId": "dev-abc123",
  "name": "Office-Temp-Sensor-1",
  "type": "temperature-sensor-v2",
  "status": "online",
  "location": {...},
  "lastSeen": "2025-11-15T10:05:00Z",
  "lastReading": {
    "temperature": 23.5,
    "humidity": 45,
    "co2": 450,
    "timestamp": "2025-11-15T10:05:00Z"
  },
  "firmwareVersion": "v2.1.0",
  "connectivity": {
    "type": "cellular",
    "signalStrength": -45,
    "ipAddress": "10.0.1.25"
  },
  "health": {
    "uptime": 99.8,
    "dataQuality": 98.5
  }
}
```

---

#### 3.1.3 List Devices

**Function:** `list_devices`

**Trigger:** API Gateway GET `/devices`

**Query Parameters:**
- `organizationId` (required)
- `status` (online|offline|maintenance)
- `deviceType`
- `location`
- `tags`
- `page` (default: 1)
- `pageSize` (default: 25)
- `sortBy` (name|lastSeen|status)
- `sortOrder` (asc|desc)

**Processing Steps:**
1. Validate user access to organization
2. Build DynamoDB query with filters
3. Apply pagination
4. Fetch devices from DynamoDB
5. Optionally enrich with latest readings
6. Return paginated response

**Output:**
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "pageSize": 25,
    "totalItems": 150,
    "totalPages": 6,
    "hasNext": true,
    "hasPrevious": false
  },
  "filters": {
    "status": "online",
    "deviceType": "temperature-sensor-v2"
  }
}
```

---

#### 3.1.4 Update Device

**Function:** `update_device`

**Trigger:** API Gateway PUT `/devices/{deviceId}`

**Purpose:** Update device metadata

**Allowed Updates:**
- name
- location
- tags
- metadata
- status (manual override)

**Processing Steps:**
1. Validate user permissions (admin or device owner)
2. Fetch existing device
3. Validate changes
4. Update device entity
5. Save to DynamoDB
6. Log change history
7. Return updated device

---

#### 3.1.5 Delete Device

**Function:** `delete_device`

**Trigger:** API Gateway DELETE `/devices/{deviceId}`

**Processing Steps:**
1. Validate admin permissions
2. Check for active alerts
3. Soft delete (set status to 'deleted')
4. Deactivate IoT Thing
5. Archive historical data (mark for deletion)
6. Return success

---

#### 3.1.6 Get Device History

**Function:** `get_device_history`

**Trigger:** API Gateway GET `/devices/{deviceId}/history`

**Query Parameters:**
- `startDate` (ISO 8601)
- `endDate` (ISO 8601)
- `metrics` (temperature,humidity,co2)
- `aggregation` (raw|1m|5m|15m|1h|1d)

**Processing Steps:**
1. Validate time range (max 90 days for raw data)
2. Build Timestream query
3. Execute query with aggregation
4. Format results for charting
5. Return time-series data

**Output:**
```json
{
  "deviceId": "dev-abc123",
  "timeRange": {
    "start": "2025-11-14T10:00:00Z",
    "end": "2025-11-15T10:00:00Z"
  },
  "metrics": ["temperature", "humidity"],
  "aggregation": "15m",
  "data": [
    {
      "timestamp": "2025-11-14T10:00:00Z",
      "temperature": 23.5,
      "humidity": 45
    },
    {
      "timestamp": "2025-11-14T10:15:00Z",
      "temperature": 23.8,
      "humidity": 44
    }
  ]
}
```

---

### 3.2 Alert Management API

#### 3.2.1 List Alerts

**Function:** `list_alerts`

**Trigger:** API Gateway GET `/alerts`

**Query Parameters:**
- `status` (triggered|acknowledged|resolved)
- `severity` (info|warning|critical)
- `deviceId`
- `startDate`, `endDate`
- `page`, `pageSize`

**Processing Steps:**
1. Validate user access
2. Build DynamoDB query with GSI (status-severity-index)
3. Apply filters
4. Fetch alerts with pagination
5. Enrich with device details
6. Return results

---

#### 3.2.2 Get Alert

**Function:** `get_alert`

**Trigger:** API Gateway GET `/alerts/{alertId}`

**Purpose:** Get detailed alert information

**Output:**
```json
{
  "alertId": "alert-123",
  "ruleId": "rule-temp-high",
  "ruleName": "High Temperature Alert",
  "deviceId": "dev-abc123",
  "deviceName": "Office-Temp-Sensor-1",
  "severity": "warning",
  "status": "acknowledged",
  "condition": "temperature > 40",
  "actualValue": 42.5,
  "threshold": 40,
  "triggeredAt": "2025-11-15T10:00:00Z",
  "acknowledgedAt": "2025-11-15T10:05:00Z",
  "acknowledgedBy": {
    "userId": "user-456",
    "name": "John Doe"
  },
  "notificationsSent": ["email", "push"],
  "comments": [
    {
      "userId": "user-456",
      "comment": "Checking HVAC system",
      "timestamp": "2025-11-15T10:06:00Z"
    }
  ],
  "relatedAlerts": [
    {
      "alertId": "alert-124",
      "deviceName": "Office-Temp-Sensor-2",
      "triggeredAt": "2025-11-15T10:02:00Z"
    }
  ]
}
```

---

#### 3.2.3 Acknowledge Alert

**Function:** `acknowledge_alert`

**Trigger:** API Gateway POST `/alerts/{alertId}/acknowledge`

**Input:**
```json
{
  "comment": "Investigating the issue"
}
```

**Processing Steps:**
1. Validate user permissions
2. Fetch alert
3. Check if already acknowledged
4. Update alert status
5. Log acknowledgment
6. Optionally notify stakeholders
7. Return updated alert

---

#### 3.2.4 Resolve Alert

**Function:** `resolve_alert`

**Trigger:** API Gateway POST `/alerts/{alertId}/resolve`

**Input:**
```json
{
  "resolution": "HVAC system adjusted",
  "preventionNotes": "Schedule regular HVAC maintenance"
}
```

**Processing Steps:**
1. Validate user permissions
2. Fetch alert
3. Check if can be resolved (must be acknowledged first)
4. Update status to 'resolved'
5. Log resolution
6. Return updated alert

---

#### 3.2.5 Create Alert Rule

**Function:** `create_alert_rule`

**Trigger:** API Gateway POST `/alert-rules`

**Input:**
```json
{
  "name": "High Temperature Alert",
  "description": "Alert when temperature exceeds 40°C",
  "deviceType": "temperature-sensor-v2",
  "deviceIds": [],  // empty = apply to all devices of this type
  "condition": {
    "metric": "temperature",
    "operator": ">",
    "threshold": 40,
    "duration": 300  // seconds, sustained condition
  },
  "severity": "warning",
  "actions": {
    "notifications": ["email", "push"],
    "webhooks": []
  },
  "cooldownPeriod": 900,  // 15 minutes
  "schedule": {
    "type": "always"  // or "business-hours" or "custom"
  }
}
```

**Processing Steps:**
1. Validate user permissions (admin or org admin)
2. Validate rule configuration
3. Create AlertRule entity
4. Save to DynamoDB
5. Return created rule

---

#### 3.2.6 Update Alert Rule

**Function:** `update_alert_rule`

**Trigger:** API Gateway PUT `/alert-rules/{ruleId}`

**Purpose:** Modify existing alert rule

---

#### 3.2.7 Delete Alert Rule

**Function:** `delete_alert_rule`

**Trigger:** API Gateway DELETE `/alert-rules/{ruleId}`

**Purpose:** Delete alert rule (soft delete)

---

#### 3.2.8 List Alert Rules

**Function:** `list_alert_rules`

**Trigger:** API Gateway GET `/alert-rules`

**Purpose:** Get all alert rules for organization

---

### 3.3 User Management API

#### 3.3.1 Get User Profile

**Function:** `get_profile`

**Trigger:** API Gateway GET `/users/me`

**Purpose:** Get current user's profile

**Output:**
```json
{
  "userId": "user-456",
  "email": "john.doe@example.com",
  "name": "John Doe",
  "organizationId": "org-789",
  "role": "operator",
  "preferences": {
    "notifications": {
      "email": true,
      "push": true,
      "sms": false
    },
    "quietHours": {
      "enabled": true,
      "start": "22:00",
      "end": "08:00",
      "timezone": "America/New_York"
    },
    "theme": "dark",
    "language": "en"
  },
  "deviceTokens": ["fcm-token-123"],
  "createdAt": "2025-01-15T10:00:00Z"
}
```

---

#### 3.3.2 Update User Profile

**Function:** `update_profile`

**Trigger:** API Gateway PUT `/users/me`

**Allowed Updates:**
- name
- preferences

---

#### 3.3.3 Update Notification Preferences

**Function:** `update_preferences`

**Trigger:** API Gateway PUT `/users/me/preferences`

---

#### 3.3.4 Register Device Token

**Function:** `register_device_token`

**Trigger:** API Gateway POST `/users/me/device-tokens`

**Purpose:** Register FCM token for push notifications

**Input:**
```json
{
  "token": "fcm-token-xyz",
  "platform": "android"
}
```

---

#### 3.3.5 List Users (Admin)

**Function:** `list_users`

**Trigger:** API Gateway GET `/users`

**Purpose:** List all users in organization (admin only)

---

#### 3.3.6 Create User (Admin)

**Function:** `create_user`

**Trigger:** API Gateway POST `/users`

**Purpose:** Create new user account

---

#### 3.3.7 Update User Role (Admin)

**Function:** `update_user_role`

**Trigger:** API Gateway PUT `/users/{userId}/role`

**Purpose:** Change user role

---

### 3.4 Firmware Management API

#### 3.4.1 Upload Firmware

**Function:** `upload_firmware`

**Trigger:** API Gateway POST `/firmware/upload`

**Processing Steps:**
1. Validate user permissions (admin)
2. Validate firmware metadata
3. Generate pre-signed S3 URL for upload
4. Return upload URL

**Output:**
```json
{
  "firmwareId": "fw-123",
  "uploadUrl": "https://s3.amazonaws.com/...",
  "fields": {
    "key": "firmware/fw-123.bin",
    "policy": "...",
    "signature": "..."
  }
}
```

**Note:** Actual firmware upload happens directly to S3 from client using pre-signed URL.

---

#### 3.4.2 List Firmware

**Function:** `list_firmware`

**Trigger:** API Gateway GET `/firmware`

**Purpose:** List available firmware versions

---

#### 3.4.3 Get Firmware

**Function:** `get_firmware`

**Trigger:** API Gateway GET `/firmware/{firmwareId}`

**Purpose:** Get firmware details

---

#### 3.4.4 Create Deployment

**Function:** `create_deployment`

**Trigger:** API Gateway POST `/firmware/deployments`

**Input:**
```json
{
  "firmwareId": "fw-123",
  "targetDevices": ["dev-abc123", "dev-def456"],
  "strategy": "staged",
  "batchSize": 10,
  "schedule": {
    "type": "scheduled",
    "startTime": "2025-11-15T14:00:00Z"
  }
}
```

**Processing Steps:**
1. Validate permissions
2. Validate firmware compatibility with target devices
3. Create Deployment entity
4. Split devices into batches
5. Save to DynamoDB
6. Schedule EventBridge rule for deployment start
7. Return deployment details

---

#### 3.4.5 Get Deployment

**Function:** `get_deployment`

**Trigger:** API Gateway GET `/firmware/deployments/{deploymentId}`

**Purpose:** Get deployment status and progress

**Output:**
```json
{
  "deploymentId": "dep-456",
  "firmwareId": "fw-123",
  "firmwareVersion": "v2.1.0",
  "strategy": "staged",
  "status": "in_progress",
  "progress": {
    "total": 100,
    "succeeded": 85,
    "failed": 2,
    "inProgress": 8,
    "pending": 5
  },
  "batches": [
    {
      "batchId": 1,
      "devices": 10,
      "status": "completed",
      "successRate": 100
    },
    {
      "batchId": 2,
      "devices": 10,
      "status": "in_progress",
      "successRate": 80
    }
  ],
  "startedAt": "2025-11-15T14:00:00Z"
}
```

---

#### 3.4.6 List Deployments

**Function:** `list_deployments`

**Trigger:** API Gateway GET `/firmware/deployments`

**Purpose:** List firmware deployments

---

### 3.5 Analytics API

#### 3.5.1 Get Dashboard Stats

**Function:** `get_dashboard_stats`

**Trigger:** API Gateway GET `/analytics/dashboard`

**Purpose:** Get real-time statistics for dashboard

**Output:**
```json
{
  "devices": {
    "total": 1500,
    "online": 1450,
    "offline": 45,
    "maintenance": 5
  },
  "alerts": {
    "active": 12,
    "critical": 2,
    "warning": 8,
    "info": 2
  },
  "dataVolume": {
    "today": 12500000,  // bytes
    "thisMonth": 385000000
  },
  "trends": {
    "devicesOnline": "+2.5%",  // vs yesterday
    "activeAlerts": "-15%"
  }
}
```

---

#### 3.5.2 Query Sensor Data

**Function:** `query_sensor_data`

**Trigger:** API Gateway POST `/analytics/query`

**Input:**
```json
{
  "deviceIds": ["dev-abc123", "dev-def456"],
  "metrics": ["temperature", "humidity"],
  "startTime": "2025-11-14T00:00:00Z",
  "endTime": "2025-11-15T00:00:00Z",
  "aggregation": {
    "interval": "15m",
    "function": "avg"
  }
}
```

**Processing Steps:**
1. Validate time range
2. Build Timestream query
3. Execute query
4. Format results
5. Return data

---

#### 3.5.3 Generate Report

**Function:** `generate_report`

**Trigger:** API Gateway POST `/analytics/reports`

**Input:**
```json
{
  "reportType": "device-uptime",
  "parameters": {
    "deviceIds": ["dev-abc123"],
    "startDate": "2025-10-01",
    "endDate": "2025-10-31"
  },
  "format": "pdf"
}
```

**Processing Steps:**
1. Validate report type
2. Queue report generation job (async via SQS)
3. Return job ID

**Output:**
```json
{
  "reportId": "report-789",
  "status": "queued",
  "estimatedCompletionTime": "2025-11-15T10:10:00Z"
}
```

**Note:** Actual report generation happens asynchronously. Client polls for completion.

---

#### 3.5.4 Export Data

**Function:** `export_data`

**Trigger:** API Gateway POST `/analytics/export`

**Purpose:** Export sensor data to CSV/JSON

---

## 4. Stream Processing Functions

### 4.1 Kinesis Consumer

**Function:** `kinesis_consumer`

**Trigger:** Kinesis Data Stream (batch size: 100, batch window: 5 seconds)

**Purpose:** Process incoming device telemetry data

**Input (Kinesis Record):**
```json
{
  "deviceId": "dev-abc123",
  "timestamp": 1700056800000,
  "data": {
    "temperature": 23.5,
    "humidity": 45,
    "co2": 450,
    "battery": 85
  }
}
```

**Processing Steps:**
1. Deserialize records
2. Validate data against device schema
3. Transform data (unit conversion, derived metrics)
4. Detect anomalies
5. **Parallel writes:**
   - Write to Timestream (time-series storage)
   - Update device last reading in DynamoDB
   - Update device last seen timestamp
6. Publish metrics to CloudWatch
7. Return success/failure per record

**Error Handling:**
- Individual record failures sent to DLQ
- Partial batch failures with batch item failures response

---

### 4.2 IoT Rule Processor

**Function:** `iot_rule_processor`

**Trigger:** IoT Core Rule action

**Purpose:** Alternative to Kinesis, direct processing from IoT Core

---

### 4.3 Alert Rule Evaluator

**Function:** `alert_evaluator`

**Trigger:** EventBridge (scheduled every 1 minute)

**Purpose:** Evaluate alert rules and generate alerts

**Processing Steps:**
1. Fetch all active alert rules from DynamoDB
2. Group rules by metric type
3. For each metric type:
   - Query Timestream for recent data (last 5 minutes)
   - For each device with data:
     - Evaluate applicable rules
     - Check if condition met
     - Check de-duplication (alert already exists)
     - Check cooldown period
     - If triggered, create alert
4. Batch write alerts to DynamoDB
5. Send alerts to SQS for notification dispatch
6. Log metrics (rules evaluated, alerts generated)

**Optimization:**
- Cache rules in Lambda execution context
- Parallel rule evaluation
- Batch operations

---

### 4.4 Notification Dispatcher

**Function:** `notification_dispatcher`

**Trigger:** SQS Alert Queue (batch size: 10)

**Purpose:** Dispatch notifications for alerts

**Processing Steps:**
1. Receive alert messages from SQS
2. For each alert:
   - Fetch alert details (from DynamoDB)
   - Fetch device details
   - Fetch affected users (based on subscriptions)
   - For each user:
     - Get notification preferences
     - Check quiet hours
     - Determine notification channels (based on severity + prefs)
     - Generate notification content (using templates)
     - Send notifications:
       - Email (via SES)
       - Push (via FCM)
       - SMS (via SNS, optional)
     - Log notification delivery
3. Update alert with notification sent status
4. Return success/failure per message

**Parallel Processing:**
- Send notifications to multiple users in parallel
- Send multiple channels in parallel

---

### 4.5 Firmware Processor

**Function:** `firmware_processor`

**Trigger:** S3 event (ObjectCreated on firmware bucket)

**Purpose:** Process uploaded firmware

**Processing Steps:**
1. Receive S3 event
2. Download firmware file
3. Calculate checksum (SHA-256)
4. Validate firmware format
5. Extract metadata (if embedded)
6. Optional: Virus scan (ClamAV)
7. Update firmware record in DynamoDB
8. Publish success/failure event
9. Notify admin

---

### 4.6 Deployment Orchestrator

**Function:** `deployment_orchestrator`

**Trigger:** EventBridge (scheduled based on deployment schedule)

**Purpose:** Orchestrate firmware deployment

**Processing Steps:**
1. Fetch deployment details from DynamoDB
2. Get next batch to deploy
3. For each device in batch:
   - Check device online status
   - Create IoT Job for firmware update
4. Update deployment progress
5. Schedule monitoring

**State Management:**
- Track batch progress
- Determine if should proceed to next batch
- Handle rollback if success rate < threshold

---

### 4.7 Deployment Monitor

**Function:** `deployment_monitor`

**Trigger:** IoT Jobs status change event

**Purpose:** Monitor firmware deployment progress

**Processing Steps:**
1. Receive job status event
2. Update deployment statistics
3. Check batch success rate
4. If batch complete:
   - If success rate >= 95%, proceed to next batch
   - If success rate < 95%, halt deployment and alert
5. If all batches complete, mark deployment as complete
6. Notify admins of deployment status

---

### 4.8 Real-Time Notifier

**Function:** `realtime_notifier`

**Trigger:** DynamoDB Stream (devices table, sensor data updates)

**Purpose:** Push real-time updates to WebSocket clients

**Processing Steps:**
1. Receive DynamoDB stream event
2. Determine what changed (device status, new reading, etc.)
3. Fetch active WebSocket connections from DynamoDB
4. Filter connections by subscriptions
5. Send update message to subscribed connections via API Gateway WebSocket
6. Handle disconnected clients

---

## 5. WebSocket Functions

### 5.1 Connect Handler

**Function:** `websocket_connect`

**Trigger:** API Gateway WebSocket $connect route

**Purpose:** Handle new WebSocket connection

**Processing Steps:**
1. Validate JWT token from query string
2. Extract userId
3. Store connection:
   - connectionId
   - userId
   - timestamp
4. Save to DynamoDB (Connections table)
5. Return success

---

### 5.2 Disconnect Handler

**Function:** `websocket_disconnect`

**Trigger:** API Gateway WebSocket $disconnect route

**Purpose:** Handle WebSocket disconnection

**Processing Steps:**
1. Remove connection from DynamoDB
2. Clean up subscriptions
3. Return success

---

### 5.3 Subscribe Handler

**Function:** `websocket_subscribe`

**Trigger:** API Gateway WebSocket route (action: subscribe)

**Message:**
```json
{
  "action": "subscribe",
  "deviceIds": ["dev-abc123", "dev-def456"]
}
```

**Processing Steps:**
1. Validate user has access to devices
2. Update connection record with subscriptions
3. Send confirmation message

---

### 5.4 Unsubscribe Handler

**Function:** `websocket_unsubscribe`

**Trigger:** API Gateway WebSocket route (action: unsubscribe)

**Purpose:** Unsubscribe from device updates

---

## 6. Scheduled Functions

### 6.1 Data Archival

**Function:** `data_archival`

**Trigger:** EventBridge (daily at 2 AM UTC)

**Purpose:** Archive old data from Timestream to S3

**Processing Steps:**
1. Query Timestream for data older than retention period
2. Export to S3 in Parquet format
3. Delete from Timestream
4. Log archival stats

---

### 6.2 Cleanup Old Alerts

**Function:** `cleanup_old_alerts`

**Trigger:** EventBridge (weekly)

**Purpose:** Clean up resolved alerts older than 90 days

**Processing Steps:**
1. Query DynamoDB for old resolved alerts
2. Archive to S3
3. Delete from DynamoDB
4. Log cleanup stats

---

### 6.3 Health Check

**Function:** `health_check`

**Trigger:** EventBridge (every hour)

**Purpose:** Monitor system health

**Processing Steps:**
1. Check service health:
   - DynamoDB table status
   - Timestream database availability
   - Kinesis stream status
   - SQS queue depth
2. Check metrics:
   - Lambda error rates
   - API Gateway 5xx errors
   - Dead-letter queue depth
3. If issues detected, create alert
4. Publish health metrics

---

### 6.4 Usage Report

**Function:** `usage_report`

**Trigger:** EventBridge (monthly)

**Purpose:** Generate monthly usage report

**Processing Steps:**
1. Query data volume
2. Calculate costs
3. Generate report
4. Send to admins via email

---

## 7. Authentication & Authorization

### 7.1 Cognito Integration

**User Pool:**
- Email/password authentication
- MFA support
- Custom attributes (organizationId, role)

**JWT Token Structure:**
```json
{
  "sub": "user-456",
  "email": "john.doe@example.com",
  "custom:organizationId": "org-789",
  "custom:role": "operator",
  "exp": 1700060400
}
```

### 7.2 Authorization Middleware

**Implementation:**
```python
def authorize(required_role: str):
    def decorator(func):
        def wrapper(event, context):
            # Extract JWT from Authorization header
            claims = decode_jwt(event['headers']['Authorization'])

            # Check role
            if not has_role(claims, required_role):
                return {
                    'statusCode': 403,
                    'body': json.dumps({'error': 'Forbidden'})
                }

            # Add claims to event
            event['user'] = claims
            return func(event, context)
        return wrapper
    return decorator

@authorize('admin')
def delete_device(event, context):
    # Only admins can delete devices
    pass
```

## 8. Error Handling Strategy

### 8.1 Error Types

```python
# Domain Exceptions
class DeviceNotFoundError(DomainException):
    pass

class InvalidDeviceDataError(DomainException):
    pass

# Infrastructure Exceptions
class DatabaseError(InfrastructureException):
    pass

class ExternalServiceError(InfrastructureException):
    pass
```

### 8.2 Error Response Format

```json
{
  "error": {
    "code": "DEVICE_NOT_FOUND",
    "message": "Device with ID 'dev-abc123' not found",
    "details": {
      "deviceId": "dev-abc123"
    },
    "requestId": "req-xyz789"
  }
}
```

### 8.3 Error Handling Flow

```python
def lambda_handler(event, context):
    try:
        # Process request
        result = process_request(event)
        return {
            'statusCode': 200,
            'body': json.dumps(result)
        }
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': str(e)})
        }
    except NotFoundError as e:
        logger.info(f"Resource not found: {e}")
        return {
            'statusCode': 404,
            'body': json.dumps({'error': str(e)})
        }
    except UnauthorizedError as e:
        logger.warning(f"Unauthorized access: {e}")
        return {
            'statusCode': 403,
            'body': json.dumps({'error': str(e)})
        }
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Internal server error'})
        }
```

## 9. Logging & Monitoring

### 9.1 Structured Logging

```python
import logging
import json

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def log_event(level, message, **kwargs):
    log_entry = {
        'level': level,
        'message': message,
        'timestamp': datetime.utcnow().isoformat(),
        **kwargs
    }
    logger.log(getattr(logging, level), json.dumps(log_entry))

# Usage
log_event('INFO', 'Device registered', deviceId='dev-abc123', userId='user-456')
```

### 9.2 X-Ray Tracing

```python
from aws_xray_sdk.core import xray_recorder

@xray_recorder.capture('device_service')
def register_device(device_data):
    # Automatically traced
    pass
```

### 9.3 Custom Metrics

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

def publish_metric(metric_name, value, unit='Count'):
    cloudwatch.put_metric_data(
        Namespace='IoTMonitoring',
        MetricData=[
            {
                'MetricName': metric_name,
                'Value': value,
                'Unit': unit,
                'Timestamp': datetime.utcnow()
            }
        ]
    )

# Usage
publish_metric('DevicesRegistered', 1)
publish_metric('AlertsGenerated', 5)
```

## 10. Testing Strategy

### 10.1 Unit Tests

```python
# tests/unit/domain/test_device_service.py

def test_register_device_success():
    # Arrange
    mock_repo = MockDeviceRepository()
    service = DeviceService(mock_repo)
    device_data = DeviceCreateDTO(...)

    # Act
    device = service.register_device(device_data)

    # Assert
    assert device.deviceId is not None
    assert device.status == 'registered'
    assert mock_repo.save_called
```

### 10.2 Integration Tests

```python
# tests/integration/test_device_api.py

@pytest.mark.integration
def test_register_device_api():
    # Use real DynamoDB Local
    response = invoke_lambda('register_device', {
        'body': json.dumps({...})
    })

    assert response['statusCode'] == 201
    assert 'deviceId' in json.loads(response['body'])
```

### 10.3 E2E Tests

```python
# tests/e2e/test_complete_workflow.py

def test_device_registration_to_alert():
    # Register device
    device = register_device(...)

    # Simulate sensor data
    send_sensor_data(device_id, temperature=45)

    # Wait for alert
    time.sleep(65)  # Wait for alert evaluator

    # Check alert created
    alerts = get_alerts(device_id)
    assert len(alerts) > 0
    assert alerts[0]['condition'] == 'temperature > 40'
```

## 11. Performance Optimization

### 11.1 Lambda Optimization

**Cold Start Reduction:**
- Use Lambda Layers for dependencies
- Minimal imports in handler
- Provisioned concurrency for critical functions

**Memory Tuning:**
```yaml
functions:
  register_device:
    handler: src/functions/device/register_device.handler
    memorySize: 512  # Tuned based on profiling
    timeout: 30
    reservedConcurrency: 10
```

**Connection Pooling:**
```python
# Initialize outside handler for reuse
dynamodb = boto3.resource('dynamodb')
devices_table = dynamodb.Table('iot-monitoring-devices')

def lambda_handler(event, context):
    # Reuse connection
    devices_table.put_item(Item={...})
```

### 11.2 Database Optimization

**DynamoDB:**
- Use batch operations where possible
- Implement caching (Lambda execution context)
- Optimize GSI for query patterns

**Timestream:**
- Query only necessary time ranges
- Use aggregation in queries (not in code)
- Implement query result caching

### 11.3 Asynchronous Processing

```python
# Don't wait for non-critical operations
sqs = boto3.client('sqs')

def send_notification_async(alert_data):
    # Send to SQS, don't wait for processing
    sqs.send_message(
        QueueUrl=ALERT_QUEUE_URL,
        MessageBody=json.dumps(alert_data)
    )
```

## 12. Security Best Practices

### 12.1 Input Validation

```python
from pydantic import BaseModel, validator

class DeviceCreateRequest(BaseModel):
    deviceType: str
    name: str
    location: dict

    @validator('name')
    def validate_name(cls, v):
        if len(v) < 3 or len(v) > 100:
            raise ValueError('Name must be 3-100 characters')
        return v
```

### 12.2 Secrets Management

```python
import boto3
from functools import lru_cache

@lru_cache(maxsize=1)
def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

# Usage
fcm_credentials = get_secret('prod/fcm/credentials')
```

### 12.3 IAM Least Privilege

```yaml
# serverless.yml
provider:
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
          Resource: arn:aws:dynamodb:region:account:table/iot-monitoring-devices
```

---

**Document Version:** 1.0
**Last Updated:** 2025-11-15
**Document Owner:** Backend Team

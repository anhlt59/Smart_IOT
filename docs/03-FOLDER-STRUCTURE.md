# Project Folder Structure - IoT Monitoring Application

## 1. Root Directory Structure

```
Smart_IOT/
├── backend/                    # Backend services (Python + Serverless Framework)
├── frontend/                   # Frontend application (Vue.js)
├── infrastructure/             # Infrastructure as Code (Serverless Framework)
├── docs/                       # Documentation
├── scripts/                    # Utility scripts (deployment, data migration, etc.)
├── .github/                    # GitHub Actions workflows
├── .gitignore                  # Git ignore file
├── README.md                   # Project overview
├── LICENSE                     # License information
└── package.json                # Root package.json for monorepo management
```

## 2. Backend Structure (Hexagonal Architecture)

```
backend/
├── src/
│   ├── functions/              # Lambda function handlers (Adapters - Driving)
│   │   ├── device/
│   │   │   ├── register_device.py           # POST /devices
│   │   │   ├── get_device.py                # GET /devices/{deviceId}
│   │   │   ├── list_devices.py              # GET /devices
│   │   │   ├── update_device.py             # PUT /devices/{deviceId}
│   │   │   ├── delete_device.py             # DELETE /devices/{deviceId}
│   │   │   ├── get_device_history.py        # GET /devices/{deviceId}/history
│   │   │   └── __init__.py
│   │   │
│   │   ├── alert/
│   │   │   ├── list_alerts.py               # GET /alerts
│   │   │   ├── get_alert.py                 # GET /alerts/{alertId}
│   │   │   ├── acknowledge_alert.py         # POST /alerts/{alertId}/acknowledge
│   │   │   ├── resolve_alert.py             # POST /alerts/{alertId}/resolve
│   │   │   ├── create_alert_rule.py         # POST /alert-rules
│   │   │   ├── update_alert_rule.py         # PUT /alert-rules/{ruleId}
│   │   │   ├── delete_alert_rule.py         # DELETE /alert-rules/{ruleId}
│   │   │   ├── list_alert_rules.py          # GET /alert-rules
│   │   │   └── __init__.py
│   │   │
│   │   ├── user/
│   │   │   ├── get_profile.py               # GET /users/me
│   │   │   ├── update_profile.py            # PUT /users/me
│   │   │   ├── update_preferences.py        # PUT /users/me/preferences
│   │   │   ├── register_device_token.py     # POST /users/me/device-tokens
│   │   │   ├── list_users.py                # GET /users (admin only)
│   │   │   ├── create_user.py               # POST /users (admin only)
│   │   │   ├── update_user_role.py          # PUT /users/{userId}/role (admin only)
│   │   │   └── __init__.py
│   │   │
│   │   ├── firmware/
│   │   │   ├── upload_firmware.py           # POST /firmware/upload
│   │   │   ├── list_firmware.py             # GET /firmware
│   │   │   ├── get_firmware.py              # GET /firmware/{firmwareId}
│   │   │   ├── create_deployment.py         # POST /firmware/deployments
│   │   │   ├── get_deployment.py            # GET /firmware/deployments/{deploymentId}
│   │   │   ├── list_deployments.py          # GET /firmware/deployments
│   │   │   └── __init__.py
│   │   │
│   │   ├── analytics/
│   │   │   ├── get_dashboard_stats.py       # GET /analytics/dashboard
│   │   │   ├── query_sensor_data.py         # POST /analytics/query
│   │   │   ├── generate_report.py           # POST /analytics/reports
│   │   │   ├── export_data.py               # POST /analytics/export
│   │   │   └── __init__.py
│   │   │
│   │   ├── stream_processing/               # Event-driven functions
│   │   │   ├── kinesis_consumer.py          # Process Kinesis stream
│   │   │   ├── iot_rule_processor.py        # Process IoT Core rule actions
│   │   │   ├── alert_evaluator.py           # Scheduled: Evaluate alert rules
│   │   │   ├── notification_dispatcher.py   # Process SQS alert queue
│   │   │   ├── firmware_processor.py        # S3 event: Process uploaded firmware
│   │   │   ├── deployment_orchestrator.py   # EventBridge: Orchestrate FOTA
│   │   │   ├── deployment_monitor.py        # IoT Jobs event: Monitor deployment
│   │   │   ├── realtime_notifier.py         # Push updates via WebSocket
│   │   │   └── __init__.py
│   │   │
│   │   ├── websocket/                       # WebSocket handlers
│   │   │   ├── connect.py                   # $connect route
│   │   │   ├── disconnect.py                # $disconnect route
│   │   │   ├── subscribe.py                 # Subscribe to device updates
│   │   │   ├── unsubscribe.py               # Unsubscribe from device updates
│   │   │   └── __init__.py
│   │   │
│   │   ├── auth/                            # Authentication helpers
│   │   │   ├── authorizer.py                # Custom authorizer (if needed)
│   │   │   ├── post_confirmation.py         # Cognito trigger: Post-confirmation
│   │   │   └── __init__.py
│   │   │
│   │   └── scheduled/                       # Scheduled tasks
│   │       ├── data_archival.py             # Daily: Archive old data
│   │       ├── cleanup_old_alerts.py        # Weekly: Cleanup resolved alerts
│   │       ├── health_check.py              # Hourly: Check system health
│   │       ├── usage_report.py              # Monthly: Generate usage reports
│   │       └── __init__.py
│   │
│   ├── domain/                  # Core Business Logic (Hexagonal Core)
│   │   ├── entities/            # Domain entities (business objects)
│   │   │   ├── device.py
│   │   │   │   └── class Device:
│   │   │   │         - deviceId: str
│   │   │   │         - organizationId: str
│   │   │   │         - deviceType: str
│   │   │   │         - status: DeviceStatus
│   │   │   │         - location: DeviceLocation
│   │   │   │         - connectivity: Connectivity
│   │   │   │         - Methods: isOnline(), needsUpdate(), toDict(), fromDict()
│   │   │   │
│   │   │   ├── alert.py
│   │   │   │   └── class Alert:
│   │   │   │         - alertId: str
│   │   │   │         - ruleId: str
│   │   │   │         - deviceId: str
│   │   │   │         - severity: AlertSeverity
│   │   │   │         - status: AlertStatus
│   │   │   │         - Methods: canAcknowledge(user), shouldEscalate()
│   │   │   │
│   │   │   ├── alert_rule.py
│   │   │   │   └── class AlertRule:
│   │   │   │         - ruleId: str
│   │   │   │         - condition: AlertCondition
│   │   │   │         - severity: AlertSeverity
│   │   │   │         - Methods: evaluate(sensorData), isApplicableTo(device)
│   │   │   │
│   │   │   ├── user.py
│   │   │   │   └── class User:
│   │   │   │         - userId: str
│   │   │   │         - email: str
│   │   │   │         - role: UserRole
│   │   │   │         - preferences: UserPreferences
│   │   │   │         - Methods: hasPermission(resource, action), canReceiveNotification(channel)
│   │   │   │
│   │   │   ├── firmware.py
│   │   │   │   └── class Firmware:
│   │   │   │         - firmwareId: str
│   │   │   │         - version: FirmwareVersion
│   │   │   │         - deviceTypes: List[str]
│   │   │   │         - Methods: isCompatibleWith(device), compareVersion(other)
│   │   │   │
│   │   │   ├── deployment.py
│   │   │   │   └── class Deployment:
│   │   │   │         - deploymentId: str
│   │   │   │         - firmwareId: str
│   │   │   │         - strategy: DeploymentStrategy
│   │   │   │         - batches: List[DeploymentBatch]
│   │   │   │         - Methods: canProceedToNextBatch(), calculateSuccessRate()
│   │   │   │
│   │   │   └── __init__.py
│   │   │
│   │   ├── value_objects/       # Immutable value objects
│   │   │   ├── device_location.py
│   │   │   │   └── class DeviceLocation:
│   │   │   │         - lat: float
│   │   │   │         - lon: float
│   │   │   │         - address: str
│   │   │   │         - Methods: distanceTo(other), __eq__(), __hash__()
│   │   │   │
│   │   │   ├── alert_severity.py
│   │   │   │   └── class AlertSeverity(Enum):
│   │   │   │         INFO, WARNING, CRITICAL
│   │   │   │
│   │   │   ├── sensor_reading.py
│   │   │   │   └── class SensorReading:
│   │   │   │         - value: float
│   │   │   │         - unit: str
│   │   │   │         - timestamp: datetime
│   │   │   │
│   │   │   ├── firmware_version.py
│   │   │   │   └── class FirmwareVersion:
│   │   │   │         - major: int
│   │   │   │         - minor: int
│   │   │   │         - patch: int
│   │   │   │         - Methods: __lt__(), __eq__(), __str__()
│   │   │   │
│   │   │   └── __init__.py
│   │   │
│   │   ├── services/            # Domain services (business logic)
│   │   │   ├── device_service.py
│   │   │   │   └── class DeviceService:
│   │   │   │         Methods:
│   │   │   │         - registerDevice(deviceData) -> Device
│   │   │   │         - updateDeviceStatus(deviceId, status) -> Device
│   │   │   │         - getDevicesByOrganization(orgId, filters) -> List[Device]
│   │   │   │         - getDeviceHistory(deviceId, timeRange) -> List[SensorReading]
│   │   │   │         - checkDeviceHealth(device) -> HealthStatus
│   │   │   │
│   │   │   ├── alert_service.py
│   │   │   │   └── class AlertService:
│   │   │   │         Methods:
│   │   │   │         - evaluateRules(devices, sensorData) -> List[Alert]
│   │   │   │         - createAlert(alertData) -> Alert
│   │   │   │         - acknowledgeAlert(alertId, userId) -> Alert
│   │   │   │         - resolveAlert(alertId) -> Alert
│   │   │   │         - shouldTriggerAlert(rule, device, data) -> bool
│   │   │   │
│   │   │   ├── user_service.py
│   │   │   │   └── class UserService:
│   │   │   │         Methods:
│   │   │   │         - createUser(userData) -> User
│   │   │   │         - updatePreferences(userId, preferences) -> User
│   │   │   │         - assignRole(userId, role) -> User
│   │   │   │         - getUsersByOrganization(orgId) -> List[User]
│   │   │   │
│   │   │   ├── firmware_service.py
│   │   │   │   └── class FirmwareService:
│   │   │   │         Methods:
│   │   │   │         - uploadFirmware(firmwareData, fileStream) -> Firmware
│   │   │   │         - createDeployment(firmwareId, targetDevices, strategy) -> Deployment
│   │   │   │         - monitorDeployment(deploymentId) -> DeploymentStatus
│   │   │   │         - rollbackDeployment(deploymentId) -> Deployment
│   │   │   │
│   │   │   ├── analytics_service.py
│   │   │   │   └── class AnalyticsService:
│   │   │   │         Methods:
│   │   │   │         - getDashboardStats(orgId) -> DashboardStats
│   │   │   │         - querySensorData(query) -> QueryResult
│   │   │   │         - generateReport(reportType, params) -> Report
│   │   │   │         - detectAnomalies(deviceId, metric) -> List[Anomaly]
│   │   │   │
│   │   │   ├── notification_service.py
│   │   │   │   └── class NotificationService:
│   │   │   │         Methods:
│   │   │   │         - dispatchNotification(alert, users) -> List[Notification]
│   │   │   │         - determineChannels(alert, user) -> List[Channel]
│   │   │   │         - generateContent(alert, template) -> NotificationContent
│   │   │   │
│   │   │   └── __init__.py
│   │   │
│   │   └── ports/               # Interfaces (Dependency Inversion)
│   │       ├── repositories/    # Repository interfaces
│   │       │   ├── i_device_repository.py
│   │       │   │   └── class IDeviceRepository(ABC):
│   │       │   │         - save(device: Device) -> Device
│   │       │   │         - findById(deviceId: str) -> Optional[Device]
│   │       │   │         - findByOrganization(orgId: str) -> List[Device]
│   │       │   │         - delete(deviceId: str) -> bool
│   │       │   │
│   │       │   ├── i_alert_repository.py
│   │       │   ├── i_user_repository.py
│   │       │   ├── i_firmware_repository.py
│   │       │   ├── i_deployment_repository.py
│   │       │   ├── i_timeseries_repository.py
│   │       │   │   └── class ITimeSeriesRepository(ABC):
│   │       │   │         - writeSensorData(data: SensorData) -> bool
│   │       │   │         - queryRecentData(deviceId: str, timeRange: TimeRange) -> List[SensorReading]
│   │       │   │         - queryAggregated(query: AggregationQuery) -> QueryResult
│   │       │   │
│   │       │   └── __init__.py
│   │       │
│   │       └── external/        # External service interfaces
│   │           ├── i_notification_provider.py
│   │           │   └── class INotificationProvider(ABC):
│   │           │         - sendEmail(recipient, subject, body) -> bool
│   │           │         - sendPush(userId, title, message) -> bool
│   │           │         - sendSMS(phoneNumber, message) -> bool
│   │           │
│   │           ├── i_storage_provider.py
│   │           │   └── class IStorageProvider(ABC):
│   │           │         - uploadFile(bucket, key, data) -> str
│   │           │         - downloadFile(bucket, key) -> bytes
│   │           │         - generatePresignedUrl(bucket, key) -> str
│   │           │
│   │           ├── i_iot_provider.py
│   │           │   └── class IIoTProvider(ABC):
│   │           │         - createJob(jobDocument, targets) -> Job
│   │           │         - getJobStatus(jobId) -> JobStatus
│   │           │         - publishMessage(topic, payload) -> bool
│   │           │
│   │           └── __init__.py
│   │
│   ├── infrastructure/           # Infrastructure Adapters (Hexagonal - Driven Adapters)
│   │   ├── repositories/        # Database implementations
│   │   │   ├── dynamodb_device_repository.py
│   │   │   │   └── class DynamoDBDeviceRepository(IDeviceRepository):
│   │   │   │         - Implements all IDeviceRepository methods
│   │   │   │         - Uses boto3 DynamoDB client
│   │   │   │
│   │   │   ├── dynamodb_alert_repository.py
│   │   │   ├── dynamodb_user_repository.py
│   │   │   ├── dynamodb_firmware_repository.py
│   │   │   ├── dynamodb_deployment_repository.py
│   │   │   ├── timestream_repository.py
│   │   │   │   └── class TimestreamRepository(ITimeSeriesRepository):
│   │   │   │         - Implements time-series data operations
│   │   │   │         - Uses boto3 Timestream client
│   │   │   │
│   │   │   └── __init__.py
│   │   │
│   │   ├── external/            # External service implementations
│   │   │   ├── ses_notification_provider.py
│   │   │   │   └── class SESNotificationProvider(INotificationProvider):
│   │   │   │         - sendEmail() using boto3 SES
│   │   │   │
│   │   │   ├── fcm_notification_provider.py
│   │   │   │   └── class FCMNotificationProvider(INotificationProvider):
│   │   │   │         - sendPush() using Firebase Admin SDK
│   │   │   │
│   │   │   ├── sns_notification_provider.py
│   │   │   │   └── class SNSNotificationProvider(INotificationProvider):
│   │   │   │         - sendSMS() using boto3 SNS
│   │   │   │
│   │   │   ├── s3_storage_provider.py
│   │   │   │   └── class S3StorageProvider(IStorageProvider):
│   │   │   │         - File operations using boto3 S3
│   │   │   │
│   │   │   ├── iot_core_provider.py
│   │   │   │   └── class IoTCoreProvider(IIoTProvider):
│   │   │   │         - IoT operations using boto3 IoT
│   │   │   │
│   │   │   ├── soracom_client.py
│   │   │   │   └── class SoracomClient:
│   │   │   │         - Integration with Soracom API
│   │   │   │
│   │   │   └── __init__.py
│   │   │
│   │   ├── messaging/           # Message queue implementations
│   │   │   ├── sqs_client.py
│   │   │   ├── kinesis_client.py
│   │   │   └── __init__.py
│   │   │
│   │   └── utils/               # Infrastructure utilities
│   │       ├── connection_pool.py
│   │       ├── retry_handler.py
│   │       └── __init__.py
│   │
│   ├── shared/                  # Shared utilities
│   │   ├── config/
│   │   │   ├── settings.py      # Environment-based configuration
│   │   │   ├── constants.py     # Application constants
│   │   │   └── __init__.py
│   │   │
│   │   ├── middleware/
│   │   │   ├── error_handler.py # Global error handling
│   │   │   ├── logger.py        # Structured logging
│   │   │   ├── cors.py          # CORS handling
│   │   │   ├── request_validator.py  # Request validation
│   │   │   └── __init__.py
│   │   │
│   │   ├── exceptions/
│   │   │   ├── base.py          # Base exception classes
│   │   │   ├── domain_exceptions.py   # Domain-specific exceptions
│   │   │   ├── infrastructure_exceptions.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── schemas/             # Validation schemas (Pydantic)
│   │   │   ├── device_schemas.py
│   │   │   ├── alert_schemas.py
│   │   │   ├── user_schemas.py
│   │   │   ├── firmware_schemas.py
│   │   │   └── __init__.py
│   │   │
│   │   ├── utils/
│   │   │   ├── datetime_helper.py
│   │   │   ├── crypto_helper.py
│   │   │   ├── validation_helper.py
│   │   │   ├── response_builder.py
│   │   │   └── __init__.py
│   │   │
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── tests/                       # Tests
│   ├── unit/                    # Unit tests
│   │   ├── domain/
│   │   │   ├── test_device.py
│   │   │   ├── test_alert.py
│   │   │   ├── test_device_service.py
│   │   │   ├── test_alert_service.py
│   │   │   └── ...
│   │   │
│   │   ├── infrastructure/
│   │   │   ├── test_dynamodb_repository.py
│   │   │   ├── test_timestream_repository.py
│   │   │   └── ...
│   │   │
│   │   └── functions/
│   │       ├── test_register_device.py
│   │       └── ...
│   │
│   ├── integration/             # Integration tests
│   │   ├── test_device_api.py
│   │   ├── test_alert_flow.py
│   │   ├── test_firmware_deployment.py
│   │   └── ...
│   │
│   ├── e2e/                     # End-to-end tests
│   │   ├── test_complete_workflow.py
│   │   └── ...
│   │
│   ├── fixtures/                # Test fixtures
│   │   ├── device_fixtures.py
│   │   ├── alert_fixtures.py
│   │   └── ...
│   │
│   ├── mocks/                   # Mock objects
│   │   ├── mock_repositories.py
│   │   ├── mock_external_services.py
│   │   └── ...
│   │
│   └── conftest.py              # Pytest configuration
│
├── layers/                      # Lambda Layers
│   ├── common/
│   │   ├── python/
│   │   │   └── requirements.txt # Common dependencies
│   │   └── README.md
│   │
│   └── firebase/
│       ├── python/
│       │   ├── firebase_admin/  # Firebase Admin SDK
│       │   └── requirements.txt
│       └── README.md
│
├── serverless.yml               # Serverless Framework configuration
├── requirements.txt             # Python dependencies
├── requirements-dev.txt         # Development dependencies
├── pytest.ini                   # Pytest configuration
├── .pylintrc                    # Linting configuration
├── mypy.ini                     # Type checking configuration
└── README.md                    # Backend documentation
```

## 3. Frontend Structure (Vue.js + TypeScript)

```
frontend/
├── public/                      # Static files
│   ├── index.html
│   ├── favicon.ico
│   └── assets/
│       ├── images/
│       └── icons/
│
├── src/
│   ├── assets/                  # Static resources (images, fonts, etc.)
│   │   ├── images/
│   │   │   ├── logo.png
│   │   │   ├── device-icons/
│   │   │   └── illustrations/
│   │   │
│   │   ├── fonts/
│   │   └── styles/              # Global styles (if not using Tailwind exclusively)
│   │       └── variables.css
│   │
│   ├── components/              # Vue Components
│   │   ├── base/                # Basic UI Components (no business logic)
│   │   │   ├── BaseButton.vue
│   │   │   ├── BaseInput.vue
│   │   │   ├── BaseSelect.vue
│   │   │   ├── BaseModal.vue
│   │   │   ├── BaseTable.vue
│   │   │   ├── BaseCard.vue
│   │   │   ├── BaseBadge.vue
│   │   │   ├── BaseSpinner.vue
│   │   │   ├── BaseToast.vue
│   │   │   ├── BaseDropdown.vue
│   │   │   ├── BasePagination.vue
│   │   │   ├── BaseChart.vue
│   │   │   ├── BaseIcon.vue
│   │   │   └── index.ts         # Export all base components
│   │   │
│   │   └── modules/             # Feature-specific components (with business logic)
│   │       ├── device/
│   │       │   ├── DeviceList.vue
│   │       │   ├── DeviceCard.vue
│   │       │   ├── DeviceDetail.vue
│   │       │   ├── DeviceStatusBadge.vue
│   │       │   ├── DeviceMap.vue
│   │       │   ├── DeviceRegistrationForm.vue
│   │       │   ├── DeviceSettingsForm.vue
│   │       │   └── index.ts
│   │       │
│   │       ├── alert/
│   │       │   ├── AlertList.vue
│   │       │   ├── AlertCard.vue
│   │       │   ├── AlertDetail.vue
│   │       │   ├── AlertRuleForm.vue
│   │       │   ├── AlertTimeline.vue
│   │       │   └── index.ts
│   │       │
│   │       ├── dashboard/
│   │       │   ├── DashboardStats.vue
│   │       │   ├── DeviceStatusOverview.vue
│   │       │   ├── RecentAlerts.vue
│   │       │   ├── SensorDataChart.vue
│   │       │   ├── DeviceHealthWidget.vue
│   │       │   └── index.ts
│   │       │
│   │       ├── analytics/
│   │       │   ├── TimeSeriesChart.vue
│   │       │   ├── DataQueryBuilder.vue
│   │       │   ├── ReportGenerator.vue
│   │       │   ├── ExportDataForm.vue
│   │       │   └── index.ts
│   │       │
│   │       ├── firmware/
│   │       │   ├── FirmwareList.vue
│   │       │   ├── FirmwareUploadForm.vue
│   │       │   ├── DeploymentWizard.vue
│   │       │   ├── DeploymentProgress.vue
│   │       │   ├── DeploymentHistory.vue
│   │       │   └── index.ts
│   │       │
│   │       ├── user/
│   │       │   ├── UserProfile.vue
│   │       │   ├── UserPreferences.vue
│   │       │   ├── NotificationSettings.vue
│   │       │   ├── UserList.vue (admin)
│   │       │   ├── UserForm.vue (admin)
│   │       │   └── index.ts
│   │       │
│   │       ├── auth/
│   │       │   ├── LoginForm.vue
│   │       │   ├── RegisterForm.vue
│   │       │   ├── ForgotPasswordForm.vue
│   │       │   ├── ResetPasswordForm.vue
│   │       │   └── index.ts
│   │       │
│   │       └── layout/
│   │           ├── AppHeader.vue
│   │           ├── AppSidebar.vue
│   │           ├── AppFooter.vue
│   │           ├── AppNavigation.vue
│   │           ├── BreadcrumbsNav.vue
│   │           └── index.ts
│   │
│   ├── composables/             # Reusable logic (Vue Composition API)
│   │   ├── useDevices.ts        # Device-related logic
│   │   ├── useAlerts.ts         # Alert-related logic
│   │   ├── useUsers.ts          # User-related logic
│   │   ├── useFirmware.ts       # Firmware-related logic
│   │   ├── useAnalytics.ts      # Analytics-related logic
│   │   ├── useAuth.ts           # Authentication logic
│   │   ├── useWebSocket.ts      # WebSocket connection management
│   │   ├── useNotifications.ts  # Toast notifications
│   │   ├── usePagination.ts     # Pagination logic
│   │   ├── useDebounce.ts       # Debounce utility
│   │   ├── useLocalStorage.ts   # Local storage management
│   │   ├── useTheme.ts          # Theme management (dark/light mode)
│   │   └── index.ts             # Export all composables
│   │
│   ├── core/                    # Domain Definitions (Types, Interfaces, Constants)
│   │   ├── types/               # TypeScript types and interfaces
│   │   │   ├── device.ts
│   │   │   │   └── export interface Device {
│   │   │   │         deviceId: string;
│   │   │   │         organizationId: string;
│   │   │   │         deviceType: string;
│   │   │   │         name: string;
│   │   │   │         status: DeviceStatus;
│   │   │   │         location: DeviceLocation;
│   │   │   │         ...
│   │   │   │     }
│   │   │   │
│   │   │   ├── alert.ts
│   │   │   │   └── export interface Alert, AlertRule, AlertSeverity, etc.
│   │   │   │
│   │   │   ├── user.ts
│   │   │   │   └── export interface User, UserPreferences, UserRole, etc.
│   │   │   │
│   │   │   ├── firmware.ts
│   │   │   │   └── export interface Firmware, Deployment, etc.
│   │   │   │
│   │   │   ├── analytics.ts
│   │   │   │   └── export interface QueryParams, ChartData, etc.
│   │   │   │
│   │   │   ├── api.ts
│   │   │   │   └── export interface ApiResponse<T>, ApiError, PaginatedResponse<T>, etc.
│   │   │   │
│   │   │   └── index.ts
│   │   │
│   │   ├── enums/               # Enumerations
│   │   │   ├── device-status.enum.ts
│   │   │   ├── alert-severity.enum.ts
│   │   │   ├── user-role.enum.ts
│   │   │   ├── deployment-strategy.enum.ts
│   │   │   └── index.ts
│   │   │
│   │   ├── constants.ts         # Global constants
│   │   │   └── export const API_BASE_URL, WS_URL, PAGE_SIZE, etc.
│   │   │
│   │   └── index.ts
│   │
│   ├── api/                     # Backend Communication Layer (Infrastructure Adapter)
│   │   ├── client.ts            # HTTP client configuration (Axios)
│   │   │   └── - Axios instance with baseURL, interceptors
│   │   │       - Request interceptor: Add auth token
│   │   │       - Response interceptor: Handle errors globally
│   │   │
│   │   ├── modules/             # API Services by domain
│   │   │   ├── devices.api.ts
│   │   │   │   └── export const deviceApiService = {
│   │   │   │         getDevices(params): Promise<PaginatedResponse<Device>>
│   │   │   │         getDevice(deviceId): Promise<Device>
│   │   │   │         createDevice(data): Promise<Device>
│   │   │   │         updateDevice(deviceId, data): Promise<Device>
│   │   │   │         deleteDevice(deviceId): Promise<void>
│   │   │   │         getDeviceHistory(deviceId, params): Promise<SensorData[]>
│   │   │   │     }
│   │   │   │
│   │   │   ├── alerts.api.ts
│   │   │   │   └── alertApiService methods
│   │   │   │
│   │   │   ├── users.api.ts
│   │   │   │   └── userApiService methods
│   │   │   │
│   │   │   ├── firmware.api.ts
│   │   │   │   └── firmwareApiService methods
│   │   │   │
│   │   │   ├── analytics.api.ts
│   │   │   │   └── analyticsApiService methods
│   │   │   │
│   │   │   ├── auth.api.ts
│   │   │   │   └── authApiService methods (login, logout, refresh token)
│   │   │   │
│   │   │   └── index.ts
│   │   │
│   │   └── websocket.ts         # WebSocket client
│   │       └── - WebSocket connection management
│   │           - Subscribe/unsubscribe to device updates
│   │           - Handle incoming real-time messages
│   │
│   ├── store/                   # State Management (Pinia)
│   │   ├── auth.store.ts
│   │   │   └── export const useAuthStore = defineStore('auth', {
│   │   │         state: () => ({
│   │   │           user: null,
│   │   │           token: null,
│   │   │           isAuthenticated: false
│   │   │         }),
│   │   │         actions: {
│   │   │           login(), logout(), refreshToken(), checkAuth()
│   │   │         }
│   │   │     })
│   │   │
│   │   ├── device.store.ts      # Device state management
│   │   ├── alert.store.ts       # Alert state management
│   │   ├── settings.store.ts    # App settings (theme, language, etc.)
│   │   ├── notification.store.ts # Toast notifications
│   │   └── index.ts
│   │
│   ├── router/                  # Vue Router
│   │   ├── index.ts             # Router configuration
│   │   │   └── Routes definition, navigation guards
│   │   │
│   │   ├── routes/
│   │   │   ├── auth.routes.ts
│   │   │   ├── dashboard.routes.ts
│   │   │   ├── device.routes.ts
│   │   │   ├── alert.routes.ts
│   │   │   ├── analytics.routes.ts
│   │   │   ├── firmware.routes.ts
│   │   │   ├── user.routes.ts
│   │   │   └── index.ts
│   │   │
│   │   └── guards/              # Route guards
│   │       ├── auth.guard.ts
│   │       ├── role.guard.ts
│   │       └── index.ts
│   │
│   ├── pages/                   # Views (Route entry points)
│   │   ├── auth/
│   │   │   ├── LoginPage.vue
│   │   │   ├── RegisterPage.vue
│   │   │   ├── ForgotPasswordPage.vue
│   │   │   └── ResetPasswordPage.vue
│   │   │
│   │   ├── dashboard/
│   │   │   └── DashboardPage.vue
│   │   │
│   │   ├── devices/
│   │   │   ├── DevicesListPage.vue
│   │   │   ├── DeviceDetailPage.vue
│   │   │   └── DeviceRegistrationPage.vue
│   │   │
│   │   ├── alerts/
│   │   │   ├── AlertsListPage.vue
│   │   │   ├── AlertDetailPage.vue
│   │   │   └── AlertRulesPage.vue
│   │   │
│   │   ├── analytics/
│   │   │   ├── AnalyticsPage.vue
│   │   │   └── ReportsPage.vue
│   │   │
│   │   ├── firmware/
│   │   │   ├── FirmwareListPage.vue
│   │   │   ├── FirmwareUploadPage.vue
│   │   │   └── DeploymentsPage.vue
│   │   │
│   │   ├── users/
│   │   │   ├── ProfilePage.vue
│   │   │   ├── SettingsPage.vue
│   │   │   └── UsersManagementPage.vue (admin)
│   │   │
│   │   ├── NotFoundPage.vue
│   │   └── UnauthorizedPage.vue
│   │
│   ├── styles/                  # CSS Configuration
│   │   ├── tailwind.css         # Tailwind base, components, utilities
│   │   ├── variables.css        # CSS custom properties
│   │   └── global.css           # Global styles
│   │
│   ├── utils/                   # Utility functions
│   │   ├── date-formatter.ts
│   │   ├── number-formatter.ts
│   │   ├── validation.ts
│   │   ├── error-handler.ts
│   │   ├── logger.ts
│   │   └── index.ts
│   │
│   ├── plugins/                 # Vue plugins
│   │   ├── toast.plugin.ts
│   │   ├── chart.plugin.ts
│   │   └── index.ts
│   │
│   ├── directives/              # Custom Vue directives
│   │   ├── v-tooltip.ts
│   │   ├── v-click-outside.ts
│   │   └── index.ts
│   │
│   ├── App.vue                  # Root component
│   ├── main.ts                  # Application entry point
│   └── vite-env.d.ts            # Vite environment types
│
├── tests/                       # Frontend tests
│   ├── unit/
│   │   ├── components/
│   │   ├── composables/
│   │   └── store/
│   │
│   ├── integration/
│   │   └── api/
│   │
│   └── e2e/
│       └── specs/
│
├── .env.development             # Development environment variables
├── .env.staging                 # Staging environment variables
├── .env.production              # Production environment variables
├── .eslintrc.js                 # ESLint configuration
├── .prettierrc                  # Prettier configuration
├── tailwind.config.js           # Tailwind CSS configuration
├── postcss.config.js            # PostCSS configuration
├── tsconfig.json                # TypeScript configuration
├── vite.config.ts               # Vite configuration
├── package.json                 # NPM dependencies and scripts
└── README.md                    # Frontend documentation
```

## 4. Infrastructure Structure (Serverless Framework + IaC)

```
infrastructure/
├── serverless.yml               # Main Serverless Framework configuration
│
├── resources/                   # CloudFormation resources
│   ├── iot/
│   │   ├── iot-core.yml         # IoT Core resources (Thing Types, Policies, Rules)
│   │   ├── iot-jobs.yml         # IoT Jobs configuration
│   │   └── iot-analytics.yml    # IoT Analytics pipelines
│   │
│   ├── storage/
│   │   ├── dynamodb.yml         # DynamoDB tables
│   │   ├── timestream.yml       # Timestream database and tables
│   │   └── s3.yml               # S3 buckets
│   │
│   ├── api/
│   │   ├── api-gateway.yml      # API Gateway configuration
│   │   ├── websocket-api.yml    # WebSocket API configuration
│   │   └── cognito.yml          # Cognito User Pool
│   │
│   ├── streaming/
│   │   ├── kinesis.yml          # Kinesis Data Streams
│   │   └── sqs.yml              # SQS queues
│   │
│   ├── monitoring/
│   │   ├── cloudwatch.yml       # CloudWatch alarms and dashboards
│   │   └── xray.yml             # X-Ray configuration
│   │
│   ├── security/
│   │   ├── kms.yml              # KMS keys
│   │   ├── secrets.yml          # Secrets Manager
│   │   └── iam-roles.yml        # IAM roles and policies
│   │
│   └── frontend/
│       ├── cloudfront.yml       # CloudFront distribution
│       └── s3-hosting.yml       # S3 static website hosting
│
├── functions/                   # Lambda function configurations
│   ├── api/
│   │   ├── device-functions.yml
│   │   ├── alert-functions.yml
│   │   ├── user-functions.yml
│   │   ├── firmware-functions.yml
│   │   └── analytics-functions.yml
│   │
│   ├── stream/
│   │   ├── kinesis-functions.yml
│   │   ├── sqs-functions.yml
│   │   └── iot-rule-functions.yml
│   │
│   ├── scheduled/
│   │   └── cron-functions.yml
│   │
│   └── websocket/
│       └── websocket-functions.yml
│
├── layers/                      # Lambda Layers configuration
│   ├── common-layer.yml
│   └── firebase-layer.yml
│
├── plugins/                     # Serverless plugins
│   └── custom-plugins/
│
├── scripts/                     # Deployment and utility scripts
│   ├── deploy-all.sh
│   ├── deploy-backend.sh
│   ├── deploy-frontend.sh
│   ├── seed-data.sh
│   ├── create-iot-certificates.sh
│   └── cleanup.sh
│
├── environments/                # Environment-specific configurations
│   ├── dev.yml
│   ├── staging.yml
│   └── prod.yml
│
└── README.md                    # Infrastructure documentation
```

## 5. Documentation Structure

```
docs/
├── 01-REQUIREMENTS-SPECIFICATION.md
├── 02-ARCHITECTURE-DESIGN.md
├── 03-FOLDER-STRUCTURE.md
├── 04-FRONTEND-DESIGN.md
├── 05-BACKEND-SERVICES-DESIGN.md
├── 06-NOTIFICATION-SYSTEM-DESIGN.md
├── 07-API-SPECIFICATION.md (OpenAPI/Swagger)
├── 08-DATABASE-SCHEMA.md
├── 09-DEPLOYMENT-GUIDE.md
├── 10-SECURITY-GUIDE.md
├── 11-MONITORING-GUIDE.md
├── 12-TESTING-STRATEGY.md
├── diagrams/
│   ├── architecture-overview.png
│   ├── data-flow.png
│   ├── deployment.png
│   └── entity-relationship.png
└── README.md
```

## 6. Scripts Directory

```
scripts/
├── deployment/
│   ├── deploy-dev.sh
│   ├── deploy-staging.sh
│   ├── deploy-prod.sh
│   ├── rollback.sh
│   └── ci-cd-pipeline.yml (GitHub Actions / GitLab CI)
│
├── data/
│   ├── seed-devices.py
│   ├── seed-users.py
│   ├── migrate-data.py
│   └── export-data.py
│
├── iot/
│   ├── create-thing.sh
│   ├── generate-certificates.sh
│   ├── activate-device.sh
│   └── bulk-provision.py
│
├── maintenance/
│   ├── cleanup-old-data.py
│   ├── archive-logs.sh
│   ├── rotate-secrets.sh
│   └── health-check.py
│
└── development/
    ├── setup-local-env.sh
    ├── start-local-api.sh
    ├── start-frontend-dev.sh
    └── run-tests.sh
```

## 7. CI/CD Structure

```
.github/
└── workflows/
    ├── backend-ci.yml           # Backend CI pipeline
    ├── backend-cd.yml           # Backend CD pipeline
    ├── frontend-ci.yml          # Frontend CI pipeline
    ├── frontend-cd.yml          # Frontend CD pipeline
    ├── integration-tests.yml    # Integration tests
    ├── security-scan.yml        # Security scanning
    └── dependency-update.yml    # Automated dependency updates
```

## 8. Configuration Files (Root Level)

```
Smart_IOT/
├── .gitignore
├── .editorconfig
├── .nvmrc                       # Node version
├── .python-version              # Python version
├── Makefile                     # Common commands
├── docker-compose.yml           # Local development (DynamoDB Local, etc.)
├── package.json                 # Root package.json (Lerna/monorepo)
├── lerna.json                   # Lerna configuration (if using)
├── README.md
└── LICENSE
```

## 9. Key Benefits of This Structure

### Backend (Hexagonal Architecture)

1. **Clear Separation of Concerns**: Business logic (domain) is isolated from infrastructure
2. **Testability**: Easy to test domain logic without dependencies on AWS services
3. **Flexibility**: Easy to swap implementations (e.g., DynamoDB → PostgreSQL)
4. **Scalability**: Services can be deployed independently
5. **Maintainability**: Changes in one layer don't affect others

### Frontend (Feature-Based Structure)

1. **Modular**: Features are self-contained
2. **Reusability**: Base components are reusable across features
3. **Type Safety**: TypeScript provides strong typing
4. **Clear Data Flow**: API → Composable → Component
5. **Easy Navigation**: Intuitive folder structure

### Infrastructure (Serverless Framework)

1. **Infrastructure as Code**: Version-controlled infrastructure
2. **Reproducibility**: Consistent deployments across environments
3. **Modularity**: Resources organized by domain
4. **Environment Management**: Separate configs for dev/staging/prod

---

**Document Version:** 1.0
**Last Updated:** 2025-11-15
**Document Owner:** Solution Architecture Team

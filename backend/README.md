# IoT Monitoring Backend

Serverless backend application for IoT device monitoring built with Python 3.11, AWS Lambda, and Serverless Framework, following Hexagonal Architecture principles.

## Architecture

This backend implements **Hexagonal Architecture** (Ports and Adapters) for:
- **Testability**: Core business logic isolated from infrastructure
- **Maintainability**: Clean separation of concerns
- **Flexibility**: Easy to swap implementations (e.g., databases, external services)

### Layer Structure

```
backend/
├── src/
│   ├── domain/              # Core business logic (technology-agnostic)
│   │   ├── entities/        # Domain entities (Device, Alert, User, etc.)
│   │   ├── value_objects/   # Immutable value objects
│   │   ├── services/        # Business logic services
│   │   └── ports/          # Interfaces for repositories and external services
│   │
│   ├── infrastructure/      # Infrastructure implementations
│   │   ├── repositories/    # DynamoDB, Timestream implementations
│   │   ├── external/        # SES, FCM, SNS, IoT Core adapters
│   │   └── messaging/       # SQS, Kinesis clients
│   │
│   ├── functions/          # Lambda handlers (API Adapters)
│   │   ├── device/         # Device management APIs
│   │   ├── alert/          # Alert management APIs
│   │   ├── user/           # User management APIs
│   │   ├── firmware/       # Firmware management APIs
│   │   ├── analytics/      # Analytics APIs
│   │   ├── stream_processing/  # Event-driven functions
│   │   └── websocket/      # WebSocket handlers
│   │
│   └── shared/             # Shared utilities
│       ├── config/         # Configuration
│       ├── middleware/     # Logging, error handling
│       ├── exceptions/     # Custom exceptions
│       └── schemas/        # Pydantic validation schemas
│
└── tests/
    ├── unit/               # Unit tests for domain logic
    ├── integration/        # Integration tests with AWS services
    └── e2e/               # End-to-end tests
```

## Technology Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **Python** | Programming language | 3.11+ |
| **Poetry** | Dependency management | 2.0+ |
| **Serverless Framework** | Infrastructure as Code | 3.x+ |
| **AWS Lambda** | Serverless compute | - |
| **boto3** | AWS SDK for Python | Latest |
| **Pydantic** | Data validation | 2.x+ |
| **pytest** | Testing framework | Latest |
| **mypy** | Static type checking | Latest |

## AWS Services Used

- **AWS Lambda**: Serverless compute (50+ functions)
- **Amazon DynamoDB**: NoSQL database for devices, users, alerts, etc.
- **Amazon Timestream**: Time-series database for sensor data
- **Amazon Kinesis**: Real-time data streaming
- **Amazon SQS**: Message queuing for alerts
- **AWS IoT Core**: Device connectivity and management
- **Amazon S3**: Firmware storage and data exports
- **Amazon SES**: Email notifications
- **Amazon SNS**: SMS notifications
- **API Gateway**: REST API and WebSocket API
- **Amazon Cognito**: User authentication
- **AWS X-Ray**: Distributed tracing
- **CloudWatch**: Logging and monitoring

## Setup

### Prerequisites

- Python 3.11+
- Poetry 2.0+ (for dependency management)
- Node.js 18+ (for Serverless Framework)
- AWS CLI configured with appropriate credentials
- Docker (for packaging Python dependencies)

### Installation

1. **Install Node.js dependencies** (Serverless Framework):
   ```bash
   npm install
   ```

2. **Install Python dependencies with Poetry**:
   ```bash
   poetry install
   ```

   This will:
   - Create a virtual environment automatically
   - Install all production dependencies
   - Install all dev dependencies (pytest, black, mypy, etc.)
   - Generate a `poetry.lock` file for reproducible builds

## Development

### Local Testing

Run unit tests:
```bash
poetry run pytest tests/unit/
```

Run all tests with coverage:
```bash
poetry run pytest tests/ --cov=src --cov-report=html
```

Or use npm scripts:
```bash
npm run test
```

### Type Checking

```bash
poetry run mypy src/
# or
npm run type-check
```

### Code Formatting

```bash
poetry run black src/ tests/
# or
npm run format
```

### Linting

```bash
poetry run flake8 src/ tests/
poetry run pylint src/
# or
npm run lint
```

### Managing Dependencies

Add a production dependency:
```bash
poetry add package-name
```

Add a development dependency:
```bash
poetry add --group dev package-name
```

Update dependencies:
```bash
poetry update
```

Show installed packages:
```bash
poetry show
```

## Deployment

### Deploy to Development

```bash
serverless deploy --stage dev
```

### Deploy to Staging

```bash
serverless deploy --stage staging
```

### Deploy to Production

```bash
serverless deploy --stage prod
```

### Deploy Single Function

```bash
serverless deploy function -f registerDevice --stage dev
```

### View Logs

```bash
serverless logs -f registerDevice --stage dev --tail
```

## API Endpoints

### Device Management

- `POST /devices` - Register new device
- `GET /devices` - List devices
- `GET /devices/{deviceId}` - Get device details
- `PUT /devices/{deviceId}` - Update device
- `DELETE /devices/{deviceId}` - Delete device
- `GET /devices/{deviceId}/history` - Get sensor data history

### Alert Management

- `GET /alerts` - List alerts
- `GET /alerts/{alertId}` - Get alert details
- `POST /alerts/{alertId}/acknowledge` - Acknowledge alert
- `POST /alerts/{alertId}/resolve` - Resolve alert
- `GET /alert-rules` - List alert rules
- `POST /alert-rules` - Create alert rule
- `PUT /alert-rules/{ruleId}` - Update alert rule
- `DELETE /alert-rules/{ruleId}` - Delete alert rule

### User Management

- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update user profile
- `PUT /users/me/preferences` - Update notification preferences
- `POST /users/me/device-tokens` - Register device token for push notifications

### Firmware Management

- `POST /firmware/upload` - Upload firmware
- `GET /firmware` - List firmware versions
- `GET /firmware/{firmwareId}` - Get firmware details
- `POST /firmware/deployments` - Create deployment
- `GET /firmware/deployments/{deploymentId}` - Get deployment status

### Analytics

- `GET /analytics/dashboard` - Get dashboard statistics
- `POST /analytics/query` - Query sensor data
- `POST /analytics/reports` - Generate report
- `POST /analytics/export` - Export data

## Environment Variables

Key environment variables (automatically set by serverless.yml):

- `ENVIRONMENT`: Deployment stage (dev/staging/prod)
- `AWS_REGION`: AWS region
- `DEVICES_TABLE`: DynamoDB devices table name
- `USERS_TABLE`: DynamoDB users table name
- `ALERTS_TABLE`: DynamoDB alerts table name
- `TIMESTREAM_DATABASE`: Timestream database name
- `FIRMWARE_BUCKET`: S3 bucket for firmware storage
- `LOG_LEVEL`: Logging level (INFO/DEBUG/ERROR)

## Monitoring

### CloudWatch Dashboards

View application metrics:
```bash
serverless metrics --function registerDevice --stage dev
```

### X-Ray Tracing

X-Ray is automatically enabled for:
- All Lambda functions
- API Gateway
- DynamoDB calls
- HTTP requests

View traces in AWS X-Ray console.

### Alarms

CloudWatch alarms are configured for:
- Lambda errors
- API Gateway 5xx errors
- DynamoDB throttling
- SQS dead-letter queue depth

## Testing Strategy

### Unit Tests
- Test domain entities and business logic
- Mock all external dependencies
- Fast execution (<1s per test)

### Integration Tests
- Test Lambda functions with real AWS services
- Use LocalStack or AWS test resources
- Slower execution (2-5s per test)

### E2E Tests
- Test complete workflows (device registration → data ingestion → alerts)
- Run against dedicated test environment
- Slowest execution (10-30s per test)

## Security

### IAM Permissions
- Least privilege principle
- Separate roles per function
- No hardcoded credentials

### Data Encryption
- Encryption at rest for DynamoDB (AWS-managed keys)
- Encryption at rest for S3 (SSE-KMS)
- TLS 1.2+ for all communications

### Authentication
- Amazon Cognito for user authentication
- JWT tokens for API authorization
- X.509 certificates for IoT devices

## Troubleshooting

### Common Issues

**Issue**: Lambda cold starts are slow
**Solution**: Use provisioned concurrency for critical functions

**Issue**: DynamoDB throttling
**Solution**: Switch to on-demand billing or increase provisioned capacity

**Issue**: Kinesis consumer lag
**Solution**: Increase shard count or batch size

**Issue**: SQS messages going to DLQ
**Solution**: Check CloudWatch logs for error details

## Contributing

1. Create feature branch from `main`
2. Write tests for new functionality
3. Ensure all tests pass
4. Run linting and type checking
5. Submit pull request

## License

Proprietary - All rights reserved

## Support

For issues and questions:
- Create GitHub issue
- Contact: support@example.com

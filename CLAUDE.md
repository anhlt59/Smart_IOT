# CLAUDE.md - Smart IOT Monitoring Platform

**AI Assistant Guide for Smart_IOT Repository**

This document provides comprehensive guidance for AI assistants (like Claude) working on the Smart_IOT codebase. It explains the architecture, development workflows, code conventions, and common tasks to ensure consistent and high-quality contributions.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Quick Start](#quick-start)
3. [Architecture Overview](#architecture-overview)
4. [Repository Structure](#repository-structure)
5. [Development Workflow](#development-workflow)
6. [Common Tasks](#common-tasks)
7. [Code Conventions](#code-conventions)
8. [Testing Strategy](#testing-strategy)
9. [Deployment](#deployment)
10. [Troubleshooting](#troubleshooting)
11. [Key Constraints](#key-constraints)
12. [Additional Resources](#additional-resources)

---

## Project Overview

### What is Smart_IOT?

Smart_IOT is a **production-ready, full-stack IoT monitoring platform** that provides:
- Real-time device monitoring and sensor data collection
- Alert management with multi-channel notifications (Email, Push, SMS)
- Firmware over-the-air (FOTA) updates
- Analytics and historical data visualization
- Multi-user management with role-based access control

### Technology Stack

**Backend:**
- Python 3.11 on AWS Lambda (Serverless)
- Poetry for dependency management
- Serverless Framework for IaC
- 15+ AWS Services (DynamoDB, Timestream, Kinesis, IoT Core, etc.)
- Hexagonal Architecture pattern

**Frontend:**
- Vue 3 with TypeScript
- Vite for build tooling
- Tailwind CSS for styling
- Pinia for state management
- Axios for HTTP communication

### Current Status

**✅ Implemented:**
- Serverless infrastructure with local development support
- REST API with mock data
- Vue.js dashboard with real API integration
- Hexagonal architecture for backend
- CORS-enabled API
- Error handling and loading states

**❌ Not Yet Implemented:**
- Real DynamoDB/Timestream integration (currently using mock data)
- AWS Cognito authentication (mock login exists)
- WebSocket real-time updates
- Actual notification sending (FCM/SES configured but not integrated)
- Frontend testing suite
- CI/CD pipeline

---

## Quick Start

### Prerequisites

- **Node.js** 18+ (for both frontend and backend Serverless tooling)
- **Python** 3.11+ (for Lambda functions)
- **Poetry** 2.0+ (for Python dependency management)
- **npm** or yarn

### Installation

```bash
# Clone and navigate to repository
cd Smart_IOT

# Backend setup
cd backend
npm install                          # Serverless dependencies
poetry install                       # Install Python dependencies with Poetry

# Frontend setup
cd ../frontend
npm install

# Return to root and start both services
cd ..
./start-dev.sh
```

### Access Points

- **Backend API:** http://localhost:3000
- **Frontend UI:** http://localhost:5173
- **API Documentation:** See `docs/05-BACKEND-SERVICES-DESIGN.md`

---

## Architecture Overview

### System Architecture

Smart_IOT follows a **microservices-based serverless architecture** with clear separation of concerns:

```
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│ IoT Devices │─────▶│ AWS IoT Core │─────▶│ Kinesis Stream  │
└─────────────┘      └──────────────┘      └────────┬────────┘
                                                      │
                                                      ▼
┌─────────────┐      ┌──────────────┐      ┌─────────────────┐
│  Frontend   │◀────▶│ API Gateway  │◀────▶│ Lambda Functions│
│  (Vue 3)    │      │   (REST)     │      │   (Python)      │
└─────────────┘      └──────────────┘      └────────┬────────┘
                                                      │
                     ┌────────────────────────────────┼────────┐
                     │                                │        │
                     ▼                                ▼        ▼
              ┌─────────────┐                  ┌──────────┐ ┌─────────┐
              │  DynamoDB   │                  │Timestream│ │   SQS   │
              │ (Metadata)  │                  │(Sensors) │ │(Alerts) │
              └─────────────┘                  └──────────┘ └─────────┘
```

### Backend: Hexagonal Architecture

The backend implements **Hexagonal Architecture (Ports & Adapters)** for maintainability and testability:

```
┌─────────────────────────────────────────────────────────┐
│                     Application Layer                    │
│              (Lambda Handlers / Use Cases)               │
└───────────────────────┬─────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
┌──────────────┐ ┌──────────┐ ┌──────────────────┐
│   Domain     │ │  Ports   │ │  Infrastructure  │
│   Entities   │ │(Abstract)│ │    (Adapters)    │
│   Services   │ │Interfaces│ │  DynamoDB, SES   │
└──────────────┘ └──────────┘ └──────────────────┘
```

**Dependency Rule:** Dependencies always point **inward** (Infrastructure → Domain, never Domain → Infrastructure).

**Key Benefits:**
- Business logic is independent of AWS services
- Easy to test (mock adapters)
- Can swap implementations (e.g., DynamoDB → PostgreSQL)

### Frontend: Layered Component Architecture

```
┌──────────────┐
│    Pages     │ ← Route-level components
└──────┬───────┘
       │
┌──────▼───────┐
│  Components  │ ← Reusable UI (base + modules)
└──────┬───────┘
       │
┌──────▼───────┐
│ Composables  │ ← Business logic hooks (useDevices, useAlerts)
└──────┬───────┘
       │
┌──────▼───────┐
│ API Services │ ← HTTP client layer (deviceApi, alertApi)
└──────┬───────┘
       │
┌──────▼───────┐
│  API Client  │ ← Axios with interceptors
└──────────────┘
```

**Data Flow:** API → Composable → Component → Page

---

## Repository Structure

```
Smart_IOT/
├── backend/                        # Serverless Python backend
│   ├── src/
│   │   ├── domain/                # Core business logic (HEXAGON CORE)
│   │   │   ├── entities/          # Device, Alert, User, Firmware
│   │   │   ├── value_objects/     # DeviceLocation, AlertSeverity, etc.
│   │   │   ├── services/          # Domain services (business rules)
│   │   │   └── ports/             # Repository interfaces (contracts)
│   │   │
│   │   ├── infrastructure/        # AWS service implementations (ADAPTERS)
│   │   │   ├── repositories/      # DynamoDB, Timestream implementations
│   │   │   ├── messaging/         # SQS, Kinesis clients
│   │   │   └── external_services/ # SES, FCM, S3 adapters
│   │   │
│   │   ├── functions/             # Lambda handlers (APPLICATION LAYER)
│   │   │   ├── device/            # Device CRUD operations
│   │   │   ├── alert/             # Alert management
│   │   │   ├── user/              # User management
│   │   │   ├── firmware/          # Firmware updates
│   │   │   ├── analytics/         # Data analytics
│   │   │   ├── stream_processing/ # Event-driven processors
│   │   │   └── websocket/         # Real-time connections
│   │   │
│   │   └── shared/                # Cross-cutting concerns
│   │       ├── config/            # Environment configuration
│   │       ├── middleware/        # Logging, error handling
│   │       ├── utils/             # Response helpers
│   │       └── exceptions/        # Custom exceptions
│   │
│   ├── tests/                     # Test suites
│   │   ├── unit/                  # Unit tests
│   │   ├── integration/           # Integration tests
│   │   └── e2e/                   # End-to-end tests
│   │
│   ├── serverless.yml             # Infrastructure as Code
│   ├── requirements.txt           # Python dependencies
│   ├── package.json               # Serverless CLI dependencies
│   └── CLAUDE.md                  # Backend-specific AI guide
│
├── frontend/                       # Vue 3 TypeScript frontend
│   ├── src/
│   │   ├── core/                  # TypeScript types and constants
│   │   │   ├── types/             # Device, Alert, User interfaces
│   │   │   ├── enums/             # DeviceStatus, AlertSeverity, etc.
│   │   │   └── constants/         # API URLs, pagination defaults
│   │   │
│   │   ├── api/                   # HTTP communication layer
│   │   │   ├── client.ts          # Axios instance with interceptors
│   │   │   └── modules/           # deviceApi, alertApi, userApi
│   │   │
│   │   ├── composables/           # Vue composables (business logic)
│   │   │   ├── useDevices.ts      # Device management logic
│   │   │   ├── useAlerts.ts       # Alert management logic
│   │   │   └── useAuth.ts         # Authentication logic
│   │   │
│   │   ├── components/            # Vue components
│   │   │   ├── base/              # Dumb components (Button, Input, Card)
│   │   │   └── modules/           # Smart components (DeviceList, AlertCard)
│   │   │
│   │   ├── pages/                 # Route-level components
│   │   │   ├── Dashboard.vue      # Main dashboard
│   │   │   ├── DeviceList.vue     # Device management
│   │   │   └── AlertList.vue      # Alert management
│   │   │
│   │   ├── store/                 # Pinia state management
│   │   │   ├── auth.ts            # Auth store
│   │   │   └── settings.ts        # App settings store
│   │   │
│   │   ├── router/                # Vue Router configuration
│   │   ├── styles/                # Global styles and Tailwind config
│   │   └── assets/                # Static assets
│   │
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── CLAUDE.md                  # Frontend-specific AI guide
│
├── docs/                           # Comprehensive documentation
│   ├── 01-REQUIREMENTS-SPECIFICATION.md
│   ├── 02-ARCHITECTURE-DESIGN.md   # **MUST READ** for understanding
│   ├── 03-FOLDER-STRUCTURE.md
│   ├── 04-FRONTEND-DESIGN.md
│   ├── 05-BACKEND-SERVICES-DESIGN.md
│   └── 06-NOTIFICATION-SYSTEM-DESIGN.md
│
├── README.md                       # Quick start guide
├── task.md                         # Original project requirements
├── start-dev.sh                    # Development startup script
└── CLAUDE.md                       # This file
```

---

## Development Workflow

### 1. Starting Local Development

**Option A: Use convenience script (recommended)**
```bash
./start-dev.sh
```

**Option B: Manual start**
```bash
# Terminal 1 - Backend
cd backend
source venv/bin/activate
npm run dev                          # Starts on port 3000

# Terminal 2 - Frontend
cd frontend
npm run dev                          # Starts on port 5173
```

### 2. Making Changes

**Always follow this workflow:**
1. Create a feature branch: `git checkout -b feature/your-feature-name`
2. Make changes following code conventions (see below)
3. Test locally (manual or automated)
4. Commit with clear messages
5. Push and create pull request

### 3. Git Workflow

**Branch Naming:**
- Features: `feature/add-device-filtering`
- Bugs: `fix/alert-not-showing`
- Refactoring: `refactor/extract-alert-logic`
- Docs: `docs/update-readme`

**Commit Messages:**
```bash
# Good examples
git commit -m "Add device filtering by status"
git commit -m "Fix alert acknowledgment not persisting"
git commit -m "Refactor device repository to use query builder"

# Bad examples
git commit -m "Updates"
git commit -m "Fix bug"
git commit -m "Changes"
```

### 4. Environment Configuration

**Backend:**
Environment variables are auto-configured in `serverless.yml` for local development:
- `ENVIRONMENT=dev`
- `AWS_REGION=us-east-1`
- `DEVICES_TABLE`, `ALERTS_TABLE`, etc.

**Frontend:**
Create environment files:

`.env.development`:
```bash
VITE_API_BASE_URL=http://localhost:3000
VITE_WS_URL=ws://localhost:3001
VITE_ENVIRONMENT=development
```

`.env.production`:
```bash
VITE_API_BASE_URL=https://api.yourapp.com
VITE_WS_URL=wss://ws.yourapp.com
VITE_ENVIRONMENT=production
```

---

## Common Tasks

### Task 1: Add a New Lambda Function

**Example: Add a "Get Device Statistics" endpoint**

1. **Create domain logic** (if needed):
```python
# backend/src/domain/services/device_statistics_service.py
from typing import Dict
from ..ports.device_repository import DeviceRepository

class DeviceStatisticsService:
    def __init__(self, device_repo: DeviceRepository):
        self.device_repo = device_repo

    def get_statistics(self) -> Dict:
        # Business logic here
        devices = self.device_repo.list_all()
        return {
            'total': len(devices),
            'online': len([d for d in devices if d.status == 'online']),
            'offline': len([d for d in devices if d.status == 'offline'])
        }
```

2. **Create Lambda handler**:
```python
# backend/src/functions/device/get_statistics.py
from ...domain.services.device_statistics_service import DeviceStatisticsService
from ...infrastructure.repositories.device_repository_impl import DeviceRepositoryImpl
from ...shared.utils.response import success_response, error_response
from ...shared.middleware.logger import logger

def lambda_handler(event, context):
    """Get device statistics"""
    try:
        logger.info("Getting device statistics")

        # Dependency injection
        device_repo = DeviceRepositoryImpl()
        service = DeviceStatisticsService(device_repo)

        # Execute business logic
        statistics = service.get_statistics()

        return success_response(statistics)
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return error_response(
            'STATISTICS_ERROR',
            'Failed to retrieve statistics',
            status_code=500
        )
```

3. **Add to serverless.yml**:
```yaml
functions:
  getDeviceStatistics:
    handler: src/functions/device/get_statistics.lambda_handler
    events:
      - http:
          path: devices/statistics
          method: get
          cors: true
```

4. **Test locally**:
```bash
curl http://localhost:3000/devices/statistics | jq
```

### Task 2: Add a New Frontend Page

**Example: Add a "Device Details" page**

1. **Define types**:
```typescript
// frontend/src/core/types/device.ts
export interface DeviceDetails extends Device {
  recentReadings: SensorReading[];
  alertHistory: Alert[];
  firmwareHistory: FirmwareVersion[];
}
```

2. **Create API service**:
```typescript
// frontend/src/api/modules/deviceApi.ts
export const deviceApi = {
  // ... existing methods

  async getDeviceDetails(deviceId: string): Promise<DeviceDetails> {
    const response = await apiClient.get<DeviceDetails>(`/devices/${deviceId}/details`);
    return response.data;
  }
};
```

3. **Create composable**:
```typescript
// frontend/src/composables/useDeviceDetails.ts
import { ref, onMounted } from 'vue';
import { deviceApi } from '@/api/modules/deviceApi';
import type { DeviceDetails } from '@/core/types/device';

export function useDeviceDetails(deviceId: string) {
  const device = ref<DeviceDetails | null>(null);
  const isLoading = ref(true);
  const error = ref<string | null>(null);

  const fetchDevice = async () => {
    isLoading.value = true;
    error.value = null;
    try {
      device.value = await deviceApi.getDeviceDetails(deviceId);
    } catch (err) {
      error.value = 'Failed to load device details';
      console.error(err);
    } finally {
      isLoading.value = false;
    }
  };

  onMounted(fetchDevice);

  return { device, isLoading, error, refetch: fetchDevice };
}
```

4. **Create page component**:
```vue
<!-- frontend/src/pages/DeviceDetails.vue -->
<template>
  <div class="container mx-auto p-4">
    <div v-if="isLoading">Loading...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else-if="device">
      <h1 class="text-2xl font-bold">{{ device.name }}</h1>
      <p>Status: {{ device.status }}</p>
      <!-- More device details -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
import { useDeviceDetails } from '@/composables/useDeviceDetails';

const route = useRoute();
const deviceId = route.params.id as string;
const { device, isLoading, error } = useDeviceDetails(deviceId);
</script>
```

5. **Add route**:
```typescript
// frontend/src/router/index.ts
{
  path: '/devices/:id',
  name: 'DeviceDetails',
  component: () => import('@/pages/DeviceDetails.vue')
}
```

### Task 3: Add Real Database Integration

**Example: Replace mock device repository with DynamoDB**

1. **Update infrastructure implementation**:
```python
# backend/src/infrastructure/repositories/device_repository_impl.py
import boto3
from typing import List, Optional
from ...domain.ports.device_repository import DeviceRepository
from ...domain.entities.device import Device
from ...shared.config.environment import get_env

class DeviceRepositoryImpl(DeviceRepository):
    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')
        self.table = self.dynamodb.Table(get_env('DEVICES_TABLE'))

    def find_by_id(self, device_id: str) -> Optional[Device]:
        response = self.table.get_item(Key={'device_id': device_id})
        item = response.get('Item')
        return Device.from_dict(item) if item else None

    def list_all(self) -> List[Device]:
        response = self.table.scan()
        return [Device.from_dict(item) for item in response.get('Items', [])]

    # ... implement other methods
```

2. **Ensure Lambda has permissions** (already configured in serverless.yml):
```yaml
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
          Resource:
            - !GetAtt DevicesTable.Arn
```

3. **Test with local DynamoDB** (optional):
```bash
# Install DynamoDB local
npm install -g dynamodb-local

# Start DynamoDB local
dynamodb-local

# Update endpoint in code for local testing
dynamodb = boto3.resource('dynamodb', endpoint_url='http://localhost:8000')
```

### Task 4: Add Frontend Tests

**Example: Test useDevices composable**

1. **Install testing dependencies**:
```bash
cd frontend
npm install -D vitest @vue/test-utils happy-dom
```

2. **Configure Vitest**:
```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,
    environment: 'happy-dom'
  }
});
```

3. **Write test**:
```typescript
// frontend/src/composables/__tests__/useDevices.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { useDevices } from '../useDevices';
import { deviceApi } from '@/api/modules/deviceApi';

vi.mock('@/api/modules/deviceApi');

describe('useDevices', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches devices on mount', async () => {
    const mockDevices = [
      { id: '1', name: 'Device 1', status: 'online' }
    ];
    vi.mocked(deviceApi.listDevices).mockResolvedValue(mockDevices);

    const { devices, isLoading } = useDevices();

    expect(isLoading.value).toBe(true);
    await new Promise(resolve => setTimeout(resolve, 0));
    expect(devices.value).toEqual(mockDevices);
    expect(isLoading.value).toBe(false);
  });
});
```

4. **Add test script**:
```json
// package.json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

---

## Code Conventions

### Backend (Python)

**Naming Conventions:**
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions/Variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`

**Code Style:**
```python
# Use type hints
def get_device(device_id: str) -> Optional[Device]:
    pass

# Use dataclasses or Pydantic models
from pydantic import BaseModel

class DeviceSchema(BaseModel):
    device_id: str
    name: str
    status: str

# Use dependency injection (constructor injection)
class DeviceService:
    def __init__(self, device_repo: DeviceRepository):
        self.device_repo = device_repo

# Use proper logging
from ...shared.middleware.logger import logger

logger.info(f"Processing device {device_id}")
logger.error(f"Error occurred: {str(e)}", exc_info=True)

# Always return standardized responses
from ...shared.utils.response import success_response, error_response

return success_response(data, status_code=200)
return error_response('ERROR_CODE', 'Message', status_code=400)
```

**Error Handling:**
```python
from ...shared.exceptions.custom_exceptions import DeviceNotFoundException

try:
    device = device_repo.find_by_id(device_id)
    if not device:
        raise DeviceNotFoundException(f"Device {device_id} not found")
except DeviceNotFoundException as e:
    return error_response('DEVICE_NOT_FOUND', str(e), status_code=404)
except Exception as e:
    logger.error(f"Unexpected error: {str(e)}", exc_info=True)
    return error_response('INTERNAL_ERROR', 'An error occurred', status_code=500)
```

**Testing:**
```python
# Use pytest
import pytest
from unittest.mock import Mock, patch

def test_get_device_success():
    # Arrange
    mock_repo = Mock()
    mock_repo.find_by_id.return_value = Device(id='123', name='Test')
    service = DeviceService(mock_repo)

    # Act
    result = service.get_device('123')

    # Assert
    assert result.id == '123'
    mock_repo.find_by_id.assert_called_once_with('123')
```

### Frontend (TypeScript/Vue)

**Naming Conventions:**
- Files: `camelCase.ts` or `PascalCase.vue`
- Components: `PascalCase.vue`
- Variables/Functions: `camelCase`
- Constants: `UPPER_SNAKE_CASE`
- Types/Interfaces: `PascalCase`

**Code Style:**
```typescript
// Use TypeScript types
interface Device {
  id: string;
  name: string;
  status: DeviceStatus;
}

// Use composition API (not options API)
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';

const count = ref(0);
const doubled = computed(() => count.value * 2);

onMounted(() => {
  console.log('Component mounted');
});
</script>

// Use composables for reusable logic
export function useDevices() {
  const devices = ref<Device[]>([]);
  const isLoading = ref(false);

  const fetchDevices = async () => {
    isLoading.value = true;
    try {
      devices.value = await deviceApi.listDevices();
    } finally {
      isLoading.value = false;
    }
  };

  return { devices, isLoading, fetchDevices };
}

// Use proper error handling
try {
  await deviceApi.createDevice(deviceData);
  showSuccessMessage('Device created successfully');
} catch (error) {
  console.error('Failed to create device:', error);
  showErrorMessage('Failed to create device');
}
```

**Component Structure:**
```vue
<template>
  <!-- Use Tailwind classes -->
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">{{ title }}</h1>

    <!-- Use v-if/v-else for conditional rendering -->
    <div v-if="isLoading">Loading...</div>
    <div v-else-if="error">Error: {{ error }}</div>
    <ul v-else>
      <li v-for="item in items" :key="item.id">
        {{ item.name }}
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { Device } from '@/core/types/device';

// Props
interface Props {
  title: string;
  filter?: string;
}

const props = withDefaults(defineProps<Props>(), {
  filter: 'all'
});

// Emits
const emit = defineEmits<{
  itemSelected: [id: string];
}>();

// State
const items = ref<Device[]>([]);
const isLoading = ref(false);
const error = ref<string | null>(null);

// Methods
const selectItem = (id: string) => {
  emit('itemSelected', id);
};

// Lifecycle
onMounted(() => {
  // Fetch data
});
</script>

<style scoped>
/* Use scoped styles sparingly - prefer Tailwind */
</style>
```

---

## Testing Strategy

### Backend Testing

**Test Structure:**
```
tests/
├── unit/                    # Unit tests (domain, services)
│   ├── test_device_service.py
│   └── test_alert_service.py
├── integration/             # Integration tests (with AWS mocks)
│   ├── test_device_repository.py
│   └── test_alert_repository.py
└── e2e/                     # End-to-end tests
    └── test_device_api.py
```

**Run tests:**
```bash
cd backend
source venv/bin/activate

# Run all tests
npm run test

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_device_service.py

# Run with verbose output
pytest -v
```

**Testing AWS Services:**
```python
# Use moto for AWS mocking
import boto3
from moto import mock_dynamodb

@mock_dynamodb
def test_device_repository():
    # Create mock DynamoDB table
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    table = dynamodb.create_table(
        TableName='devices',
        KeySchema=[{'AttributeName': 'device_id', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'device_id', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )

    # Test repository
    repo = DeviceRepositoryImpl()
    device = Device(device_id='123', name='Test')
    repo.save(device)

    result = repo.find_by_id('123')
    assert result.device_id == '123'
```

### Frontend Testing (To Be Implemented)

**Recommended Setup:**
- Vitest for unit/integration tests
- Vue Test Utils for component testing
- Playwright or Cypress for E2E tests

**Coverage Goals:**
- Unit tests: 80%+
- Integration tests: Key user flows
- E2E tests: Critical paths

---

## Deployment

### Backend Deployment

**Deploy to AWS:**
```bash
cd backend
source venv/bin/activate

# Deploy to dev environment
npm run deploy:dev

# Deploy to production
npm run deploy:prod

# Deploy single function (faster)
npm run deploy:prod -- -f getDevice

# Remove infrastructure
npm run remove:prod
```

**What gets deployed:**
- Lambda functions with dependencies
- API Gateway endpoints
- DynamoDB tables
- Kinesis streams
- SQS queues
- S3 buckets
- IAM roles and policies
- CloudWatch log groups

**Environment Stages:**
- `dev` - Development (use for testing)
- `staging` - Staging (not configured yet)
- `prod` - Production (be careful!)

### Frontend Deployment

**Build for production:**
```bash
cd frontend
npm run build
# Output in dist/ directory
```

**Deploy to S3 + CloudFront:**
```bash
# Install AWS CLI
aws --version

# Create S3 bucket
aws s3 mb s3://your-app-frontend

# Build and sync
npm run build
aws s3 sync dist/ s3://your-app-frontend --delete

# Configure CloudFront for distribution
# (See docs/02-ARCHITECTURE-DESIGN.md for details)
```

**Environment Variables:**
Update `VITE_API_BASE_URL` to point to deployed API Gateway URL.

---

## Troubleshooting

### Common Issues

**1. Backend won't start**
```bash
# Symptom: serverless-offline fails to start
# Solution: Check Poetry environment and dependencies
cd backend
poetry install

# Check Node dependencies
npm install
```

**2. Frontend can't connect to backend**
```bash
# Symptom: CORS errors or network errors
# Solution: Verify backend is running
curl http://localhost:3000/devices

# Check VITE_API_BASE_URL
cat frontend/.env.development
# Should be: VITE_API_BASE_URL=http://localhost:3000
```

**3. TypeScript errors in frontend**
```bash
# Run type check
cd frontend
npm run type-check

# Common fix: Update types
npm install -D @types/node
```

**4. Lambda function timeout**
```yaml
# Increase timeout in serverless.yml
functions:
  myFunction:
    timeout: 60  # Increase from 30 to 60 seconds
```

**5. DynamoDB permission errors**
```yaml
# Ensure IAM permissions in serverless.yml
provider:
  iam:
    role:
      statements:
        - Effect: Allow
          Action:
            - dynamodb:Query
            - dynamodb:GetItem
          Resource: !GetAtt DevicesTable.Arn
```

### Debug Tips

**Backend:**
```python
# Add detailed logging
from ...shared.middleware.logger import logger

logger.info(f"Processing event: {event}")
logger.debug(f"Device data: {device.dict()}")
```

**Frontend:**
```typescript
// Use Vue DevTools browser extension
// Add console logs in composables
console.log('Fetching devices...');
console.log('Response:', response);

// Check network tab in browser DevTools (F12)
```

---

## Key Constraints

### What NOT to Do

**1. DO NOT modify hexagonal architecture boundaries**
- ❌ Don't import infrastructure code in domain layer
- ❌ Don't bypass ports/adapters
- ✅ Always use dependency injection

**2. DO NOT commit sensitive data**
- ❌ No AWS credentials in code
- ❌ No API keys in frontend
- ✅ Use AWS Secrets Manager or environment variables

**3. DO NOT break existing APIs without versioning**
- ❌ Changing response structure breaks frontend
- ✅ Version APIs: `/v1/devices`, `/v2/devices`

**4. DO NOT use options API in Vue**
- ❌ Options API is deprecated in this project
- ✅ Always use composition API with `<script setup>`

**5. DO NOT skip error handling**
- ❌ Unhandled exceptions crash Lambda
- ✅ Always use try-catch and return proper error responses

**6. DO NOT deploy to production without testing**
- ❌ `npm run deploy:prod` without testing
- ✅ Test in dev first, then staging, then prod

### Security Considerations

**Authentication:**
- All API endpoints should require Cognito authentication (not implemented yet)
- Use JWT tokens for authorization
- Implement role-based access control

**Data Validation:**
- Always validate input data in Lambda functions
- Use Pydantic models for type safety
- Sanitize user inputs

**Secrets Management:**
- Store secrets in AWS Secrets Manager
- Never log sensitive data
- Use environment variables for configuration

---

## Additional Resources

### Documentation

**Must-read documents:**
1. `docs/02-ARCHITECTURE-DESIGN.md` - Complete architecture overview
2. `docs/05-BACKEND-SERVICES-DESIGN.md` - API specifications
3. `backend/CLAUDE.md` - Backend-specific guide
4. `frontend/CLAUDE.md` - Frontend-specific guide

**External resources:**
- [Serverless Framework Docs](https://www.serverless.com/framework/docs)
- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [AWS Lambda Best Practices](https://docs.aws.amazon.com/lambda/latest/dg/best-practices.html)

### Useful Commands

**Backend:**
```bash
cd backend

# Install dependencies
poetry install

# Format code
poetry run black src/

# Lint code
poetry run flake8 src/

# Type check
poetry run mypy src/

# Run tests
poetry run pytest

# Add new dependency
poetry add package-name

# Add dev dependency
poetry add --group dev package-name

# Update dependencies
poetry update

# Deploy
npm run deploy:dev
```

**Frontend:**
```bash
# Type check
npm run type-check

# Build
npm run build

# Preview production build
npm run preview
```

### Contact & Support

- **Repository:** Check recent commits and PRs for context
- **Documentation:** Always check `docs/` folder first
- **Issues:** Review `.git` history for similar problems

---

## Quick Reference

### File Locations

| What | Where |
|------|-------|
| Lambda handler | `backend/src/functions/{domain}/{action}.py` |
| Domain entity | `backend/src/domain/entities/{entity}.py` |
| Repository interface | `backend/src/domain/ports/{entity}_repository.py` |
| Repository implementation | `backend/src/infrastructure/repositories/{entity}_repository_impl.py` |
| API service | `frontend/src/api/modules/{domain}Api.ts` |
| Composable | `frontend/src/composables/use{Feature}.ts` |
| Type definition | `frontend/src/core/types/{type}.ts` |
| Vue component | `frontend/src/components/{base|modules}/{Component}.vue` |
| Vue page | `frontend/src/pages/{Page}.vue` |

### Code Snippets

**Lambda Handler Template:**
```python
from ...shared.utils.response import success_response, error_response
from ...shared.middleware.logger import logger

def lambda_handler(event, context):
    try:
        logger.info(f"Event: {event}")
        # Your logic here
        return success_response(data)
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return error_response('ERROR_CODE', str(e), status_code=500)
```

**Vue Composable Template:**
```typescript
import { ref } from 'vue';
import type { YourType } from '@/core/types/yourType';

export function useYourFeature() {
  const data = ref<YourType[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const fetchData = async () => {
    isLoading.value = true;
    error.value = null;
    try {
      data.value = await yourApi.fetchData();
    } catch (err) {
      error.value = 'Failed to fetch data';
    } finally {
      isLoading.value = false;
    }
  };

  return { data, isLoading, error, fetchData };
}
```

---

**Last Updated:** 2025-11-15
**Version:** 1.0.0
**Maintainer:** AI Assistant (Claude)

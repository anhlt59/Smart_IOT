# IoT Monitoring Application

A full-stack IoT monitoring application with a Vue.js frontend and AWS Lambda backend (running locally with serverless-offline).

## Architecture

### Backend
- **Framework**: Serverless Framework with AWS Lambda (Python 3.11)
- **Architecture**: Hexagonal Architecture pattern
- **Local Development**: serverless-offline for local API Gateway simulation
- **API**: REST API with CORS enabled

### Frontend
- **Framework**: Vue 3 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **State Management**: Pinia
- **Routing**: Vue Router
- **HTTP Client**: Axios

## Project Structure

```
Smart_IOT/
├── backend/                 # Serverless Lambda backend
│   ├── src/
│   │   ├── functions/      # Lambda function handlers
│   │   │   ├── device/     # Device management endpoints
│   │   │   ├── alert/      # Alert management endpoints
│   │   │   └── websocket/  # WebSocket handlers
│   │   ├── shared/         # Shared utilities
│   │   │   ├── config/     # Configuration
│   │   │   ├── middleware/ # Logger, etc.
│   │   │   └── utils/      # Response helpers
│   │   └── domain/         # Domain models
│   ├── package.json
│   ├── requirements.txt
│   └── serverless.yml
│
└── frontend/               # Vue.js frontend
    ├── src/
    │   ├── api/           # API client and services
    │   ├── components/    # Vue components
    │   ├── composables/   # Vue composables (business logic)
    │   ├── core/          # Types and constants
    │   ├── pages/         # Page components
    │   ├── router/        # Vue Router configuration
    │   └── store/         # Pinia stores
    ├── package.json
    └── vite.config.ts
```

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.11+
- npm or yarn

### Installation

1. **Install Backend Dependencies**

```bash
cd backend

# Install Node.js dependencies (for serverless)
npm install

# Create virtual environment and install Python dependencies
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Install Frontend Dependencies**

```bash
cd frontend
npm install
```

### Running the Application

#### Option 1: Use the convenience script

From the root directory:

```bash
./start-dev.sh
```

This will start both backend and frontend servers.

#### Option 2: Start services individually

**Terminal 1 - Backend:**
```bash
cd backend
npm run dev
```
Backend will be available at http://localhost:3000

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend will be available at http://localhost:5173

## API Endpoints

The backend exposes the following REST API endpoints:

### Devices
- `GET /devices` - List all devices with pagination
- `GET /devices/{deviceId}` - Get device by ID
- `POST /devices` - Register a new device
- `PUT /devices/{deviceId}` - Update device metadata
- `DELETE /devices/{deviceId}` - Delete a device
- `GET /devices/{deviceId}/history` - Get device sensor data history

### Alerts
- `GET /alerts` - List alerts with filters
- `GET /alerts/{alertId}` - Get alert details
- `POST /alerts/{alertId}/acknowledge` - Acknowledge an alert
- `POST /alerts/{alertId}/resolve` - Resolve an alert

### WebSocket
- `$connect` - WebSocket connection handler
- `$disconnect` - WebSocket disconnection handler
- `subscribe` - Subscribe to device updates

## Testing the Integration

### 1. Test Backend API Directly

```bash
# Test devices endpoint
curl http://localhost:3000/devices | jq

# Test alerts endpoint
curl http://localhost:3000/alerts | jq
```

### 2. Test Frontend

1. Open http://localhost:5173 in your browser
2. The dashboard should load and display:
   - Device statistics (2 devices - 1 online, 1 with warning)
   - Alert statistics (3 alerts - 1 critical, 1 warning, 1 resolved)
   - Recent devices list
   - Recent alerts list
   - Device health metrics

### 3. Verify Integration

The frontend makes API calls to the backend on page load. Check the browser console (F12) to see:
- Network requests to http://localhost:3000/devices and /alerts
- Successful responses with status 200
- Data being displayed in the UI

## Current Features

### Implemented
- ✅ Backend API with serverless-offline
- ✅ Frontend API client with Axios
- ✅ Composables for business logic (useDevices, useAlerts)
- ✅ Dashboard page with real API integration
- ✅ Mock data for devices and alerts
- ✅ CORS configuration
- ✅ Error handling
- ✅ Loading states

### Mock Data Available

**Devices:**
- Office Temperature Sensor (online, temperature-sensor)
- Warehouse Humidity Sensor (warning, humidity-sensor)

**Alerts:**
- High Temperature Alert (critical, triggered)
- Low Battery Warning (warning, acknowledged)
- Connectivity Issue (info, resolved)

## Development

### Backend Development

The backend uses hexagonal architecture:
- **Domain Layer**: Core business logic and entities
- **Application Layer**: Use cases and application services
- **Infrastructure Layer**: AWS services, repositories, external APIs

Lambda functions are in `backend/src/functions/` and follow this pattern:
```python
from ...shared.utils.response import success_response, error_response

def lambda_handler(event, context):
    try:
        # Business logic here
        return success_response(data)
    except Exception as e:
        return error_response('ERROR_CODE', str(e), status_code=500)
```

### Frontend Development

The frontend follows a layered architecture:
- **Core**: TypeScript types and constants
- **API**: HTTP client and service modules
- **Composables**: Reusable business logic
- **Components**: UI components
- **Pages**: Route-level components

To add a new API endpoint:
1. Add types in `frontend/src/core/types/`
2. Create API service in `frontend/src/api/modules/`
3. Create composable in `frontend/src/composables/`
4. Use composable in components/pages

## Environment Configuration

### Backend
- `PORT`: API Gateway port (default: 3000)
- `STAGE`: Deployment stage (dev/prod)

### Frontend
- `VITE_API_BASE_URL`: Backend API URL (default: http://localhost:3000/api)
- `VITE_WS_URL`: WebSocket URL (default: ws://localhost:3000)

Environment files:
- `.env.development` - Development environment
- `.env.production` - Production environment

## Troubleshooting

### Backend not starting
- Ensure Python virtual environment is activated
- Check that all Python dependencies are installed
- Verify Node.js dependencies are installed

### Frontend can't connect to backend
- Ensure backend is running on port 3000
- Check CORS configuration in Lambda responses
- Verify `VITE_API_BASE_URL` in `.env.development`

### TypeScript errors in frontend
- Run `npm run type-check` to see all type errors
- Ensure all imports are correct

## Next Steps

To complete the application:

1. **Add Authentication**
   - Implement AWS Cognito integration
   - Add login/register pages
   - Protect routes with auth guards

2. **Add Real Data Sources**
   - Connect to DynamoDB for device/alert storage
   - Connect to Timestream for sensor data
   - Implement real-time updates with WebSocket

3. **Add More Features**
   - Device registration form
   - Alert rule management
   - Sensor data visualization with charts
   - Firmware update management

4. **Deploy to AWS**
   - Deploy backend with `serverless deploy`
   - Build frontend with `npm run build`
   - Deploy frontend to S3 + CloudFront

## Contributing

1. Create a feature branch
2. Make your changes
3. Test locally
4. Commit with clear messages
5. Push and create pull request

## License

MIT

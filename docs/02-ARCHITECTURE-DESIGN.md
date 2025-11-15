# Architecture Design - IoT Monitoring Application

## 1. Architecture Overview

The IoT Monitoring Application follows a **serverless, event-driven architecture** built on AWS cloud services, implementing **Hexagonal Architecture** (Ports and Adapters) principles to ensure modularity, testability, and maintainability.

### 1.1 Architecture Principles

- **Serverless-First**: Minimize operational overhead using managed services
- **Event-Driven**: Decouple components using asynchronous messaging
- **Hexagonal Architecture**: Separate core business logic from infrastructure concerns
- **Scalability**: Auto-scale based on demand
- **Resilience**: Design for failure with retry mechanisms and circuit breakers
- **Security**: Implement defense-in-depth security strategy
- **Cost-Optimization**: Pay only for what you use

### 1.2 High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              IoT DEVICES LAYER                              │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Sensors  │  │  Gateways│  │ Actuators│  │  Meters  │  │  Cameras │     │
│  │ (Wi-Fi)  │  │(LoRaWAN) │  │(Cellular)│  │  (NB-IoT)│  │ (4G/5G)  │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┼───────────┘
        │             │             │             │             │
        └─────────────┴─────────────┴─────────────┴─────────────┘
                                    │
                    ┌───────────────▼────────────────┐
                    │    Soracom SIM Management      │
                    │  (Cellular Connectivity Layer) │
                    └───────────────┬────────────────┘
                                    │
┌───────────────────────────────────▼─────────────────────────────────────────┐
│                          AWS IoT INGESTION LAYER                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────┐         │
│  │                      AWS IoT Core                              │         │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │         │
│  │  │ Device       │  │  IoT Rules   │  │ Device       │        │         │
│  │  │ Registry     │  │  Engine      │  │ Shadow       │        │         │
│  │  └──────────────┘  └──────┬───────┘  └──────────────┘        │         │
│  └─────────────────────────────┼──────────────────────────────────┘         │
└─────────────────────────────────┼──────────────────────────────────────────┘
                                  │
        ┌─────────────────────────┼─────────────────────────┐
        │                         │                         │
        ▼                         ▼                         ▼
┌──────────────┐        ┌──────────────────┐      ┌─────────────────┐
│ Lambda       │        │ Amazon Kinesis   │      │ AWS IoT         │
│ (Device      │        │ Data Streams     │      │ Analytics       │
│ Auth)        │        │ (Real-time)      │      │ (Advanced)      │
└──────────────┘        └────────┬─────────┘      └─────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
┌───────────────────────────────────────────────────────────────────────────┐
│                      STREAM PROCESSING LAYER                              │
├───────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────┐           │
│  │         Lambda Functions (Stream Consumers)                │           │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │           │
│  │  │ Data         │  │ Data         │  │ Anomaly      │    │           │
│  │  │ Validator    │  │ Transformer  │  │ Detector     │    │           │
│  │  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │           │
│  └─────────┼──────────────────┼──────────────────┼────────────┘           │
└────────────┼──────────────────┼──────────────────┼────────────────────────┘
             │                  │                  │
             └──────────────────┴──────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
┌─────────────────────────────┐   ┌─────────────────────────────┐
│     DATA STORAGE LAYER      │   │   MONITORING ENGINE         │
├─────────────────────────────┤   ├─────────────────────────────┤
│ ┌──────────────────────┐    │   │ ┌─────────────────────┐     │
│ │ Amazon Timestream    │    │   │ │ Lambda              │     │
│ │ (Time-series data)   │    │   │ │ (Rule Evaluator)    │     │
│ │                      │    │   │ └──────────┬──────────┘     │
│ │ - Memory Store (24h) │    │   │            │                │
│ │ - Magnetic Store (∞) │    │   │            ▼                │
│ └──────────────────────┘    │   │ ┌─────────────────────┐     │
│                             │   │ │ Amazon SQS          │     │
│ ┌──────────────────────┐    │   │ │ (Alert Queue)       │     │
│ │ Amazon DynamoDB      │    │   │ └──────────┬──────────┘     │
│ │                      │    │   └────────────┼────────────────┘
│ │ - Devices            │    │                │
│ │ - Users              │    │                ▼
│ │ - Alert Rules        │    │   ┌─────────────────────────────┐
│ │ - Notifications Log  │    │   │   NOTIFICATION LAYER        │
│ │ - Firmware Metadata  │    │   ├─────────────────────────────┤
│ └──────────────────────┘    │   │ ┌─────────────────────┐     │
│                             │   │ │ Lambda              │     │
│ ┌──────────────────────┐    │   │ │ (Notification       │     │
│ │ Amazon S3            │    │   │ │  Dispatcher)        │     │
│ │                      │    │   │ └──────────┬──────────┘     │
│ │ - Firmware Packages  │    │   │            │                │
│ │ - Data Exports       │    │   │   ┌────────┼────────┐       │
│ │ - Logs Archive       │    │   │   │        │        │       │
│ └──────────────────────┘    │   │   ▼        ▼        ▼       │
└─────────────────────────────┘   │ ┌────┐ ┌─────┐ ┌──────┐    │
                                  │ │SES │ │ FCM │ │ SNS  │    │
                                  │ │Email│ │Push │ │ SMS  │    │
                                  │ └────┘ └─────┘ └──────┘    │
                                  └─────────────────────────────┘
                                                │
┌───────────────────────────────────────────────┼───────────────────────────┐
│                          APPLICATION LAYER    │                           │
├───────────────────────────────────────────────┼───────────────────────────┤
│  ┌────────────────────────────────────────────▼────────────┐              │
│  │              Amazon API Gateway                         │              │
│  │  ┌──────────────────┐  ┌──────────────────┐            │              │
│  │  │ REST API         │  │ WebSocket API    │            │              │
│  │  │ (CRUD Ops)       │  │ (Real-time)      │            │              │
│  │  └────────┬─────────┘  └────────┬─────────┘            │              │
│  └───────────┼─────────────────────┼────────────────────────┘              │
│              │                     │                                       │
│  ┌───────────▼─────────────────────▼──────────────────────┐               │
│  │          Lambda Functions (Hexagonal Core)             │               │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │               │
│  │  │ Device Mgmt  │  │ User Mgmt    │  │ Analytics   │  │               │
│  │  │ Service      │  │ Service      │  │ Service     │  │               │
│  │  └──────────────┘  └──────────────┘  └─────────────┘  │               │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │               │
│  │  │ Alert Mgmt   │  │ Firmware     │  │ Report Gen  │  │               │
│  │  │ Service      │  │ Service      │  │ Service     │  │               │
│  │  └──────────────┘  └──────────────┘  └─────────────┘  │               │
│  └────────────────────────────────────────────────────────┘               │
└───────────────────────────────────────┬───────────────────────────────────┘
                                        │
┌───────────────────────────────────────▼───────────────────────────────────┐
│                        PRESENTATION LAYER                                 │
├───────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────┐          │
│  │              CloudFront (CDN)                               │          │
│  │  ┌──────────────────────────────────────────────┐           │          │
│  │  │     S3 Static Website Hosting                │           │          │
│  │  │  ┌────────────────────────────────────┐      │           │          │
│  │  │  │   Vue.js Web Application           │      │           │          │
│  │  │  │  - Device Dashboard                │      │           │          │
│  │  │  │  - Real-time Monitoring            │      │           │          │
│  │  │  │  - Alert Management                │      │           │          │
│  │  │  │  - Analytics & Reports             │      │           │          │
│  │  │  └────────────────────────────────────┘      │           │          │
│  │  └──────────────────────────────────────────────┘           │          │
│  └─────────────────────────────────────────────────────────────┘          │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                     SECURITY & IDENTITY LAYER                             │
├───────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐        │
│  │ Amazon Cognito   │  │ AWS Secrets      │  │ AWS KMS          │        │
│  │ (User Auth)      │  │ Manager          │  │ (Encryption)     │        │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘        │
└───────────────────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────────────────┐
│                   MONITORING & OBSERVABILITY LAYER                        │
├───────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ CloudWatch   │  │ CloudWatch   │  │ X-Ray        │  │ CloudTrail   │  │
│  │ Metrics      │  │ Logs         │  │ (Tracing)    │  │ (Audit)      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘  │
└───────────────────────────────────────────────────────────────────────────┘
```

## 2. Data Flow Diagrams

### 2.1 Device Data Ingestion Flow

```
┌─────────────┐
│ IoT Device  │
│ (Sensor)    │
└──────┬──────┘
       │ 1. MQTT Publish
       │ Topic: dt/devices/{deviceId}/telemetry
       │ Payload: {temp: 25.5, humidity: 60, co2: 450, timestamp: ...}
       │
       ▼
┌──────────────────────────────────────────────────┐
│            AWS IoT Core                          │
│  ┌────────────────────────────────────────┐      │
│  │  Device Certificate Validation         │      │
│  │  Policy Authorization                  │      │
│  └───────────────┬────────────────────────┘      │
│                  │                                │
│  ┌───────────────▼────────────────────────┐      │
│  │  IoT Rules Engine                      │      │
│  │  Rule: "Forward all telemetry"         │      │
│  │  SQL: SELECT * FROM                    │      │
│  │       'dt/devices/+/telemetry'         │      │
│  └───────────────┬────────────────────────┘      │
└──────────────────┼───────────────────────────────┘
                   │
       ┌───────────┴───────────┐
       │                       │
       ▼                       ▼
┌──────────────┐      ┌────────────────────┐
│ Kinesis      │      │ Lambda             │
│ Data Stream  │      │ (Enrichment)       │
│              │      │                    │
│ Partition:   │      │ - Add metadata     │
│ deviceId     │      │ - Validate schema  │
└──────┬───────┘      └──────┬─────────────┘
       │                     │
       │ 2. Stream Records   │ 3. Enriched Data
       │                     │
       ▼                     ▼
┌─────────────────────────────────────────┐
│  Lambda: Stream Processor               │
│  (Consumer of Kinesis)                  │
│                                         │
│  Process Flow:                          │
│  1. Deserialize data                    │
│  2. Validate against device schema      │
│  3. Transform units if needed           │
│  4. Calculate derived metrics           │
│  5. Detect anomalies                    │
│  6. Parallel write to storage           │
└──────┬─────────────────────┬────────────┘
       │                     │
       │ 4a. Time-series     │ 4b. Metadata
       │                     │
       ▼                     ▼
┌──────────────┐      ┌─────────────────┐
│ Timestream   │      │ DynamoDB        │
│              │      │                 │
│ Table:       │      │ Table: Devices  │
│ SensorData   │      │ - Last reading  │
│              │      │ - Last seen     │
│ Write:       │      │ - Status        │
│ - deviceId   │      │ - Metrics cache │
│ - timestamp  │      └─────────────────┘
│ - measures   │
│   (temp,     │
│    humidity, │
│    co2, ...)  │
└──────────────┘
       │
       │ 5. Query for monitoring
       │
       ▼
┌─────────────────────────────────────────┐
│  Lambda: Alert Rule Evaluator           │
│  (Triggered every 1 min via EventBridge)│
│                                         │
│  Process Flow:                          │
│  1. Fetch active alert rules from DB    │
│  2. Query Timestream for recent data    │
│  3. Evaluate conditions                 │
│  4. Check de-duplication window         │
│  5. Generate alerts if triggered        │
└──────┬──────────────────────────────────┘
       │
       │ 6. Alert event
       │
       ▼
┌──────────────────┐
│ Amazon SQS       │
│ (Alert Queue)    │
│                  │
│ Message:         │
│ {                │
│   alertId: ...   │
│   deviceId: ...  │
│   condition: ... │
│   severity: ...  │
│   timestamp: ... │
│ }                │
└──────┬───────────┘
       │
       │ 7. Process alert
       │
       ▼
┌─────────────────────────────────────────┐
│  Lambda: Notification Dispatcher        │
│                                         │
│  Process Flow:                          │
│  1. Fetch alert details                 │
│  2. Fetch user preferences              │
│  3. Generate notification content       │
│  4. Route to appropriate channels       │
│  5. Log notification delivery           │
└──────┬─────────────────────┬────────────┘
       │                     │
       │ 8a. Email           │ 8b. Push
       │                     │
       ▼                     ▼
┌──────────────┐      ┌─────────────┐
│ Amazon SES   │      │ Firebase    │
│ (Email)      │      │ FCM (Push)  │
└──────────────┘      └─────────────┘
       │                     │
       └──────────┬──────────┘
                  │
                  ▼
          ┌───────────────┐
          │  End User     │
          │  (Mobile/Web) │
          └───────────────┘
```

### 2.2 User Interaction Flow (Dashboard)

```
┌──────────────┐
│  User        │
│  (Browser)   │
└──────┬───────┘
       │
       │ 1. HTTPS Request
       │ GET /dashboard
       │
       ▼
┌────────────────────────────┐
│  CloudFront (CDN)          │
│  - SSL/TLS Termination     │
│  - Static Content Cache    │
└──────┬─────────────────────┘
       │
       │ 2. Serve static files
       │
       ▼
┌────────────────────────────┐
│  S3 Static Website         │
│  - index.html              │
│  - Vue.js app bundle       │
│  - CSS, images             │
└──────┬─────────────────────┘
       │
       │ 3. Load Vue app
       │
       ▼
┌────────────────────────────────────────┐
│  Vue.js Application (Browser)          │
│                                        │
│  4. User Login                         │
│     ┌─────────────────┐                │
│     │ Login Component │                │
│     └────────┬────────┘                │
└──────────────┼─────────────────────────┘
               │
               │ 5. Authenticate
               │ POST /auth/login
               │
               ▼
┌────────────────────────────────────────┐
│  Amazon Cognito                        │
│  - Verify credentials                  │
│  - Issue JWT tokens                    │
│    (ID token, Access token, Refresh)   │
└────────────┬───────────────────────────┘
             │
             │ 6. Return JWT tokens
             │
             ▼
┌────────────────────────────────────────┐
│  Vue.js Application                    │
│  - Store tokens (localStorage)         │
│  - Navigate to dashboard               │
│                                        │
│  7. Fetch dashboard data               │
│     ┌─────────────────┐                │
│     │ Dashboard View  │                │
│     │ (useDevices,    │                │
│     │  useAlerts)     │                │
│     └────────┬────────┘                │
└──────────────┼─────────────────────────┘
               │
               │ 8. API Request
               │ GET /api/devices
               │ Authorization: Bearer {JWT}
               │
               ▼
┌────────────────────────────────────────┐
│  API Gateway                           │
│  - Validate JWT (Cognito Authorizer)   │
│  - Rate limiting                       │
│  - Request validation                  │
└────────────┬───────────────────────────┘
             │
             │ 9. Invoke Lambda
             │
             ▼
┌────────────────────────────────────────┐
│  Lambda: Device Service                │
│  (Hexagonal Architecture)              │
│                                        │
│  ┌──────────────────────────────────┐  │
│  │  API Handler (Adapter)           │  │
│  │  - Parse request                 │  │
│  │  - Call domain service           │  │
│  └────────────┬─────────────────────┘  │
│               ▼                        │
│  ┌──────────────────────────────────┐  │
│  │  Domain Service (Core)           │  │
│  │  - Business logic                │  │
│  │  - Validation                    │  │
│  └────────────┬─────────────────────┘  │
│               ▼                        │
│  ┌──────────────────────────────────┐  │
│  │  Repository (Adapter)            │  │
│  │  - Data access                   │  │
│  └────────────┬─────────────────────┘  │
└───────────────┼────────────────────────┘
                │
                │ 10. Query data
                │
                ▼
┌─────────────────────────────────────────┐
│  DynamoDB: Devices Table                │
│  - Fetch devices for user's org        │
│  - Apply filters                        │
│  - Return device metadata               │
└────────────┬────────────────────────────┘
             │
             │ 11. Return data
             │
             ▼
┌────────────────────────────────────────┐
│  Lambda: Device Service                │
│  - Format response                     │
│  - Add HATEOAS links                   │
└────────────┬───────────────────────────┘
             │
             │ 12. HTTP Response
             │ 200 OK
             │ {devices: [...]}
             │
             ▼
┌────────────────────────────────────────┐
│  API Gateway                           │
│  - Add CORS headers                    │
│  - Log request                         │
└────────────┬───────────────────────────┘
             │
             │ 13. Response
             │
             ▼
┌────────────────────────────────────────┐
│  Vue.js Application                    │
│  - Update reactive state               │
│  - Render device list                  │
│                                        │
│  14. Establish WebSocket               │
│      (for real-time updates)           │
└──────────────┼─────────────────────────┘
               │
               │ WSS connection
               │
               ▼
┌────────────────────────────────────────┐
│  API Gateway WebSocket                 │
│  - Connection management               │
└────────────┬───────────────────────────┘
             │
             │ Store connection
             │
             ▼
┌────────────────────────────────────────┐
│  DynamoDB: Connections Table           │
│  - connectionId                        │
│  - userId                              │
│  - subscribedDevices[]                 │
└────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│  When new data arrives:                 │
│                                         │
│  Lambda: Real-time Notifier             │
│  - Fetch active WebSocket connections   │
│  - Filter by subscriptions              │
│  - Push updates via API Gateway         │
└──────────────┬──────────────────────────┘
               │
               │ Push message
               │
               ▼
┌────────────────────────────────────────┐
│  Vue.js Application                    │
│  - Receive WebSocket message           │
│  - Update reactive state               │
│  - UI auto-updates                     │
└────────────────────────────────────────┘
```

### 2.3 Firmware Update Flow (FOTA)

```
┌──────────────┐
│  Admin User  │
└──────┬───────┘
       │
       │ 1. Upload firmware
       │ POST /api/firmware/upload
       │
       ▼
┌────────────────────────────────────────┐
│  API Gateway + Lambda                  │
│  (Firmware Service)                    │
│                                        │
│  Validation:                           │
│  - File format (binary, .bin, .hex)    │
│  - Signature verification              │
│  - Version number format               │
│  - Target device types                 │
└────────────┬───────────────────────────┘
             │
             │ 2. Generate pre-signed URL
             │
             ▼
┌────────────────────────────────────────┐
│  S3: Firmware Bucket                   │
│  - Upload firmware package             │
│  - Versioning enabled                  │
│  - Encryption at rest (KMS)            │
└────────────┬───────────────────────────┘
             │
             │ 3. S3 Event Notification
             │
             ▼
┌────────────────────────────────────────┐
│  Lambda: Firmware Processor            │
│                                        │
│  Actions:                              │
│  - Calculate checksum (SHA-256)        │
│  - Extract metadata                    │
│  - Virus scan (optional)               │
│  - Create DynamoDB record              │
└────────────┬───────────────────────────┘
             │
             │ 4. Store metadata
             │
             ▼
┌────────────────────────────────────────┐
│  DynamoDB: Firmware Table              │
│  {                                     │
│    firmwareId: "fw-123"                │
│    version: "2.1.0"                    │
│    deviceTypes: ["sensor-temp-v2"]     │
│    s3Key: "firmware/fw-123.bin"        │
│    checksum: "a1b2c3..."               │
│    size: 524288                        │
│    status: "available"                 │
│    uploadedBy: "admin@example.com"     │
│    uploadedAt: "2025-11-15T10:00:00Z"  │
│  }                                     │
└────────────────────────────────────────┘
             │
             │ 5. Admin creates deployment
             │ POST /api/firmware/deployments
             │ {
             │   firmwareId: "fw-123"
             │   targetDevices: ["device-1", "device-2"]
             │   strategy: "staged" (canary/all-at-once/staged)
             │   batchSize: 10
             │   schedule: "2025-11-15T14:00:00Z"
             │ }
             │
             ▼
┌────────────────────────────────────────┐
│  Lambda: Deployment Service            │
│                                        │
│  Actions:                              │
│  - Create deployment record            │
│  - Schedule EventBridge rule           │
│  - Prepare device batches              │
└────────────┬───────────────────────────┘
             │
             │ 6. Store deployment
             │
             ▼
┌────────────────────────────────────────┐
│  DynamoDB: Deployments Table           │
│  {                                     │
│    deploymentId: "dep-456"             │
│    firmwareId: "fw-123"                │
│    status: "scheduled"                 │
│    strategy: "staged"                  │
│    batches: [                          │
│      {                                 │
│        batchId: 1,                     │
│        devices: ["device-1", "..."],   │
│        status: "pending"               │
│      }                                 │
│    ]                                   │
│  }                                     │
└────────────────────────────────────────┘
             │
             │ 7. EventBridge triggers deployment
             │
             ▼
┌────────────────────────────────────────┐
│  Lambda: Update Orchestrator           │
│                                        │
│  For each batch:                       │
│  1. Update deployment status           │
│  2. For each device in batch:          │
│     - Check device online status       │
│     - Send update job to IoT Core      │
│  3. Monitor progress                   │
│  4. Proceed to next batch if success   │
│     rate > 95%                         │
└────────────┬───────────────────────────┘
             │
             │ 8. Create IoT Job
             │
             ▼
┌────────────────────────────────────────┐
│  AWS IoT Jobs                          │
│  Job Document:                         │
│  {                                     │
│    operation: "firmware_update"        │
│    firmwareVersion: "2.1.0"            │
│    downloadUrl: "https://s3..."        │
│    checksum: "a1b2c3..."               │
│    size: 524288                        │
│  }                                     │
└────────────┬───────────────────────────┘
             │
             │ 9. Device polls for jobs
             │ (or receives job via MQTT)
             │
             ▼
┌────────────────────────────────────────┐
│  IoT Device                            │
│                                        │
│  Update Process:                       │
│  1. Receive job notification           │
│  2. Download firmware from S3          │
│  3. Verify checksum                    │
│  4. Update job status: "in_progress"   │
│  5. Flash firmware to memory           │
│  6. Reboot device                      │
│  7. Verify new firmware                │
│  8. Update job status: "succeeded"     │
│  9. Report new version to IoT Core     │
└────────────┬───────────────────────────┘
             │
             │ 10. Job status updates
             │
             ▼
┌────────────────────────────────────────┐
│  AWS IoT Jobs (Status Tracking)        │
└────────────┬───────────────────────────┘
             │
             │ 11. EventBridge rule
             │ (Job status changed)
             │
             ▼
┌────────────────────────────────────────┐
│  Lambda: Deployment Monitor            │
│                                        │
│  Actions:                              │
│  - Update deployment statistics        │
│  - Check success rate                  │
│  - Trigger next batch or rollback      │
│  - Send notifications                  │
└────────────┬───────────────────────────┘
             │
             │ 12. Update statistics
             │
             ▼
┌────────────────────────────────────────┐
│  DynamoDB: Deployments Table           │
│  Update:                               │
│  - Batch status                        │
│  - Device update status                │
│  - Overall progress %                  │
│  - Success/failure counts              │
└────────────────────────────────────────┘
             │
             │ 13. If failures > threshold
             │
             ▼
┌────────────────────────────────────────┐
│  Lambda: Rollback Handler              │
│                                        │
│  Actions:                              │
│  - Halt deployment                     │
│  - Notify administrators               │
│  - Optionally trigger rollback job     │
└────────────────────────────────────────┘
```

### 2.4 Alert Processing Flow

```
┌──────────────────────────────────────────┐
│  EventBridge (Cron Schedule)             │
│  Rule: "Every 1 minute"                  │
└──────────────┬───────────────────────────┘
               │
               │ Trigger
               │
               ▼
┌────────────────────────────────────────────────────────────────┐
│  Lambda: Alert Rule Evaluator                                  │
│                                                                │
│  Step 1: Fetch Active Rules                                   │
│  ┌──────────────────────────────────────────────────────┐     │
│  │ DynamoDB: AlertRules Table                           │     │
│  │ Query: status = "active"                             │     │
│  │                                                      │     │
│  │ Example Rules:                                       │     │
│  │ {                                                    │     │
│  │   ruleId: "rule-temp-high"                           │     │
│  │   condition: "temperature > 30"                      │     │
│  │   deviceType: "sensor-temp-v2"                       │     │
│  │   severity: "warning"                                │     │
│  │   cooldownPeriod: 300 (seconds)                      │     │
│  │ }                                                    │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                │
│  Step 2: For each rule type, fetch recent data                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │ Timestream Query:                                    │     │
│  │                                                      │     │
│  │ SELECT deviceId, measure_value::double as temp       │     │
│  │ FROM SensorData                                      │     │
│  │ WHERE measure_name = 'temperature'                   │     │
│  │   AND time > ago(5m)                                 │     │
│  │   AND deviceType = 'sensor-temp-v2'                  │     │
│  │ GROUP BY deviceId                                    │     │
│  └──────────────────────────────────────────────────────┘     │
│                                                                │
│  Step 3: Evaluate conditions                                  │
│  For each device:                                             │
│    if (temp > 30):                                            │
│      - Check if alert already fired (de-duplication)          │
│      - Check cooldown period                                  │
│      - Generate alert if conditions met                       │
│                                                                │
│  Step 4: Generate alerts                                      │
│  ┌──────────────────────────────────────────────────────┐     │
│  │ Alert Object:                                        │     │
│  │ {                                                    │     │
│  │   alertId: "alert-123"                               │     │
│  │   ruleId: "rule-temp-high"                           │     │
│  │   deviceId: "device-abc"                             │     │
│  │   severity: "warning"                                │     │
│  │   condition: "temperature > 30"                      │     │
│  │   actualValue: 32.5                                  │     │
│  │   timestamp: "2025-11-15T10:05:00Z"                  │     │
│  │   status: "triggered"                                │     │
│  │ }                                                    │     │
│  └──────────────────────────────────────────────────────┘     │
└────────────┬───────────────────────────────────────────────────┘
             │
             │ 5. Send to SQS
             │
             ▼
┌────────────────────────────────────────┐
│  Amazon SQS: Alert Queue               │
│  - De-coupling                         │
│  - Buffering                           │
│  - Retry handling                      │
│  - Visibility timeout: 30s             │
└────────────┬───────────────────────────┘
             │
             │ 6. Lambda polls SQS
             │ (Batch size: 10)
             │
             ▼
┌─────────────────────────────────────────────────────────────────┐
│  Lambda: Notification Dispatcher                                │
│                                                                 │
│  Step 1: Enrich alert data                                      │
│  ┌───────────────────────────────────────────────────────┐      │
│  │ Parallel fetch:                                       │      │
│  │ - Device metadata (DynamoDB: Devices)                 │      │
│  │ - Device location/name                                │      │
│  │ - User notification preferences (DynamoDB: Users)     │      │
│  │ - Historical context (Timestream)                     │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                 │
│  Step 2: Determine notification channels                        │
│  Based on:                                                      │
│  - Alert severity                                               │
│  - User preferences                                             │
│  - Time of day (respect quiet hours)                            │
│  - Escalation policy                                            │
│                                                                 │
│  Decision Matrix:                                               │
│  ┌─────────────┬───────┬──────┬─────┐                          │
│  │ Severity    │ Email │ Push │ SMS │                          │
│  ├─────────────┼───────┼──────┼─────┤                          │
│  │ Info        │   ✓   │      │     │                          │
│  │ Warning     │   ✓   │  ✓   │     │                          │
│  │ Critical    │   ✓   │  ✓   │  ✓  │                          │
│  └─────────────┴───────┴──────┴─────┘                          │
│                                                                 │
│  Step 3: Generate notification content                          │
│  ┌───────────────────────────────────────────────────────┐      │
│  │ Template Engine:                                      │      │
│  │ - Load template for alert type                        │      │
│  │ - Replace placeholders                                │      │
│  │ - Add device context                                  │      │
│  │ - Include action links                                │      │
│  │                                                       │      │
│  │ Example Email:                                        │      │
│  │ Subject: [WARNING] High temperature at Office 301     │      │
│  │ Body:                                                 │      │
│  │   Device: Temp Sensor #123                            │      │
│  │   Location: Office 301, Building A                    │      │
│  │   Condition: Temperature exceeded 30°C                │      │
│  │   Current Value: 32.5°C                               │      │
│  │   Timestamp: 2025-11-15 10:05:00 UTC                  │      │
│  │   [View Dashboard] [Acknowledge Alert]                │      │
│  └───────────────────────────────────────────────────────┘      │
│                                                                 │
│  Step 4: Send notifications                                     │
└────────┬──────────────────────────┬────────────────────────────┘
         │                          │
         │ Email                    │ Push
         │                          │
         ▼                          ▼
┌────────────────────┐      ┌───────────────────┐
│  Amazon SES        │      │  Firebase FCM     │
│                    │      │                   │
│  - Render HTML     │      │  - Format FCM msg │
│  - Send email      │      │  - Send to device │
│  - Track delivery  │      │    tokens         │
└────────┬───────────┘      └────────┬──────────┘
         │                           │
         │ 7. Delivery status        │
         │                           │
         └──────────┬────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────┐
│  Lambda: Notification Logger            │
│                                         │
│  Actions:                               │
│  - Store notification delivery record   │
│  - Update alert status                  │
│  - Track success/failure                │
└────────────┬────────────────────────────┘
             │
             │ 8. Log notification
             │
             ▼
┌─────────────────────────────────────────┐
│  DynamoDB: Notifications Table          │
│  {                                      │
│    notificationId: "notif-789"          │
│    alertId: "alert-123"                 │
│    userId: "user-456"                   │
│    channel: "email"                     │
│    status: "delivered"                  │
│    sentAt: "2025-11-15T10:05:10Z"       │
│    deliveredAt: "2025-11-15T10:05:12Z"  │
│  }                                      │
└─────────────────────────────────────────┘
             │
             │ Also update
             │
             ▼
┌─────────────────────────────────────────┐
│  DynamoDB: Alerts Table                 │
│  Update:                                │
│  - notificationSent: true               │
│  - notificationChannels: ["email","push"]│
│  - lastNotifiedAt: timestamp            │
└─────────────────────────────────────────┘
```

## 3. Component Architecture (Hexagonal Architecture)

### 3.1 Hexagonal Architecture Overview

```
┌───────────────────────────────────────────────────────────────────┐
│                         LAMBDA FUNCTION                           │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                    ADAPTERS (Outer Layer)                   │ │
│  │                                                             │ │
│  │  ┌──────────────────┐           ┌──────────────────┐       │ │
│  │  │ API Handler      │  Driving  │ CLI Handler      │       │ │
│  │  │ (API Gateway)    │  Adapters │ (EventBridge)    │       │ │
│  │  │                  │           │                  │       │ │
│  │  │ - Parse HTTP req │           │ - Parse events   │       │ │
│  │  │ - Validate input │           │ - Trigger actions│       │ │
│  │  │ - Format HTTP res│           │ - Format output  │       │ │
│  │  └────────┬─────────┘           └─────────┬────────┘       │ │
│  │           │                               │                │ │
│  │           │  ┌────────────────────────┐   │                │ │
│  │           └─▶│    PORTS (Interfaces)  │◀──┘                │ │
│  │              │                        │                    │ │
│  │              │  - IDeviceService      │                    │ │
│  │              │  - IAlertService       │                    │ │
│  │              │  - IUserService        │                    │ │
│  │              │  - IFirmwareService    │                    │ │
│  │              └────────┬───────────────┘                    │ │
│  └───────────────────────┼────────────────────────────────────┘ │
│                          │                                      │
│  ┌───────────────────────▼────────────────────────────────────┐ │
│  │                  DOMAIN (Core Layer)                       │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────┐     │ │
│  │  │  Services (Business Logic)                       │     │ │
│  │  │                                                  │     │ │
│  │  │  - DeviceService                                 │     │ │
│  │  │    * registerDevice()                            │     │ │
│  │  │    * updateDeviceStatus()                        │     │ │
│  │  │    * getDevicesByOrganization()                  │     │ │
│  │  │                                                  │     │ │
│  │  │  - AlertService                                  │     │ │
│  │  │    * evaluateRules()                             │     │ │
│  │  │    * createAlert()                               │     │ │
│  │  │    * acknowledgeAlert()                          │     │ │
│  │  │                                                  │     │ │
│  │  │  - UserService                                   │     │ │
│  │  │    * createUser()                                │     │ │
│  │  │    * updatePreferences()                         │     │ │
│  │  │    * assignRoles()                               │     │ │
│  │  │                                                  │     │ │
│  │  │  - FirmwareService                               │     │ │
│  │  │    * uploadFirmware()                            │     │ │
│  │  │    * createDeployment()                          │     │ │
│  │  │    * monitorProgress()                           │     │ │
│  │  └──────────────────────────────────────────────────┘     │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────┐     │ │
│  │  │  Entities (Domain Models)                        │     │ │
│  │  │                                                  │     │ │
│  │  │  - Device                                        │     │ │
│  │  │    * deviceId, type, location, status, ...       │     │ │
│  │  │    * isOnline()                                  │     │ │
│  │  │    * needsUpdate()                               │     │ │
│  │  │                                                  │     │ │
│  │  │  - Alert                                         │     │ │
│  │  │    * alertId, ruleId, severity, status, ...      │     │ │
│  │  │    * shouldEscalate()                            │     │ │
│  │  │    * canAcknowledge(user)                        │     │ │
│  │  │                                                  │     │ │
│  │  │  - User                                          │     │ │
│  │  │    * userId, email, roles, preferences, ...      │     │ │
│  │  │    * hasPermission(resource, action)             │     │ │
│  │  │    * canReceiveNotification(channel)             │     │ │
│  │  │                                                  │     │ │
│  │  │  - Firmware                                      │     │ │
│  │  │    * firmwareId, version, deviceTypes, ...       │     │ │
│  │  │    * isCompatibleWith(device)                    │     │ │
│  │  └──────────────────────────────────────────────────┘     │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────┐     │ │
│  │  │  Value Objects                                   │     │ │
│  │  │                                                  │     │ │
│  │  │  - DeviceLocation(lat, lon, address)             │     │ │
│  │  │  - AlertSeverity(level, priority)                │     │ │
│  │  │  - FirmwareVersion(major, minor, patch)          │     │ │
│  │  │  - SensorReading(value, unit, timestamp)         │     │ │
│  │  └──────────────────────────────────────────────────┘     │ │
│  │                                                            │ │
│  │  ┌──────────────────────────────────────────────────┐     │ │
│  │  │  Repository Interfaces (Ports)                   │     │ │
│  │  │                                                  │     │ │
│  │  │  - IDeviceRepository                             │     │ │
│  │  │    * save(device)                                │     │ │
│  │  │    * findById(deviceId)                          │     │ │
│  │  │    * findByOrganization(orgId)                   │     │ │
│  │  │                                                  │     │ │
│  │  │  - ITimeSeriesRepository                         │     │ │
│  │  │    * writeSensorData(data)                       │     │ │
│  │  │    * queryRecentData(deviceId, timeRange)        │     │ │
│  │  │                                                  │     │ │
│  │  │  - INotificationPort                             │     │ │
│  │  │    * sendEmail(recipient, content)               │     │ │
│  │  │    * sendPush(userId, message)                   │     │ │
│  │  └──────────────────────────────────────────────────┘     │ │
│  └──────────────────────┬─────────────────────────────────────┘ │
│                         │                                       │
│  ┌──────────────────────▼──────────────────────────────────────┐ │
│  │             ADAPTERS (Infrastructure - Outer Layer)         │ │
│  │                                                             │ │
│  │  ┌──────────────────┐           ┌──────────────────┐       │ │
│  │  │ DynamoDB Adapter │  Driven   │ Timestream       │       │ │
│  │  │ (Repository)     │  Adapters │ Adapter          │       │ │
│  │  │                  │           │ (Repository)     │       │ │
│  │  │ implements:      │           │                  │       │ │
│  │  │ IDeviceRepository│           │ implements:      │       │ │
│  │  │                  │           │ ITimeSeriesRepo  │       │ │
│  │  └──────────────────┘           └──────────────────┘       │ │
│  │                                                             │ │
│  │  ┌──────────────────┐           ┌──────────────────┐       │ │
│  │  │ SES Adapter      │           │ FCM Adapter      │       │ │
│  │  │ (Notification)   │           │ (Notification)   │       │ │
│  │  │                  │           │                  │       │ │
│  │  │ implements:      │           │ implements:      │       │ │
│  │  │ INotificationPort│           │ INotificationPort│       │ │
│  │  └──────────────────┘           └──────────────────┘       │ │
│  │                                                             │ │
│  │  ┌──────────────────┐           ┌──────────────────┐       │ │
│  │  │ S3 Adapter       │           │ IoT Core Adapter │       │ │
│  │  │ (File Storage)   │           │ (Device Comm)    │       │ │
│  │  └──────────────────┘           └──────────────────┘       │ │
│  └─────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

### 3.2 Benefits of Hexagonal Architecture

1. **Testability**: Core business logic isolated, easy to unit test
2. **Maintainability**: Changes to infrastructure don't affect core logic
3. **Flexibility**: Easy to swap implementations (e.g., DynamoDB → RDS)
4. **Clear Dependencies**: Dependencies point inward (dependency inversion)
5. **Technology Agnostic**: Core logic independent of frameworks

## 4. Infrastructure Components

### 4.1 AWS Services Mapping

| Service | Purpose | Configuration |
|---------|---------|---------------|
| **AWS IoT Core** | Device connectivity, authentication, message routing | - Device registry<br>- Certificate-based auth<br>- MQTT/HTTPS protocols<br>- Thing Groups |
| **Amazon Kinesis Data Streams** | Real-time data streaming | - 4 shards (initial)<br>- Auto-scaling enabled<br>- Retention: 24 hours |
| **AWS Lambda** | Serverless compute | - Runtime: Python 3.11<br>- Memory: 512MB-3GB<br>- Timeout: 30s-900s<br>- Reserved concurrency |
| **Amazon Timestream** | Time-series database | - Memory retention: 24h<br>- Magnetic retention: 90 days<br>- Multi-AZ enabled |
| **Amazon DynamoDB** | NoSQL database | - On-demand billing<br>- Point-in-time recovery<br>- Encryption at rest<br>- Global tables (optional) |
| **Amazon S3** | Object storage | - Versioning enabled<br>- Lifecycle policies<br>- Encryption (SSE-KMS)<br>- Intelligent tiering |
| **Amazon SQS** | Message queue | - Standard queue<br>- Visibility timeout: 30s<br>- Dead-letter queue<br>- Retention: 14 days |
| **Amazon SES** | Email service | - Domain verification<br>- DKIM/SPF setup<br>- Bounce handling<br>- Sending quotas |
| **Firebase FCM** | Push notifications | - Device token management<br>- Topic subscriptions<br>- Delivery tracking |
| **API Gateway** | API management | - REST + WebSocket APIs<br>- Cognito authorizer<br>- Rate limiting<br>- Request validation |
| **Amazon Cognito** | User management | - User pools<br>- MFA enabled<br>- JWT tokens<br>- Custom attributes |
| **CloudFront** | CDN | - Edge locations<br>- Origin: S3<br>- HTTPS only<br>- Caching policies |
| **EventBridge** | Event bus, scheduling | - Cron rules<br>- Event patterns<br>- Cross-account events |
| **CloudWatch** | Monitoring, logging | - Metrics<br>- Log groups<br>- Alarms<br>- Dashboards |
| **AWS X-Ray** | Distributed tracing | - Service map<br>- Trace analysis<br>- Performance insights |
| **AWS KMS** | Key management | - CMKs for encryption<br>- Key rotation<br>- IAM policies |
| **AWS Secrets Manager** | Secrets storage | - Auto-rotation<br>- Version tracking<br>- Encryption |
| **Soracom** | SIM connectivity | - SIM card management<br>- Data usage tracking<br>- API integration |

### 4.2 Data Storage Schema Design

#### DynamoDB Tables

**Devices Table**
```
Table: iot-monitoring-devices
Partition Key: deviceId (String)
Sort Key: None
GSIs:
  - organizationId-index (PK: organizationId, SK: deviceType)
  - status-index (PK: status, SK: lastSeen)

Attributes:
{
  deviceId: String (PK)
  organizationId: String
  deviceType: String
  name: String
  location: {
    lat: Number,
    lon: Number,
    address: String
  }
  status: String (online|offline|maintenance)
  firmwareVersion: String
  lastSeen: Number (timestamp)
  lastReading: Map {
    temperature: Number,
    humidity: Number,
    co2: Number,
    ...
  }
  metadata: Map {
    model: String,
    manufacturer: String,
    serialNumber: String,
    installDate: Number,
    ...
  }
  connectivity: {
    type: String (wifi|cellular|lorawan)
    simId: String (if cellular)
    ipAddress: String
    signalStrength: Number
  }
  tags: List<String>
  createdAt: Number
  updatedAt: Number
}
```

**Users Table**
```
Table: iot-monitoring-users
Partition Key: userId (String)
Sort Key: None
GSIs:
  - email-index (PK: email)
  - organizationId-index (PK: organizationId, SK: role)

Attributes:
{
  userId: String (PK)
  email: String
  organizationId: String
  role: String (super_admin|org_admin|operator|viewer)
  preferences: {
    notifications: {
      email: Boolean,
      push: Boolean,
      sms: Boolean
    },
    quietHours: {
      enabled: Boolean,
      start: String (HH:mm),
      end: String (HH:mm),
      timezone: String
    },
    subscribedDevices: List<String>,
    dashboardLayout: Map
  }
  deviceTokens: List<String> (for FCM)
  createdAt: Number
  updatedAt: Number
}
```

**AlertRules Table**
```
Table: iot-monitoring-alert-rules
Partition Key: ruleId (String)
Sort Key: None
GSIs:
  - organizationId-status-index (PK: organizationId, SK: status)

Attributes:
{
  ruleId: String (PK)
  organizationId: String
  name: String
  description: String
  deviceType: String (or "all")
  deviceIds: List<String> (specific devices, or empty for all)
  condition: {
    metric: String (temperature|humidity|co2|...)
    operator: String (>|<|>=|<=|==)
    threshold: Number
    duration: Number (seconds, sustained condition)
  }
  severity: String (info|warning|critical)
  status: String (active|inactive)
  cooldownPeriod: Number (seconds)
  actions: {
    notifications: List<String> (email|push|sms)
    webhooks: List<String>
  }
  createdBy: String (userId)
  createdAt: Number
  updatedAt: Number
}
```

**Alerts Table**
```
Table: iot-monitoring-alerts
Partition Key: alertId (String)
Sort Key: timestamp (Number)
GSIs:
  - deviceId-timestamp-index (PK: deviceId, SK: timestamp)
  - status-severity-index (PK: status, SK: severity-timestamp)

Attributes:
{
  alertId: String (PK)
  ruleId: String
  deviceId: String
  organizationId: String
  timestamp: Number (SK)
  condition: String
  actualValue: Number
  severity: String
  status: String (triggered|acknowledged|resolved)
  acknowledgedBy: String (userId, optional)
  acknowledgedAt: Number (optional)
  resolvedAt: Number (optional)
  notificationsSent: List<String> (email|push|sms)
  metadata: Map
}
```

**Firmware Table**
```
Table: iot-monitoring-firmware
Partition Key: firmwareId (String)
Sort Key: None
GSIs:
  - deviceType-version-index (PK: deviceType, SK: version)

Attributes:
{
  firmwareId: String (PK)
  version: String (semver)
  deviceTypes: List<String>
  s3Bucket: String
  s3Key: String
  checksum: String (SHA-256)
  size: Number (bytes)
  status: String (available|deprecated|withdrawn)
  changelog: String
  uploadedBy: String (userId)
  uploadedAt: Number
  metadata: Map
}
```

**Deployments Table**
```
Table: iot-monitoring-deployments
Partition Key: deploymentId (String)
Sort Key: None
GSIs:
  - firmwareId-status-index (PK: firmwareId, SK: status)

Attributes:
{
  deploymentId: String (PK)
  firmwareId: String
  strategy: String (all-at-once|canary|staged)
  targetDevices: List<String>
  status: String (scheduled|in_progress|completed|failed|rolled_back)
  batches: List<{
    batchId: Number,
    devices: List<String>,
    status: String,
    successCount: Number,
    failureCount: Number
  }>
  progress: {
    total: Number,
    succeeded: Number,
    failed: Number,
    inProgress: Number,
    pending: Number
  }
  scheduledAt: Number
  startedAt: Number (optional)
  completedAt: Number (optional)
  createdBy: String (userId)
  createdAt: Number
}
```

#### Timestream Schema

**Database: iot_monitoring**

**Table: sensor_data**
```
Dimensions:
  - deviceId (String)
  - deviceType (String)
  - organizationId (String)
  - location (String)

Measures:
  - temperature (DOUBLE)
  - humidity (DOUBLE)
  - co2 (BIGINT)
  - pm25 (DOUBLE)
  - pm10 (DOUBLE)
  - noise (DOUBLE)
  - vibration (DOUBLE)
  - power (DOUBLE)
  - battery (DOUBLE)
  - signalStrength (BIGINT)
  - [custom measures based on device type]

Time column: timestamp

Retention:
  - Memory store: 24 hours
  - Magnetic store: 90 days (configurable)

Partitioning: Automatic by time

Magnetic store writes: Enabled
```

**Sample Query Patterns:**
```sql
-- Get latest temperature for a device
SELECT deviceId, measure_value::double as temperature, time
FROM sensor_data
WHERE deviceId = 'device-123'
  AND measure_name = 'temperature'
  AND time > ago(1h)
ORDER BY time DESC
LIMIT 1

-- Aggregate data for analytics
SELECT deviceId,
       BIN(time, 15m) as binned_time,
       AVG(measure_value::double) as avg_temp,
       MAX(measure_value::double) as max_temp,
       MIN(measure_value::double) as min_temp
FROM sensor_data
WHERE measure_name = 'temperature'
  AND time BETWEEN ago(24h) AND now()
GROUP BY deviceId, BIN(time, 15m)
ORDER BY binned_time DESC

-- Detect anomalies (values > 3 std dev from mean)
WITH stats AS (
  SELECT deviceId,
         AVG(measure_value::double) as mean,
         STDDEV(measure_value::double) as stddev
  FROM sensor_data
  WHERE measure_name = 'temperature'
    AND time > ago(7d)
  GROUP BY deviceId
)
SELECT s.deviceId, s.time, s.measure_value::double as temperature
FROM sensor_data s
JOIN stats st ON s.deviceId = st.deviceId
WHERE s.measure_name = 'temperature'
  AND s.time > ago(1h)
  AND ABS(s.measure_value::double - st.mean) > 3 * st.stddev
```

## 5. Security Architecture

### 5.1 Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: Network Security                                      │
│  - VPC with public/private subnets                              │
│  - Security Groups (least privilege)                            │
│  - NACLs                                                        │
│  - VPC Endpoints for AWS services (avoid internet)              │
│  - WAF for API Gateway                                          │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Layer 2: Device Security                                       │
│  - X.509 certificate-based authentication                       │
│  - TLS 1.2+ for all device communication                        │
│  - Certificate rotation policies                                │
│  - Device authorization via IoT policies                        │
│  - Just-in-time registration (JITR)                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Layer 3: Application Security                                  │
│  - Cognito User Pools for authentication                        │
│  - JWT tokens (short-lived: 1 hour)                             │
│  - MFA enforcement for admin roles                              │
│  - Role-Based Access Control (RBAC)                             │
│  - API Gateway authorizers                                      │
│  - Input validation at API Gateway                              │
│  - SQL injection protection (parameterized queries)             │
│  - XSS protection (output encoding)                             │
│  - CSRF tokens for state-changing operations                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Layer 4: Data Security                                         │
│  - Encryption at rest (AES-256)                                 │
│    * DynamoDB: AWS-managed CMK or customer-managed CMK          │
│    * S3: SSE-KMS                                                │
│    * Timestream: Automatic encryption                           │
│  - Encryption in transit (TLS 1.2+)                             │
│  - KMS for key management                                       │
│  - Secrets Manager for API keys, credentials                    │
│  - Data access logging (CloudTrail)                             │
│  - Fine-grained access control (IAM policies)                   │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  Layer 5: Monitoring & Incident Response                        │
│  - CloudWatch Alarms for security events                        │
│  - GuardDuty for threat detection                               │
│  - Security Hub for compliance monitoring                       │
│  - CloudTrail for audit logging                                 │
│  - Automated incident response (Lambda)                         │
│  - Regular security assessments                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 IAM Policies (Principle of Least Privilege)

```yaml
# Example: Lambda execution role for Device Service
DeviceServiceExecutionRole:
  Type: AWS::IAM::Role
  Policies:
    - PolicyName: DynamoDBAccess
      Statement:
        - Effect: Allow
          Action:
            - dynamodb:GetItem
            - dynamodb:PutItem
            - dynamodb:UpdateItem
            - dynamodb:Query
          Resource:
            - arn:aws:dynamodb:region:account:table/iot-monitoring-devices
            - arn:aws:dynamodb:region:account:table/iot-monitoring-devices/index/*
    - PolicyName: TimestreamRead
      Statement:
        - Effect: Allow
          Action:
            - timestream:Select
            - timestream:DescribeTable
          Resource:
            - arn:aws:timestream:region:account:database/iot_monitoring/table/sensor_data
    - PolicyName: CloudWatchLogs
      Statement:
        - Effect: Allow
          Action:
            - logs:CreateLogGroup
            - logs:CreateLogStream
            - logs:PutLogEvents
          Resource: arn:aws:logs:region:account:log-group:/aws/lambda/device-service:*
```

## 6. Scalability & Performance

### 6.1 Auto-Scaling Configuration

| Component | Scaling Trigger | Min | Max | Target |
|-----------|----------------|-----|-----|--------|
| **Lambda** | Automatic (on-demand) | 0 | 1000 concurrent | - |
| **Kinesis Shards** | CloudWatch alarm (IncomingRecords > 80%) | 4 | 100 | 70% utilization |
| **DynamoDB** | On-demand (auto-scaling) | - | - | - |
| **API Gateway** | No limit (managed) | - | - | 10,000 RPS |

### 6.2 Performance Optimization Strategies

1. **Lambda Optimization**
   - Use Lambda Layers for shared dependencies
   - Minimize cold starts with provisioned concurrency (critical functions)
   - Right-size memory allocation (use AWS Lambda Power Tuning)
   - Connection pooling for database clients

2. **Data Access Optimization**
   - DynamoDB: Use batch operations where possible
   - Timestream: Query only necessary time ranges
   - Caching: Implement CloudFront caching for static content
   - API Gateway caching for frequently accessed endpoints

3. **Asynchronous Processing**
   - Use SQS for non-critical operations
   - Decouple alert generation from notification delivery
   - Background jobs for report generation

4. **Monitoring & Profiling**
   - X-Ray tracing for performance bottlenecks
   - CloudWatch metrics for component-level monitoring
   - Custom business metrics

## 7. Disaster Recovery & Business Continuity

### 7.1 Backup Strategy

| Data Store | Backup Method | Frequency | Retention |
|------------|--------------|-----------|-----------|
| **DynamoDB** | Point-in-time recovery (PITR) | Continuous | 35 days |
| **S3** | Versioning + Lifecycle | Continuous | 90 days |
| **Timestream** | No backup (cold data to S3) | Daily export | 1 year |

### 7.2 High Availability

- **Multi-AZ Deployment**: All services deployed across 3 AZs
- **Regional Failover**: CloudFront + Route 53 for multi-region (optional)
- **Service SLAs**:
  - Lambda: 99.95%
  - DynamoDB: 99.99%
  - API Gateway: 99.95%
  - IoT Core: 99.9%
  - **Target System SLA**: 99.9% (43.8 minutes downtime/month)

### 7.3 Disaster Recovery Plan

- **RTO (Recovery Time Objective)**: 4 hours
- **RPO (Recovery Point Objective)**: 1 hour
- **DR Strategy**: Warm standby in secondary region (optional for critical deployments)

---

**Document Version:** 1.0
**Last Updated:** 2025-11-15
**Document Owner:** Solution Architecture Team

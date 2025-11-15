# Task

Design an IOT application that should monitor devices, analyze sensor data, send notifications,
and manage firmware updates. Provide a detailed description of the architecture, components, and technologies used.

## Output:
- Requirement Specification document for IoT Monitoring Application
- Architecture Diagram (text-based), Infrastructure Components, and Data Flow
- Folder Structure for the project (backend, frontend and infrastructure as code)
- Frontend screens and features description
- Backend services and Lambda functions description
- Notification System design

Note: Do not provide actual code implementation, only the design and structure.

## Key Technologies

- **Backend:** Serverless API Gateway with AWS Lambda functions written in Python.
- **Frontend:** VueJS for the web dashboard.
- **Framework:** Serverless Framework
- **Services:**
    - Amazon Timestream: A time-series database for storing sensor data.
    - Amazon DynamoDB: A NoSQL database for device metadata and user information.
    - Amazon Kinesis: For real-time data streaming from IoT devices.
    - AWS Lambda: For serverless compute to process data and handle business logic.
    - Amazon SQS: For decoupling components and handling asynchronous processing.
    - AWS IoT Analytics: For advanced analytics on IoT data.
    - AWS IoT Core for device communication and data ingestion.
    - Soracom for SIM card management and connectivity.
    - Amazon SES for sending email notifications.
    - Amazon SES for sending email notifications.
    - Firebase Cloud Messaging (FCM) for push notifications to mobile devices.

## Backend Architecture

The project is following the hexagonal architecture pattern. (
sample https://github.com/anhlt59/aws-monitoring/tree/feat/sigle-account)

### Core Functionality

#### 1. Data Ingestion and Processing

- **IoT Data Stream:**
  Help me to design the data ingestion flow from IoT devices to AWS services.

#### 2. Device Monitoring

The system monitors devices for various conditions and triggers notifications based on predefined thresholds. For
example:
  - **Case 1: CO2 Concentration:** Monitors for high CO2 levels.
  - **Case 2: Temperature:** Monitors for high temperatures.
  - **Case 3: Long-Term Absence:** Detects if a device has been inactive for an extended period.
  - **Case 4: Long-Term Disconnect:** Detects if a device has been offline for an extended period.
  - Help me to research then add additional cases

## Frontend Dashboard

Frontend Application Structure (Vue 3 + TS + Tailwind CSS)
This directory structure is designed based on the principle of Separation of Concerns, highly suitable for backend
experienced developers.
It facilitates easy expansion and maintenance.

1. Overall Directory Structure
   frontend/
   ├── assets/ # Static resources (images, fonts)
   ├── components/ # Vue Components
   │ ├── base/ # Basic UI Components (no business logic)
   │ └── modules/ # Components containing presentation logic by feature
   ├── composables/ # Reusable logic (equivalent to React Hooks)
   ├── core/ # Domain Definitions (TypeScript Interfaces/Types)
   ├── api/ # Backend Communication Layer (Infrastructure Adapter)
   ├── pages/ # Pages (Views) - Router Entry Points
   ├── store/ # State Management (Pinia)
   ├── styles/ # CSS Configuration (Tailwind base, custom utility)
   └── App.vue # Root Component
   └── main.ts # Vue application initialization

2. Detailed Directory Explanation
   2.1. core/ (Domain - Application Core)
   This is where the "entities" of the Frontend application are defined.
   | File/Directory Name | Role | Example |
   | core/types/ | Contains all the TypeScript Interfaces/Types (data format for User, Product, API Responses, etc.) |
   user.ts, product.ts, api.ts|
   | core/constants.ts | Global constants (API base URL, page size, Route names). | API_URL, PAGE_SIZE
   2.2. api/ (Infrastructure - API Communication Layer)
   This is where API calls are implemented (equivalent to the Adapter layer communicating with the outside in Hexagonal
   Architecture).
   | File/Directory Name | Role | Example |
   | api/modules/ | Separate API Services by Domain/Context. | users.api.ts, products.api.ts |
   | api/client.ts | Basic configuration for the HTTP library (like Axios/Fetch), handling tokens, interceptors. | Set
   up Axios instance with Base URL.
   users.api.ts Example:// users.api.ts

```
import { User } from '../core/types/user';
import apiClient from '../api/client';

export const userApiService = {
  // Function to get the list of Users
  async getUsers(): Promise<User[]> {
    const response = await apiClient.get<User[]>('/users');
    return response.data;
  },
  // Function to create a User
  async createUser(data: Partial<User>): Promise<User> {
    const response = await apiClient.post<User>('/users', data);
    return response.data;
  }
};
```

2.3. composables/ (Business/Application Logic - Hooks Equivalent)
Contains reusable functions (Custom Hooks in React), where Frontend business logic is handled (data fetching, local
state management, complex validation).
| File/Directory Name | Role | Example |
| useUsers.ts | Logic for fetching the User list (calls userApiService.getUsers(), manages isLoading state). |
Equivalent to useQuery in React Query (if not using that library). |
| useAuth.ts | Login, logout logic, checking Auth status. ||
| useDebounce.ts | General utilities. ||
useUsers.ts Example:// useUsers.ts

```
import { ref, onMounted } from 'vue';
import { userApiService } from '@/api/modules/users.api';
import { User } from '@/core/types/user';

export function useUsers() {
  const users = ref<User[]>([]);
  const isLoading = ref(true);

  const fetchUsers = async () => {
    isLoading.value = true;
    try {
      users.value = await userApiService.getUsers();
    } catch (error) {
      console.error('Error fetching User data:', error);
      // Error handling
    } finally {
      isLoading.value = false;
    }
  };

  onMounted(fetchUsers);

  return { users, isLoading, fetchUsers };
}
```

2.4. store/ (State Management - Pinia)
Uses Pinia (a lightweight, modern, and recommended Vue state management library).
| File/Directory Name | Role | Example |
| auth.store.ts | Manages login status, current User information. | Defines useAuthStore() |
| settings.store.ts | Application settings (light/dark theme, language). ||
2.5. components/ (Presentation - UI)
Separating Components into 2 types:
2.5.1. components/base/ (Dumb/UI Components)
No business logic.
Only receives data via props and emits events via emits.
Example: BaseButton.vue, BaseInput.vue, Card.vue, Modal.vue.
2.5.2. components/modules/ (Smart/Feature Components)
Contains presentation and interaction logic (uses composables/, store/).
Usually named by feature (Feature/Module).
Example: UserList.vue (calls useUsers), LoginForm.vue (calls useAuthStore).
2.6. pages/ (Views/Routes)
The highest-level Component, connecting Components and the Router.
Each file in pages/ corresponds to a Route.
Example: pages/Users.vue, pages/Home.vue, pages/Login.vue.

3. Benefits of using Vue + Tailwind + this Structure
   Maximize TypeScript Utility: Every layer (core, api, composables) is protected by TypeScript, giving you more
   confidence when working with data (which backend/infra developers highly value).
   Clear Logic:

- Data Flow: API -> Composable -> Component
- Presentation Logic: Using Tailwind, styling resides directly in the <template>. No need to switch back and forth
  between HTML/Vue and CSS files.
  Layer Separation: If you need to change the API calling method (e.g., switching from REST to GraphQL), you only need
  to modify the api/ directory without affecting composables/ or components/.
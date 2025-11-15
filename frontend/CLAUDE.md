# CLAUDE.md - Frontend (Vue.js + TypeScript)

**AI Assistant Guide for Smart_IOT Frontend Development**

This document provides detailed guidance for AI assistants working on the Vue.js frontend of the Smart_IOT platform. It covers Vue 3 best practices, TypeScript patterns, component architecture, and frontend-specific workflows.

---

## Table of Contents

1. [Frontend Overview](#frontend-overview)
2. [Tech Stack](#tech-stack)
3. [Project Structure](#project-structure)
4. [Development Workflow](#development-workflow)
5. [Architecture Patterns](#architecture-patterns)
6. [Common Tasks](#common-tasks)
7. [Code Conventions](#code-conventions)
8. [Component Guidelines](#component-guidelines)
9. [State Management](#state-management)
10. [API Integration](#api-integration)
11. [Styling Guidelines](#styling-guidelines)
12. [Testing (To Be Implemented)](#testing-to-be-implemented)
13. [Performance Optimization](#performance-optimization)
14. [Troubleshooting](#troubleshooting)

---

## Frontend Overview

### What We're Building

The Smart_IOT frontend is a **single-page application (SPA)** that provides:
- Real-time IoT device monitoring dashboard
- Alert management and notifications
- Device configuration and management
- Sensor data visualization
- User profile and settings
- Firmware update management

### Key Features

**✅ Implemented:**
- Dashboard with device and alert statistics
- API integration with backend
- Composables for business logic
- Responsive layout with Tailwind CSS
- Routing with Vue Router
- State management setup with Pinia
- Error handling and loading states

**🚧 In Progress:**
- Authentication flow
- WebSocket real-time updates
- Data visualization charts
- Device CRUD operations
- Alert rule management

**📋 Planned:**
- Firmware update UI
- User management
- Advanced analytics
- Mobile responsiveness improvements
- Dark mode

---

## Tech Stack

### Core Framework

| Technology | Version | Purpose |
|------------|---------|---------|
| Vue | 3.5.24 | Progressive JavaScript framework |
| TypeScript | 5.9.3 | Type-safe JavaScript |
| Vite | 7.2.2 | Fast build tool and dev server |

### UI & Styling

| Technology | Version | Purpose |
|------------|---------|---------|
| Tailwind CSS | 4.1.17 | Utility-first CSS framework |
| Chart.js | 4.5.1 | Data visualization |

### State & Routing

| Technology | Version | Purpose |
|------------|---------|---------|
| Pinia | 3.0.4 | Vue state management |
| Vue Router | 4.6.3 | Client-side routing |

### HTTP & Data

| Technology | Version | Purpose |
|------------|---------|---------|
| Axios | 1.13.2 | HTTP client |
| date-fns | 4.1.0 | Date formatting and manipulation |

---

## Project Structure

```
frontend/
├── src/
│   ├── core/                      # Domain definitions (types, enums, constants)
│   │   ├── types/                 # TypeScript interfaces
│   │   │   ├── device.ts          # Device, DeviceDetails, SensorReading
│   │   │   ├── alert.ts           # Alert, AlertRule, AlertSeverity
│   │   │   ├── user.ts            # User, UserProfile, UserPreferences
│   │   │   ├── firmware.ts        # FirmwareVersion, Deployment
│   │   │   └── api.ts             # ApiResponse, PaginatedResponse
│   │   │
│   │   ├── enums/                 # TypeScript enums
│   │   │   ├── DeviceStatus.ts    # online, offline, warning, error
│   │   │   ├── AlertSeverity.ts   # critical, warning, info
│   │   │   └── AlertStatus.ts     # triggered, acknowledged, resolved
│   │   │
│   │   └── constants/             # Global constants
│   │       ├── api.ts             # API_BASE_URL, endpoints
│   │       ├── pagination.ts      # PAGE_SIZE, MAX_PAGE_SIZE
│   │       └── routes.ts          # Route names
│   │
│   ├── api/                       # Backend communication layer
│   │   ├── client.ts              # Axios instance with interceptors
│   │   └── modules/               # Domain-specific API services
│   │       ├── deviceApi.ts       # Device CRUD operations
│   │       ├── alertApi.ts        # Alert management
│   │       ├── userApi.ts         # User profile and auth
│   │       ├── firmwareApi.ts     # Firmware management
│   │       └── analyticsApi.ts    # Analytics and reports
│   │
│   ├── composables/               # Reusable business logic (Vue Hooks)
│   │   ├── useDevices.ts          # Device list, CRUD operations
│   │   ├── useAlerts.ts           # Alert list, acknowledgment
│   │   ├── useAuth.ts             # Login, logout, auth state
│   │   ├── useWebSocket.ts        # Real-time updates
│   │   ├── usePagination.ts       # Pagination logic
│   │   └── useDebounce.ts         # Debounce utility
│   │
│   ├── components/                # Vue components
│   │   ├── base/                  # Dumb/Presentational components
│   │   │   ├── BaseButton.vue     # Reusable button
│   │   │   ├── BaseInput.vue      # Form input
│   │   │   ├── BaseCard.vue       # Card container
│   │   │   ├── BaseModal.vue      # Modal dialog
│   │   │   ├── BaseTable.vue      # Data table
│   │   │   └── BaseSpinner.vue    # Loading spinner
│   │   │
│   │   └── modules/               # Smart/Feature components
│   │       ├── DeviceCard.vue     # Device display card
│   │       ├── DeviceList.vue     # Device list with filters
│   │       ├── AlertCard.vue      # Alert display card
│   │       ├── AlertList.vue      # Alert list
│   │       ├── StatCard.vue       # Statistics card
│   │       └── SensorChart.vue    # Sensor data chart
│   │
│   ├── pages/                     # Route-level components
│   │   ├── Dashboard.vue          # Main dashboard
│   │   ├── DeviceList.vue         # Device management page
│   │   ├── DeviceDetails.vue      # Single device view
│   │   ├── AlertList.vue          # Alert management page
│   │   ├── Analytics.vue          # Analytics and reports
│   │   ├── Settings.vue           # User settings
│   │   └── Login.vue              # Login page
│   │
│   ├── store/                     # Pinia state management
│   │   ├── auth.ts                # Authentication state
│   │   ├── settings.ts            # App settings (theme, language)
│   │   └── notifications.ts       # Toast notifications
│   │
│   ├── router/                    # Vue Router configuration
│   │   └── index.ts               # Route definitions
│   │
│   ├── styles/                    # Global styles
│   │   ├── index.css              # Tailwind imports and custom styles
│   │   └── variables.css          # CSS custom properties
│   │
│   ├── assets/                    # Static assets
│   │   ├── images/                # Images
│   │   └── icons/                 # SVG icons
│   │
│   ├── App.vue                    # Root component
│   └── main.ts                    # Application entry point
│
├── public/                         # Static files (served as-is)
│   └── favicon.ico
│
├── package.json                    # Dependencies and scripts
├── vite.config.ts                  # Vite configuration
├── tsconfig.json                   # TypeScript root config
├── tsconfig.app.json               # TypeScript app config
├── tailwind.config.js              # Tailwind CSS config
└── CLAUDE.md                       # This file
```

---

## Development Workflow

### 1. Start Development Server

```bash
cd frontend
npm install                    # First time only
npm run dev                    # Start dev server on port 5173
```

**What happens:**
- Vite starts development server with HMR (Hot Module Replacement)
- TypeScript compilation in watch mode
- Tailwind CSS processing
- Auto-reload on file changes

### 2. Environment Setup

Create environment files:

**`.env.development`** (local development):
```bash
VITE_API_BASE_URL=http://localhost:3000
VITE_WS_URL=ws://localhost:3001
VITE_ENVIRONMENT=development
```

**`.env.production`** (production build):
```bash
VITE_API_BASE_URL=https://api.smart-iot.example.com
VITE_WS_URL=wss://ws.smart-iot.example.com
VITE_ENVIRONMENT=production
```

**Access environment variables:**
```typescript
const apiUrl = import.meta.env.VITE_API_BASE_URL;
```

### 3. Development Flow

1. **Make changes** to Vue files, TypeScript, or styles
2. **See updates** instantly in browser (HMR)
3. **Check console** for TypeScript errors
4. **Test manually** in browser
5. **Run type check** before committing: `npm run type-check`
6. **Build** before deploying: `npm run build`

---

## Architecture Patterns

### Layered Architecture

The frontend follows a **clean architecture** approach with clear layers:

```
┌──────────────────────────────────────┐
│         Pages (Routes)               │  ← User-facing views
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│         Components                   │  ← UI building blocks
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│       Composables (Logic)            │  ← Business logic
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│      API Services (HTTP)             │  ← Backend communication
└──────────────┬───────────────────────┘
               │
┌──────────────▼───────────────────────┐
│         API Client (Axios)           │  ← HTTP transport
└──────────────────────────────────────┘
```

### Data Flow

**Unidirectional data flow:**
```
User Action → Component → Composable → API Service → Backend
                  ↑                                      │
                  └──────────────────────────────────────┘
```

**Example:**
```
User clicks "Acknowledge Alert" button
  → AlertCard.vue emits event
    → Page component calls useAlerts().acknowledgeAlert(id)
      → useAlerts calls alertApi.acknowledge(id)
        → alertApi makes POST request to backend
          → Backend responds with updated alert
            → Composable updates reactive state
              → Component re-renders with new data
```

### Component Hierarchy

**Two types of components:**

1. **Base Components (Dumb/Presentational)**
   - No business logic
   - Accept data via props
   - Emit events for user actions
   - Highly reusable
   - Example: `BaseButton.vue`, `BaseCard.vue`

2. **Module Components (Smart/Container)**
   - Contain business logic
   - Use composables and stores
   - Fetch data
   - Handle user interactions
   - Example: `DeviceList.vue`, `AlertCard.vue`

---

## Common Tasks

### Task 1: Add a New API Endpoint

**Scenario:** Add endpoint to get device sensor history

**1. Define types in `core/types/device.ts`:**
```typescript
export interface SensorReading {
  timestamp: string;
  temperature?: number;
  humidity?: number;
  pressure?: number;
  [key: string]: any;
}

export interface SensorHistoryResponse {
  deviceId: string;
  readings: SensorReading[];
  nextToken?: string;
}
```

**2. Add API method in `api/modules/deviceApi.ts`:**
```typescript
import type { SensorHistoryResponse } from '@/core/types/device';
import apiClient from '../client';

export const deviceApi = {
  // ... existing methods

  /**
   * Get sensor history for a device
   * @param deviceId - Device ID
   * @param startTime - Start timestamp (ISO 8601)
   * @param endTime - End timestamp (ISO 8601)
   */
  async getSensorHistory(
    deviceId: string,
    startTime: string,
    endTime: string
  ): Promise<SensorHistoryResponse> {
    const response = await apiClient.get<SensorHistoryResponse>(
      `/devices/${deviceId}/history`,
      { params: { startTime, endTime } }
    );
    return response.data;
  }
};
```

**3. Create composable in `composables/useSensorHistory.ts`:**
```typescript
import { ref, computed } from 'vue';
import { deviceApi } from '@/api/modules/deviceApi';
import type { SensorReading } from '@/core/types/device';

export function useSensorHistory(deviceId: string) {
  const readings = ref<SensorReading[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const fetchHistory = async (startTime: string, endTime: string) => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await deviceApi.getSensorHistory(
        deviceId,
        startTime,
        endTime
      );
      readings.value = response.readings;
    } catch (err: any) {
      error.value = err.response?.data?.message || 'Failed to fetch history';
      console.error('Error fetching sensor history:', err);
    } finally {
      isLoading.value = false;
    }
  };

  // Computed properties
  const latestReading = computed(() => readings.value[0] || null);
  const hasData = computed(() => readings.value.length > 0);

  return {
    readings,
    isLoading,
    error,
    latestReading,
    hasData,
    fetchHistory
  };
}
```

**4. Use in component:**
```vue
<template>
  <div>
    <h2>Sensor History</h2>
    <div v-if="isLoading">Loading...</div>
    <div v-else-if="error" class="text-red-500">{{ error }}</div>
    <div v-else-if="hasData">
      <ul>
        <li v-for="reading in readings" :key="reading.timestamp">
          {{ reading.timestamp }}: {{ reading.temperature }}°C
        </li>
      </ul>
    </div>
    <div v-else>No data available</div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { useSensorHistory } from '@/composables/useSensorHistory';

const props = defineProps<{ deviceId: string }>();

const { readings, isLoading, error, hasData, fetchHistory } =
  useSensorHistory(props.deviceId);

onMounted(() => {
  const endTime = new Date().toISOString();
  const startTime = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString();
  fetchHistory(startTime, endTime);
});
</script>
```

### Task 2: Create a New Page Component

**Scenario:** Add a "Device Details" page

**1. Create type definition (if needed) in `core/types/device.ts`:**
```typescript
export interface DeviceDetails extends Device {
  location: {
    latitude: number;
    longitude: number;
    address: string;
  };
  connectivity: {
    lastSeen: string;
    ipAddress: string;
    signalStrength: number;
  };
  metrics: {
    uptime: number;
    dataPoints: number;
    alertCount: number;
  };
}
```

**2. Create page component `pages/DeviceDetails.vue`:**
```vue
<template>
  <div class="container mx-auto p-6">
    <!-- Header -->
    <div class="mb-6">
      <button @click="goBack" class="text-blue-500 hover:underline mb-2">
        ← Back to Devices
      </button>
      <h1 class="text-3xl font-bold">Device Details</h1>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center items-center h-64">
      <BaseSpinner />
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
      {{ error }}
    </div>

    <!-- Content -->
    <div v-else-if="device" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Device Info Card -->
      <BaseCard>
        <h2 class="text-xl font-semibold mb-4">Device Information</h2>
        <dl class="space-y-2">
          <div>
            <dt class="text-gray-500">Name</dt>
            <dd class="font-medium">{{ device.name }}</dd>
          </div>
          <div>
            <dt class="text-gray-500">Status</dt>
            <dd>
              <span
                class="px-2 py-1 rounded text-sm"
                :class="getStatusClass(device.status)"
              >
                {{ device.status }}
              </span>
            </dd>
          </div>
          <div>
            <dt class="text-gray-500">Type</dt>
            <dd>{{ device.type }}</dd>
          </div>
        </dl>
      </BaseCard>

      <!-- Location Card -->
      <BaseCard>
        <h2 class="text-xl font-semibold mb-4">Location</h2>
        <p>{{ device.location?.address || 'No location data' }}</p>
      </BaseCard>

      <!-- Metrics Card -->
      <BaseCard class="lg:col-span-2">
        <h2 class="text-xl font-semibold mb-4">Metrics</h2>
        <div class="grid grid-cols-3 gap-4">
          <StatCard label="Uptime" :value="`${device.metrics?.uptime || 0}%`" />
          <StatCard label="Data Points" :value="device.metrics?.dataPoints || 0" />
          <StatCard label="Alerts" :value="device.metrics?.alertCount || 0" />
        </div>
      </BaseCard>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useDeviceDetails } from '@/composables/useDeviceDetails';
import BaseCard from '@/components/base/BaseCard.vue';
import BaseSpinner from '@/components/base/BaseSpinner.vue';
import StatCard from '@/components/modules/StatCard.vue';
import type { DeviceStatus } from '@/core/enums/DeviceStatus';

const route = useRoute();
const router = useRouter();

const deviceId = computed(() => route.params.id as string);
const { device, isLoading, error } = useDeviceDetails(deviceId.value);

const goBack = () => {
  router.push({ name: 'DeviceList' });
};

const getStatusClass = (status: DeviceStatus) => {
  const classes: Record<DeviceStatus, string> = {
    online: 'bg-green-100 text-green-800',
    offline: 'bg-gray-100 text-gray-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800'
  };
  return classes[status] || '';
};
</script>
```

**3. Add route in `router/index.ts`:**
```typescript
import { createRouter, createWebHistory } from 'vue-router';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'Dashboard',
      component: () => import('@/pages/Dashboard.vue')
    },
    {
      path: '/devices',
      name: 'DeviceList',
      component: () => import('@/pages/DeviceList.vue')
    },
    {
      path: '/devices/:id',
      name: 'DeviceDetails',
      component: () => import('@/pages/DeviceDetails.vue'),
      props: true  // Pass route params as props
    }
    // ... other routes
  ]
});

export default router;
```

### Task 3: Add State Management with Pinia

**Scenario:** Create a notification store for toast messages

**1. Create store in `store/notifications.ts`:**
```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  duration?: number;  // Auto-dismiss after ms
}

export const useNotificationStore = defineStore('notifications', () => {
  // State
  const notifications = ref<Notification[]>([]);

  // Getters
  const hasNotifications = computed(() => notifications.value.length > 0);
  const activeNotifications = computed(() => notifications.value);

  // Actions
  const addNotification = (
    type: Notification['type'],
    message: string,
    duration = 5000
  ) => {
    const id = `notification-${Date.now()}-${Math.random()}`;
    const notification: Notification = { id, type, message, duration };

    notifications.value.push(notification);

    // Auto-dismiss
    if (duration > 0) {
      setTimeout(() => {
        removeNotification(id);
      }, duration);
    }
  };

  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex((n) => n.id === id);
    if (index !== -1) {
      notifications.value.splice(index, 1);
    }
  };

  const clearAll = () => {
    notifications.value = [];
  };

  // Convenience methods
  const success = (message: string, duration?: number) =>
    addNotification('success', message, duration);

  const error = (message: string, duration?: number) =>
    addNotification('error', message, duration);

  const warning = (message: string, duration?: number) =>
    addNotification('warning', message, duration);

  const info = (message: string, duration?: number) =>
    addNotification('info', message, duration);

  return {
    // State
    notifications,
    // Getters
    hasNotifications,
    activeNotifications,
    // Actions
    addNotification,
    removeNotification,
    clearAll,
    success,
    error,
    warning,
    info
  };
});
```

**2. Use in component:**
```vue
<script setup lang="ts">
import { useNotificationStore } from '@/store/notifications';

const notificationStore = useNotificationStore();

const handleSave = async () => {
  try {
    await deviceApi.updateDevice(deviceId, formData);
    notificationStore.success('Device updated successfully');
  } catch (error) {
    notificationStore.error('Failed to update device');
  }
};
</script>
```

**3. Create notification component `components/modules/NotificationToast.vue`:**
```vue
<template>
  <div class="fixed top-4 right-4 z-50 space-y-2">
    <TransitionGroup name="notification">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="px-4 py-3 rounded shadow-lg min-w-[300px]"
        :class="getNotificationClass(notification.type)"
      >
        <div class="flex items-center justify-between">
          <span>{{ notification.message }}</span>
          <button
            @click="removeNotification(notification.id)"
            class="ml-4 text-xl"
          >
            &times;
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useNotificationStore } from '@/store/notifications';
import type { Notification } from '@/store/notifications';

const store = useNotificationStore();
const notifications = computed(() => store.activeNotifications);
const removeNotification = store.removeNotification;

const getNotificationClass = (type: Notification['type']) => {
  const classes = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    warning: 'bg-yellow-500 text-white',
    info: 'bg-blue-500 text-white'
  };
  return classes[type];
};
</script>

<style scoped>
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100px);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100px);
}
</style>
```

---

## Code Conventions

### TypeScript Best Practices

**1. Always use types:**
```typescript
// ✅ Good
interface User {
  id: string;
  name: string;
  email: string;
}

const user: User = {
  id: '123',
  name: 'John Doe',
  email: 'john@example.com'
};

// ❌ Bad
const user = {
  id: '123',
  name: 'John Doe',
  email: 'john@example.com'
};
```

**2. Use type inference when obvious:**
```typescript
// ✅ Good - type inferred
const count = ref(0);  // Ref<number>
const name = ref('');  // Ref<string>

// ✅ Also good - explicit type
const user = ref<User | null>(null);

// ❌ Unnecessary
const count = ref<number>(0);
```

**3. Use enums for constants:**
```typescript
// ✅ Good
export enum DeviceStatus {
  Online = 'online',
  Offline = 'offline',
  Warning = 'warning',
  Error = 'error'
}

// ❌ Bad
const DEVICE_STATUS = {
  ONLINE: 'online',
  OFFLINE: 'offline',
  WARNING: 'warning',
  ERROR: 'error'
};
```

**4. Use proper null handling:**
```typescript
// ✅ Good
const device = ref<Device | null>(null);

if (device.value) {
  console.log(device.value.name);  // TypeScript knows device is not null
}

// ❌ Bad
const device = ref<Device>(null as any);
console.log(device.value!.name);  // Using ! is dangerous
```

### Vue Best Practices

**1. Always use Composition API with `<script setup>`:**
```vue
<!-- ✅ Good -->
<script setup lang="ts">
import { ref } from 'vue';

const count = ref(0);
const increment = () => count.value++;
</script>

<!-- ❌ Bad - Don't use Options API -->
<script lang="ts">
export default {
  data() {
    return { count: 0 };
  },
  methods: {
    increment() {
      this.count++;
    }
  }
};
</script>
```

**2. Define props and emits with TypeScript:**
```vue
<script setup lang="ts">
// Props
interface Props {
  title: string;
  count?: number;
  items: string[];
}

const props = withDefaults(defineProps<Props>(), {
  count: 0
});

// Emits
const emit = defineEmits<{
  update: [value: number];
  delete: [id: string];
}>();

// Use
emit('update', props.count + 1);
</script>
```

**3. Use computed for derived state:**
```typescript
// ✅ Good
const doubleCount = computed(() => count.value * 2);

// ❌ Bad - Don't duplicate state
const doubleCount = ref(0);
watch(count, (newCount) => {
  doubleCount.value = newCount * 2;
});
```

**4. Use composables for reusable logic:**
```typescript
// ✅ Good - Extract to composable
// composables/useCounter.ts
export function useCounter(initialValue = 0) {
  const count = ref(initialValue);
  const increment = () => count.value++;
  const decrement = () => count.value--;
  return { count, increment, decrement };
}

// Component
const { count, increment } = useCounter(10);

// ❌ Bad - Duplicate logic in components
const count = ref(0);
const increment = () => count.value++;
```

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `DeviceCard.vue`, `BaseButton.vue` |
| Composables | camelCase, use prefix | `useDevices.ts`, `useAuth.ts` |
| Types/Interfaces | PascalCase | `interface Device {}` |
| Enums | PascalCase | `enum DeviceStatus {}` |
| Variables/Functions | camelCase | `deviceId`, `fetchDevices()` |
| Constants | UPPER_SNAKE_CASE | `API_BASE_URL`, `MAX_RETRIES` |
| Files (non-component) | camelCase | `deviceApi.ts`, `pagination.ts` |

---

## Component Guidelines

### Base Components (Dumb/Presentational)

**Characteristics:**
- No API calls
- No business logic
- Accept data via props
- Emit events for user actions
- Highly reusable

**Example: BaseButton.vue**
```vue
<template>
  <button
    :type="type"
    :disabled="disabled || loading"
    :class="buttonClasses"
    @click="handleClick"
  >
    <span v-if="loading" class="spinner"></span>
    <slot v-else />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue';

interface Props {
  type?: 'button' | 'submit' | 'reset';
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
}

const props = withDefaults(defineProps<Props>(), {
  type: 'button',
  variant: 'primary',
  size: 'md',
  disabled: false,
  loading: false
});

const emit = defineEmits<{
  click: [event: MouseEvent];
}>();

const buttonClasses = computed(() => {
  const base = 'rounded font-medium transition-colors';

  const variants = {
    primary: 'bg-blue-500 text-white hover:bg-blue-600',
    secondary: 'bg-gray-200 text-gray-800 hover:bg-gray-300',
    danger: 'bg-red-500 text-white hover:bg-red-600'
  };

  const sizes = {
    sm: 'px-3 py-1 text-sm',
    md: 'px-4 py-2',
    lg: 'px-6 py-3 text-lg'
  };

  const disabled = props.disabled || props.loading ? 'opacity-50 cursor-not-allowed' : '';

  return `${base} ${variants[props.variant]} ${sizes[props.size]} ${disabled}`;
});

const handleClick = (event: MouseEvent) => {
  if (!props.disabled && !props.loading) {
    emit('click', event);
  }
};
</script>
```

### Module Components (Smart/Container)

**Characteristics:**
- Use composables
- Fetch data
- Handle business logic
- Use base components for UI

**Example: DeviceCard.vue**
```vue
<template>
  <BaseCard>
    <div class="flex items-center justify-between mb-4">
      <h3 class="text-lg font-semibold">{{ device.name }}</h3>
      <span
        class="px-2 py-1 rounded text-sm"
        :class="statusClass"
      >
        {{ device.status }}
      </span>
    </div>

    <dl class="space-y-2 mb-4">
      <div>
        <dt class="text-gray-500 text-sm">Type</dt>
        <dd>{{ device.type }}</dd>
      </div>
      <div>
        <dt class="text-gray-500 text-sm">Last Seen</dt>
        <dd>{{ formattedLastSeen }}</dd>
      </div>
    </dl>

    <div class="flex gap-2">
      <BaseButton
        size="sm"
        @click="handleViewDetails"
      >
        View Details
      </BaseButton>
      <BaseButton
        size="sm"
        variant="secondary"
        @click="handleEdit"
      >
        Edit
      </BaseButton>
    </div>
  </BaseCard>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { formatDistanceToNow } from 'date-fns';
import type { Device } from '@/core/types/device';
import BaseCard from '@/components/base/BaseCard.vue';
import BaseButton from '@/components/base/BaseButton.vue';

interface Props {
  device: Device;
}

const props = defineProps<Props>();
const emit = defineEmits<{
  edit: [device: Device];
}>();

const router = useRouter();

const statusClass = computed(() => {
  const classes = {
    online: 'bg-green-100 text-green-800',
    offline: 'bg-gray-100 text-gray-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800'
  };
  return classes[props.device.status] || '';
});

const formattedLastSeen = computed(() =>
  formatDistanceToNow(new Date(props.device.lastSeen), { addSuffix: true })
);

const handleViewDetails = () => {
  router.push({ name: 'DeviceDetails', params: { id: props.device.id } });
};

const handleEdit = () => {
  emit('edit', props.device);
};
</script>
```

---

## State Management

### When to Use Pinia Stores

**Use stores for:**
- Global application state (auth, settings)
- Shared state between components
- State that needs to persist

**Don't use stores for:**
- Component-local state
- Derived state (use computed instead)
- Temporary UI state

### Store Pattern

```typescript
import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useMyStore = defineStore('myStore', () => {
  // State (use ref)
  const items = ref<Item[]>([]);
  const isLoading = ref(false);

  // Getters (use computed)
  const itemCount = computed(() => items.value.length);
  const hasItems = computed(() => items.value.length > 0);

  // Actions (regular functions)
  const fetchItems = async () => {
    isLoading.value = true;
    try {
      items.value = await api.fetchItems();
    } finally {
      isLoading.value = false;
    }
  };

  const addItem = (item: Item) => {
    items.value.push(item);
  };

  return {
    // State
    items,
    isLoading,
    // Getters
    itemCount,
    hasItems,
    // Actions
    fetchItems,
    addItem
  };
});
```

---

## API Integration

### API Client Setup

**`api/client.ts`:**
```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor (add auth token)
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor (handle errors)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Redirect to login
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### Error Handling

**Consistent error handling in composables:**
```typescript
export function useDevices() {
  const devices = ref<Device[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const fetchDevices = async () => {
    isLoading.value = true;
    error.value = null;

    try {
      devices.value = await deviceApi.listDevices();
    } catch (err: any) {
      // Extract error message
      error.value = err.response?.data?.message || 'Failed to fetch devices';

      // Log for debugging
      console.error('Error fetching devices:', err);

      // Optional: Show notification
      // useNotificationStore().error(error.value);
    } finally {
      isLoading.value = false;
    }
  };

  return { devices, isLoading, error, fetchDevices };
}
```

---

## Styling Guidelines

### Tailwind CSS Usage

**Use utility classes in template:**
```vue
<template>
  <!-- ✅ Good - Tailwind utilities -->
  <div class="container mx-auto p-4">
    <h1 class="text-2xl font-bold mb-4">Title</h1>
    <button class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">
      Click Me
    </button>
  </div>
</template>
```

**Avoid custom CSS when Tailwind suffices:**
```vue
<!-- ❌ Bad -->
<template>
  <div class="my-container">
    <button class="my-button">Click Me</button>
  </div>
</template>

<style>
.my-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.my-button {
  padding: 0.5rem 1rem;
  background-color: #3b82f6;
  color: white;
  border-radius: 0.25rem;
}
</style>
```

**Use `@apply` for repeated patterns:**
```vue
<style scoped>
.btn {
  @apply px-4 py-2 rounded font-medium transition-colors;
}

.btn-primary {
  @apply bg-blue-500 text-white hover:bg-blue-600;
}
</style>
```

---

## Testing (To Be Implemented)

### Recommended Setup

**Install dependencies:**
```bash
npm install -D vitest @vue/test-utils happy-dom
npm install -D @vitest/ui  # Optional: UI for tests
```

**Configure Vitest in `vite.config.ts`:**
```typescript
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

**Add test scripts to `package.json`:**
```json
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

### Testing Patterns

**Test composables:**
```typescript
// composables/__tests__/useDevices.test.ts
import { describe, it, expect, vi } from 'vitest';
import { useDevices } from '../useDevices';
import { deviceApi } from '@/api/modules/deviceApi';

vi.mock('@/api/modules/deviceApi');

describe('useDevices', () => {
  it('fetches devices successfully', async () => {
    const mockDevices = [{ id: '1', name: 'Device 1' }];
    vi.mocked(deviceApi.listDevices).mockResolvedValue(mockDevices);

    const { devices, fetchDevices } = useDevices();
    await fetchDevices();

    expect(devices.value).toEqual(mockDevices);
  });
});
```

**Test components:**
```typescript
// components/__tests__/DeviceCard.test.ts
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';
import DeviceCard from '../DeviceCard.vue';

describe('DeviceCard', () => {
  it('renders device name', () => {
    const device = { id: '1', name: 'Test Device', status: 'online' };
    const wrapper = mount(DeviceCard, {
      props: { device }
    });

    expect(wrapper.text()).toContain('Test Device');
  });

  it('emits edit event', async () => {
    const device = { id: '1', name: 'Test Device', status: 'online' };
    const wrapper = mount(DeviceCard, {
      props: { device }
    });

    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted('edit')).toBeTruthy();
  });
});
```

---

## Performance Optimization

### Lazy Loading

**Route-level code splitting:**
```typescript
// router/index.ts
const routes = [
  {
    path: '/dashboard',
    component: () => import('@/pages/Dashboard.vue')  // Lazy loaded
  }
];
```

**Component lazy loading:**
```vue
<script setup lang="ts">
import { defineAsyncComponent } from 'vue';

const HeavyChart = defineAsyncComponent(() =>
  import('@/components/modules/HeavyChart.vue')
);
</script>
```

### Computed vs Watch

**Prefer computed for derived state:**
```typescript
// ✅ Good - Cached, only recomputes when dependencies change
const filteredDevices = computed(() =>
  devices.value.filter(d => d.status === filter.value)
);

// ❌ Bad - Runs on every change, duplicates state
const filteredDevices = ref<Device[]>([]);
watch([devices, filter], () => {
  filteredDevices.value = devices.value.filter(d => d.status === filter.value);
});
```

### Virtual Scrolling

For large lists (1000+ items), use virtual scrolling:
```bash
npm install vue-virtual-scroller
```

---

## Troubleshooting

### TypeScript Errors

**Problem:** Type errors in IDE
**Solution:**
```bash
npm run type-check  # Check all type errors
```

### Build Errors

**Problem:** Build fails with "out of memory"
**Solution:**
```bash
NODE_OPTIONS="--max_old_space_size=4096" npm run build
```

### Hot Reload Not Working

**Problem:** Changes don't reflect in browser
**Solution:**
1. Check Vite server is running
2. Clear browser cache
3. Restart dev server: `npm run dev`

### CORS Errors

**Problem:** API requests fail with CORS error
**Solution:**
1. Verify backend CORS configuration
2. Check `VITE_API_BASE_URL` is correct
3. Ensure backend is running

---

**Last Updated:** 2025-11-15
**Maintainer:** AI Assistant (Claude)

**See also:**
- Main CLAUDE.md in root directory
- backend/CLAUDE.md for backend development
- docs/04-FRONTEND-DESIGN.md for UI/UX specifications

import { DeviceStatus } from '../enums'

export interface DeviceLocation {
  lat: number
  lon: number
  address?: string
  building?: string
  floor?: string
  room?: string
}

export interface Connectivity {
  type: 'wifi' | 'cellular' | 'ethernet' | 'lora'
  rssi?: number
  quality?: number
  lastSeen?: string
}

export interface DeviceMetadata {
  manufacturer?: string
  model?: string
  serialNumber?: string
  firmwareVersion?: string
  hardwareVersion?: string
}

export interface Device {
  deviceId: string
  organizationId: string
  deviceType: string
  name: string
  description?: string
  status: DeviceStatus
  location: DeviceLocation
  connectivity: Connectivity
  metadata: DeviceMetadata
  tags?: string[]
  batteryLevel?: number
  lastHeartbeat?: string
  createdAt: string
  updatedAt: string
}

export interface SensorReading {
  deviceId: string
  metric: string
  value: number
  unit: string
  timestamp: string
}

export interface DeviceHealth {
  uptime: number
  dataQuality: number
  errorRate: number
  lastError?: string
}

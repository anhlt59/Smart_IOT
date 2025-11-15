import { DeploymentStrategy } from '../enums'

export interface FirmwareVersion {
  major: number
  minor: number
  patch: number
}

export interface Firmware {
  firmwareId: string
  version: string
  deviceTypes: string[]
  size: number
  checksum: string
  changelog?: string
  releaseNotes?: string
  uploadedBy: string
  uploadedAt: string
  deprecated: boolean
  url?: string
}

export enum DeploymentStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled',
}

export interface DeploymentBatch {
  batchId: string
  deviceIds: string[]
  startedAt?: string
  completedAt?: string
  successCount: number
  failedCount: number
  pendingCount: number
}

export interface Deployment {
  deploymentId: string
  firmwareId: string
  firmwareVersion: string
  strategy: DeploymentStrategy
  targetDevices: string[]
  batches: DeploymentBatch[]
  status: DeploymentStatus
  progress: number
  successCount: number
  failedCount: number
  pendingCount: number
  createdBy: string
  createdAt: string
  startedAt?: string
  completedAt?: string
  scheduledFor?: string
}

export interface DeploymentLog {
  deviceId: string
  status: 'success' | 'failed' | 'pending'
  message?: string
  timestamp: string
}

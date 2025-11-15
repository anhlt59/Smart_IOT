import { AlertSeverity } from '../enums'

export enum AlertStatus {
  TRIGGERED = 'triggered',
  ACKNOWLEDGED = 'acknowledged',
  RESOLVED = 'resolved',
}

export interface AlertCondition {
  metric: string
  operator: '>' | '<' | '==' | '!=' | '>=' | '<='
  threshold: number
  duration?: number
}

export interface Alert {
  alertId: string
  ruleId: string
  deviceId: string
  deviceName?: string
  deviceLocation?: string
  severity: AlertSeverity
  status: AlertStatus
  title: string
  message: string
  condition: AlertCondition
  actualValue: number
  triggeredAt: string
  acknowledgedAt?: string
  acknowledgedBy?: string
  resolvedAt?: string
  resolvedBy?: string
  notes?: string[]
}

export interface AlertRule {
  ruleId: string
  name: string
  description?: string
  condition: AlertCondition
  severity: AlertSeverity
  targetDevices: string[] | 'all'
  deviceTypes?: string[]
  enabled: boolean
  notificationChannels: ('email' | 'push' | 'sms')[]
  cooldownPeriod?: number
  schedule?: {
    type: 'always' | 'business_hours' | 'custom'
    customSchedule?: string
  }
  createdAt: string
  updatedAt: string
}

export interface AlertStats {
  total: number
  critical: number
  warning: number
  info: number
  triggered: number
  acknowledged: number
  resolved: number
}

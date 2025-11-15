export interface DashboardStats {
  totalDevices: number
  onlineDevices: number
  offlineDevices: number
  maintenanceDevices: number
  activeAlerts: number
  criticalAlerts: number
  warningAlerts: number
  infoAlerts: number
  dataVolume: number
  deviceHealthAvg: number
}

export interface ChartDataPoint {
  timestamp: string
  value: number
  label?: string
}

export interface ChartData {
  labels: string[]
  datasets: {
    label: string
    data: number[]
    borderColor?: string
    backgroundColor?: string
    fill?: boolean
  }[]
}

export interface QueryParams {
  devices: string[]
  metrics: string[]
  startTime: string
  endTime: string
  aggregation?: 'avg' | 'min' | 'max' | 'sum'
  groupBy?: 'device' | 'time' | 'metric'
  interval?: '5m' | '15m' | '1h' | '6h' | '1d'
}

export interface QueryResult {
  data: ChartDataPoint[]
  metadata: {
    totalPoints: number
    queryTime: number
    fromCache: boolean
  }
}

export interface Report {
  reportId: string
  name: string
  type: string
  parameters: Record<string, any>
  generatedAt: string
  generatedBy: string
  url?: string
}

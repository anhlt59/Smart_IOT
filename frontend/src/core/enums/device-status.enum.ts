export enum DeviceStatus {
  ONLINE = 'online',
  OFFLINE = 'offline',
  MAINTENANCE = 'maintenance',
  ERROR = 'error',
}

export const DeviceStatusLabels: Record<DeviceStatus, string> = {
  [DeviceStatus.ONLINE]: 'Online',
  [DeviceStatus.OFFLINE]: 'Offline',
  [DeviceStatus.MAINTENANCE]: 'Maintenance',
  [DeviceStatus.ERROR]: 'Error',
}

export const DeviceStatusColors: Record<DeviceStatus, string> = {
  [DeviceStatus.ONLINE]: 'success',
  [DeviceStatus.OFFLINE]: 'danger',
  [DeviceStatus.MAINTENANCE]: 'warning',
  [DeviceStatus.ERROR]: 'danger',
}

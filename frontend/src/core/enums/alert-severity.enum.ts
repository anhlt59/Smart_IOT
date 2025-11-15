export enum AlertSeverity {
  INFO = 'info',
  WARNING = 'warning',
  CRITICAL = 'critical',
}

export const AlertSeverityLabels: Record<AlertSeverity, string> = {
  [AlertSeverity.INFO]: 'Info',
  [AlertSeverity.WARNING]: 'Warning',
  [AlertSeverity.CRITICAL]: 'Critical',
}

export const AlertSeverityColors: Record<AlertSeverity, string> = {
  [AlertSeverity.INFO]: 'primary',
  [AlertSeverity.WARNING]: 'warning',
  [AlertSeverity.CRITICAL]: 'danger',
}

export const AlertSeverityIcons: Record<AlertSeverity, string> = {
  [AlertSeverity.INFO]: 'ℹ️',
  [AlertSeverity.WARNING]: '⚠️',
  [AlertSeverity.CRITICAL]: '🔴',
}

export enum DeploymentStrategy {
  ALL_AT_ONCE = 'all_at_once',
  CANARY = 'canary',
  STAGED = 'staged',
}

export const DeploymentStrategyLabels: Record<DeploymentStrategy, string> = {
  [DeploymentStrategy.ALL_AT_ONCE]: 'All at Once',
  [DeploymentStrategy.CANARY]: 'Canary',
  [DeploymentStrategy.STAGED]: 'Staged',
}

export const DeploymentStrategyDescriptions: Record<DeploymentStrategy, string> = {
  [DeploymentStrategy.ALL_AT_ONCE]: 'Deploy to all devices simultaneously',
  [DeploymentStrategy.CANARY]: 'Deploy to a small percentage first, then roll out to all',
  [DeploymentStrategy.STAGED]: 'Deploy in multiple configurable batches',
}

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  VIEWER = 'viewer',
}

export const UserRoleLabels: Record<UserRole, string> = {
  [UserRole.ADMIN]: 'Administrator',
  [UserRole.USER]: 'User',
  [UserRole.VIEWER]: 'Viewer',
}

export const UserRolePermissions: Record<UserRole, string[]> = {
  [UserRole.ADMIN]: ['read', 'write', 'delete', 'manage_users', 'manage_settings'],
  [UserRole.USER]: ['read', 'write'],
  [UserRole.VIEWER]: ['read'],
}

"""User Entity"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class UserRole(Enum):
    """User roles"""
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


@dataclass
class UserPreferences:
    """User preferences value object"""
    notifications: Dict = field(default_factory=lambda: {
        'email': True,
        'push': True,
        'sms': False
    })
    quiet_hours: Dict = field(default_factory=lambda: {
        'enabled': False,
        'start': '22:00',
        'end': '08:00',
        'timezone': 'UTC'
    })
    subscribed_devices: List[str] = field(default_factory=list)
    dashboard_layout: Dict = field(default_factory=dict)
    theme: str = 'light'
    language: str = 'en'

    def to_dict(self) -> Dict:
        return {
            'notifications': self.notifications,
            'quietHours': self.quiet_hours,
            'subscribedDevices': self.subscribed_devices,
            'dashboardLayout': self.dashboard_layout,
            'theme': self.theme,
            'language': self.language
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'UserPreferences':
        return cls(
            notifications=data.get('notifications', {}),
            quiet_hours=data.get('quietHours', {}),
            subscribed_devices=data.get('subscribedDevices', []),
            dashboard_layout=data.get('dashboardLayout', {}),
            theme=data.get('theme', 'light'),
            language=data.get('language', 'en')
        )


@dataclass
class User:
    """User Entity"""
    user_id: str
    email: str
    organization_id: str
    role: UserRole
    preferences: UserPreferences
    device_tokens: List[str] = field(default_factory=list)
    name: Optional[str] = None
    phone_number: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def has_permission(self, resource: str, action: str) -> bool:
        """Check if user has permission for action on resource"""
        # Super admin has all permissions
        if self.role == UserRole.SUPER_ADMIN:
            return True

        # Org admin has all permissions within organization
        if self.role == UserRole.ORG_ADMIN:
            return True

        # Operator can read and update
        if self.role == UserRole.OPERATOR:
            return action in ['read', 'update']

        # Viewer can only read
        if self.role == UserRole.VIEWER:
            return action == 'read'

        return False

    def can_receive_notification(self, channel: str) -> bool:
        """Check if user can receive notification on channel"""
        return self.preferences.notifications.get(channel, False)

    def add_device_token(self, token: str):
        """Add device token for push notifications"""
        if token not in self.device_tokens:
            self.device_tokens.append(token)
            self.updated_at = datetime.utcnow()

    def remove_device_token(self, token: str):
        """Remove device token"""
        if token in self.device_tokens:
            self.device_tokens.remove(token)
            self.updated_at = datetime.utcnow()

    def to_dict(self) -> Dict:
        return {
            'userId': self.user_id,
            'email': self.email,
            'name': self.name,
            'organizationId': self.organization_id,
            'role': self.role.value,
            'preferences': self.preferences.to_dict(),
            'deviceTokens': self.device_tokens,
            'phoneNumber': self.phone_number,
            'createdAt': int(self.created_at.timestamp() * 1000) if self.created_at else None,
            'updatedAt': int(self.updated_at.timestamp() * 1000) if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'User':
        return cls(
            user_id=data['userId'],
            email=data['email'],
            name=data.get('name'),
            organization_id=data['organizationId'],
            role=UserRole(data['role']),
            preferences=UserPreferences.from_dict(data.get('preferences', {})),
            device_tokens=data.get('deviceTokens', []),
            phone_number=data.get('phoneNumber'),
            created_at=datetime.fromtimestamp(data['createdAt'] / 1000) if data.get('createdAt') else None,
            updated_at=datetime.fromtimestamp(data['updatedAt'] / 1000) if data.get('updatedAt') else None
        )

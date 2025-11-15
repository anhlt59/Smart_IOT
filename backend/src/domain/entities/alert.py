"""Alert Entity - Represents a triggered alert"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertStatus(Enum):
    """Alert status"""
    TRIGGERED = "triggered"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


@dataclass
class Alert:
    """Alert Entity - Represents a triggered alert"""
    alert_id: str
    rule_id: str
    device_id: str
    organization_id: str
    severity: AlertSeverity
    status: AlertStatus
    condition: str
    actual_value: float
    threshold: float
    timestamp: datetime
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    notifications_sent: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)

    def can_acknowledge(self, user_id: str) -> bool:
        """Check if alert can be acknowledged by user"""
        if self.status != AlertStatus.TRIGGERED:
            return False
        return True

    def acknowledge(self, user_id: str):
        """Acknowledge the alert"""
        self.status = AlertStatus.ACKNOWLEDGED
        self.acknowledged_by = user_id
        self.acknowledged_at = datetime.utcnow()

    def resolve(self, resolution_note: Optional[str] = None):
        """Resolve the alert"""
        if self.status != AlertStatus.ACKNOWLEDGED:
            raise ValueError("Alert must be acknowledged before resolution")

        self.status = AlertStatus.RESOLVED
        self.resolved_at = datetime.utcnow()

        if resolution_note:
            self.metadata['resolution'] = resolution_note

    def should_escalate(self) -> bool:
        """Check if alert should be escalated"""
        if self.severity != AlertSeverity.CRITICAL:
            return False

        if self.status == AlertStatus.TRIGGERED and self.acknowledged_at is None:
            # Critical alert not acknowledged within 15 minutes
            time_since_trigger = (datetime.utcnow() - self.timestamp).total_seconds()
            return time_since_trigger > 900  # 15 minutes

        return False

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'alertId': self.alert_id,
            'ruleId': self.rule_id,
            'deviceId': self.device_id,
            'organizationId': self.organization_id,
            'severity': self.severity.value,
            'status': self.status.value,
            'condition': self.condition,
            'actualValue': self.actual_value,
            'threshold': self.threshold,
            'timestamp': int(self.timestamp.timestamp() * 1000),
            'acknowledgedBy': self.acknowledged_by,
            'acknowledgedAt': int(self.acknowledged_at.timestamp() * 1000) if self.acknowledged_at else None,
            'resolvedAt': int(self.resolved_at.timestamp() * 1000) if self.resolved_at else None,
            'notificationsSent': self.notifications_sent,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Alert':
        """Create from dictionary"""
        return cls(
            alert_id=data['alertId'],
            rule_id=data['ruleId'],
            device_id=data['deviceId'],
            organization_id=data['organizationId'],
            severity=AlertSeverity(data['severity']),
            status=AlertStatus(data['status']),
            condition=data['condition'],
            actual_value=data['actualValue'],
            threshold=data['threshold'],
            timestamp=datetime.fromtimestamp(data['timestamp'] / 1000),
            acknowledged_by=data.get('acknowledgedBy'),
            acknowledged_at=datetime.fromtimestamp(data['acknowledgedAt'] / 1000) if data.get('acknowledgedAt') else None,
            resolved_at=datetime.fromtimestamp(data['resolvedAt'] / 1000) if data.get('resolvedAt') else None,
            notifications_sent=data.get('notificationsSent', []),
            metadata=data.get('metadata', {})
        )

"""Alert Rule Entity"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from datetime import datetime
from .alert import AlertSeverity


@dataclass
class AlertCondition:
    """Alert condition value object"""
    metric: str  # temperature, humidity, co2, etc.
    operator: str  # >, <, >=, <=, ==
    threshold: float
    duration: int  # seconds, sustained condition

    def evaluate(self, value: float) -> bool:
        """Evaluate condition against a value"""
        operators = {
            '>': lambda x, y: x > y,
            '<': lambda x, y: x < y,
            '>=': lambda x, y: x >= y,
            '<=': lambda x, y: x <= y,
            '==': lambda x, y: x == y
        }
        return operators[self.operator](value, self.threshold)

    def to_dict(self) -> Dict:
        return {
            'metric': self.metric,
            'operator': self.operator,
            'threshold': self.threshold,
            'duration': self.duration
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'AlertCondition':
        return cls(
            metric=data['metric'],
            operator=data['operator'],
            threshold=data['threshold'],
            duration=data['duration']
        )


@dataclass
class AlertRule:
    """Alert Rule Entity"""
    rule_id: str
    organization_id: str
    name: str
    description: str
    device_type: str
    device_ids: List[str]
    condition: AlertCondition
    severity: AlertSeverity
    status: str  # active|inactive
    cooldown_period: int  # seconds
    actions: Dict
    created_by: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    def is_applicable_to(self, device_id: str, device_type: str) -> bool:
        """Check if rule applies to a device"""
        # Check device type
        if self.device_type != 'all' and self.device_type != device_type:
            return False

        # Check specific devices if specified
        if self.device_ids and device_id not in self.device_ids:
            return False

        return True

    def evaluate(self, sensor_data: Dict) -> bool:
        """Evaluate rule against sensor data"""
        if self.status != 'active':
            return False

        metric_value = sensor_data.get(self.condition.metric)
        if metric_value is None:
            return False

        return self.condition.evaluate(metric_value)

    def to_dict(self) -> Dict:
        return {
            'ruleId': self.rule_id,
            'organizationId': self.organization_id,
            'name': self.name,
            'description': self.description,
            'deviceType': self.device_type,
            'deviceIds': self.device_ids,
            'condition': self.condition.to_dict(),
            'severity': self.severity.value,
            'status': self.status,
            'cooldownPeriod': self.cooldown_period,
            'actions': self.actions,
            'createdBy': self.created_by,
            'createdAt': int(self.created_at.timestamp() * 1000),
            'updatedAt': int(self.updated_at.timestamp() * 1000) if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'AlertRule':
        return cls(
            rule_id=data['ruleId'],
            organization_id=data['organizationId'],
            name=data['name'],
            description=data['description'],
            device_type=data['deviceType'],
            device_ids=data.get('deviceIds', []),
            condition=AlertCondition.from_dict(data['condition']),
            severity=AlertSeverity(data['severity']),
            status=data['status'],
            cooldown_period=data['cooldownPeriod'],
            actions=data.get('actions', {}),
            created_by=data['createdBy'],
            created_at=datetime.fromtimestamp(data['createdAt'] / 1000),
            updated_at=datetime.fromtimestamp(data['updatedAt'] / 1000) if data.get('updatedAt') else None
        )

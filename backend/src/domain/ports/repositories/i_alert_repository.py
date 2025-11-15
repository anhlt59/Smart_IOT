"""Alert Repository Interface"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from ...entities.alert import Alert
from ...entities.alert_rule import AlertRule


class IAlertRepository(ABC):
    """Interface for alert data access"""

    @abstractmethod
    def save_alert(self, alert: Alert) -> Alert:
        """Save alert"""
        pass

    @abstractmethod
    def find_alert_by_id(self, alert_id: str) -> Optional[Alert]:
        """Find alert by ID"""
        pass

    @abstractmethod
    def find_alerts(
        self,
        organization_id: str,
        filters: Optional[Dict] = None,
        page: int = 1,
        page_size: int = 25
    ) -> Dict:
        """Find alerts with filters and pagination"""
        pass

    @abstractmethod
    def update_alert(self, alert_id: str, updates: Dict) -> Alert:
        """Update alert"""
        pass

    @abstractmethod
    def save_rule(self, rule: AlertRule) -> AlertRule:
        """Save alert rule"""
        pass

    @abstractmethod
    def find_rule_by_id(self, rule_id: str) -> Optional[AlertRule]:
        """Find alert rule by ID"""
        pass

    @abstractmethod
    def find_active_rules(self, organization_id: str) -> List[AlertRule]:
        """Find all active alert rules"""
        pass

    @abstractmethod
    def update_rule(self, rule_id: str, updates: Dict) -> AlertRule:
        """Update alert rule"""
        pass

    @abstractmethod
    def delete_rule(self, rule_id: str) -> bool:
        """Delete alert rule"""
        pass

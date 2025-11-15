"""Device Repository Interface - Port for hexagonal architecture"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from ...entities.device import Device


class IDeviceRepository(ABC):
    """Interface for device data access"""

    @abstractmethod
    def save(self, device: Device) -> Device:
        """Save device to storage"""
        pass

    @abstractmethod
    def find_by_id(self, device_id: str) -> Optional[Device]:
        """Find device by ID"""
        pass

    @abstractmethod
    def find_by_organization(
        self,
        organization_id: str,
        filters: Optional[Dict] = None,
        page: int = 1,
        page_size: int = 25
    ) -> Dict:
        """
        Find devices by organization with pagination

        Returns:
            {
                'items': List[Device],
                'pagination': {
                    'page': int,
                    'pageSize': int,
                    'totalItems': int,
                    'totalPages': int
                }
            }
        """
        pass

    @abstractmethod
    def update(self, device_id: str, updates: Dict) -> Device:
        """Update device attributes"""
        pass

    @abstractmethod
    def delete(self, device_id: str) -> bool:
        """Delete device"""
        pass

    @abstractmethod
    def update_last_reading(self, device_id: str, reading: Dict):
        """Update device's last reading"""
        pass

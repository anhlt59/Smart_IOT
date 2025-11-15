"""Firmware Repository Interface"""
from abc import ABC, abstractmethod
from typing import List, Optional
from ...entities.firmware import Firmware
from ...entities.deployment import Deployment


class IFirmwareRepository(ABC):
    """Interface for firmware data access"""

    @abstractmethod
    def save_firmware(self, firmware: Firmware) -> Firmware:
        """Save firmware"""
        pass

    @abstractmethod
    def find_firmware_by_id(self, firmware_id: str) -> Optional[Firmware]:
        """Find firmware by ID"""
        pass

    @abstractmethod
    def find_all_firmware(self, device_type: Optional[str] = None) -> List[Firmware]:
        """Find all firmware, optionally filtered by device type"""
        pass

    @abstractmethod
    def save_deployment(self, deployment: Deployment) -> Deployment:
        """Save deployment"""
        pass

    @abstractmethod
    def find_deployment_by_id(self, deployment_id: str) -> Optional[Deployment]:
        """Find deployment by ID"""
        pass

    @abstractmethod
    def find_deployments_by_firmware(self, firmware_id: str) -> List[Deployment]:
        """Find all deployments for a firmware"""
        pass

    @abstractmethod
    def update_deployment(self, deployment_id: str, updates: dict) -> Deployment:
        """Update deployment"""
        pass

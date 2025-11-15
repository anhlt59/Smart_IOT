"""Device Entity - Core business object representing an IoT device"""
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime
from enum import Enum


class DeviceStatus(str, Enum):
    """Device status enumeration"""
    ONLINE = "online"
    OFFLINE = "offline"
    MAINTENANCE = "maintenance"
    REGISTERED = "registered"
    DELETED = "deleted"


class DeviceLocation(BaseModel):
    """Device location value object"""
    lat: float
    lon: float
    address: str

    class Config:
        json_schema_extra = {
            "example": {
                "lat": 37.7749,
                "lon": -122.4194,
                "address": "Office 301, Building A"
            }
        }


class Connectivity(BaseModel):
    """Device connectivity information"""
    type: str  # wifi|cellular|lorawan
    sim_id: Optional[str] = Field(None, alias='simId')
    ip_address: Optional[str] = Field(None, alias='ipAddress')
    signal_strength: Optional[int] = Field(None, alias='signalStrength')

    class Config:
        populate_by_name = True


class Device(BaseModel):
    """Device Entity - Represents an IoT device in the system"""
    device_id: str = Field(..., alias='deviceId')
    organization_id: str = Field(..., alias='organizationId')
    device_type: str = Field(..., alias='deviceType')
    name: str
    status: DeviceStatus
    location: DeviceLocation
    connectivity: Connectivity
    firmware_version: Optional[str] = Field(None, alias='firmwareVersion')
    last_seen: Optional[datetime] = Field(None, alias='lastSeen')
    last_reading: Optional[Dict] = Field(default_factory=dict, alias='lastReading')
    metadata: Optional[Dict] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    created_at: Optional[datetime] = Field(None, alias='createdAt')
    updated_at: Optional[datetime] = Field(None, alias='updatedAt')

    class Config:
        populate_by_name = True
        use_enum_values = False

    def is_online(self) -> bool:
        """Check if device is currently online"""
        if self.status != DeviceStatus.ONLINE:
            return False

        if self.last_seen is None:
            return False

        # Device is considered offline if not seen in last 5 minutes
        time_diff = (datetime.utcnow() - self.last_seen).total_seconds()
        return time_diff < 300  # 5 minutes

    def needs_update(self, target_firmware_version: str) -> bool:
        """Check if device needs firmware update"""
        if self.firmware_version is None:
            return True
        return self.firmware_version != target_firmware_version

    def update_last_reading(self, reading: Dict):
        """Update the last sensor reading"""
        self.last_reading = reading
        self.last_seen = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def set_status(self, status: DeviceStatus):
        """Update device status"""
        self.status = status
        self.updated_at = datetime.utcnow()

    def to_dynamodb_item(self) -> Dict:
        """Convert to DynamoDB item format"""
        data = self.model_dump(by_alias=True)
        # Convert datetime to timestamp
        if self.last_seen:
            data['lastSeen'] = int(self.last_seen.timestamp() * 1000)
        if self.created_at:
            data['createdAt'] = int(self.created_at.timestamp() * 1000)
        if self.updated_at:
            data['updatedAt'] = int(self.updated_at.timestamp() * 1000)
        data['status'] = self.status.value
        return data

    @classmethod
    def from_dynamodb_item(cls, item: Dict) -> 'Device':
        """Create entity from DynamoDB item"""
        # Convert timestamps to datetime
        if item.get('lastSeen'):
            item['lastSeen'] = datetime.fromtimestamp(item['lastSeen'] / 1000)
        if item.get('createdAt'):
            item['createdAt'] = datetime.fromtimestamp(item['createdAt'] / 1000)
        if item.get('updatedAt'):
            item['updatedAt'] = datetime.fromtimestamp(item['updatedAt'] / 1000)
        return cls(**item)

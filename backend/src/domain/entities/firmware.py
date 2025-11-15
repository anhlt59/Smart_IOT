"""Firmware Entity"""
from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime


@dataclass
class FirmwareVersion:
    """Firmware version value object"""
    major: int
    minor: int
    patch: int

    def __lt__(self, other: 'FirmwareVersion') -> bool:
        return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

    def __eq__(self, other) -> bool:
        return (self.major, self.minor, self.patch) == (other.major, other.minor, other.patch)

    def __str__(self) -> str:
        return f"v{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def from_string(cls, version_str: str) -> 'FirmwareVersion':
        """Parse version string like 'v2.1.0' or '2.1.0'"""
        version_str = version_str.lstrip('v')
        parts = version_str.split('.')
        return cls(int(parts[0]), int(parts[1]), int(parts[2]))


@dataclass
class Firmware:
    """Firmware Entity"""
    firmware_id: str
    version: FirmwareVersion
    device_types: List[str]
    s3_bucket: str
    s3_key: str
    checksum: str
    size: int
    status: str  # available|deprecated|withdrawn
    changelog: str = ""
    uploaded_by: str = ""
    uploaded_at: datetime = None
    metadata: Dict = field(default_factory=dict)

    def is_compatible_with(self, device_type: str) -> bool:
        """Check if firmware is compatible with device type"""
        return device_type in self.device_types

    def to_dict(self) -> Dict:
        return {
            'firmwareId': self.firmware_id,
            'version': str(self.version),
            'deviceTypes': self.device_types,
            's3Bucket': self.s3_bucket,
            's3Key': self.s3_key,
            'checksum': self.checksum,
            'size': self.size,
            'status': self.status,
            'changelog': self.changelog,
            'uploadedBy': self.uploaded_by,
            'uploadedAt': int(self.uploaded_at.timestamp() * 1000) if self.uploaded_at else None,
            'metadata': self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Firmware':
        return cls(
            firmware_id=data['firmwareId'],
            version=FirmwareVersion.from_string(data['version']),
            device_types=data['deviceTypes'],
            s3_bucket=data['s3Bucket'],
            s3_key=data['s3Key'],
            checksum=data['checksum'],
            size=data['size'],
            status=data['status'],
            changelog=data.get('changelog', ''),
            uploaded_by=data.get('uploadedBy', ''),
            uploaded_at=datetime.fromtimestamp(data['uploadedAt'] / 1000) if data.get('uploadedAt') else None,
            metadata=data.get('metadata', {})
        )

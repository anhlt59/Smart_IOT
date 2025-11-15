"""Deployment Entity"""
from dataclasses import dataclass, field
from typing import Dict, List
from datetime import datetime


@dataclass
class DeploymentBatch:
    """Deployment batch value object"""
    batch_id: int
    devices: List[str]
    status: str  # pending|in_progress|completed|failed
    success_count: int = 0
    failure_count: int = 0

    def calculate_success_rate(self) -> float:
        """Calculate batch success rate"""
        total = self.success_count + self.failure_count
        return (self.success_count / total * 100) if total > 0 else 0.0

    def to_dict(self) -> Dict:
        return {
            'batchId': self.batch_id,
            'devices': self.devices,
            'status': self.status,
            'successCount': self.success_count,
            'failureCount': self.failure_count
        }


@dataclass
class Deployment:
    """Deployment Entity"""
    deployment_id: str
    firmware_id: str
    strategy: str  # all-at-once|canary|staged
    target_devices: List[str]
    status: str  # scheduled|in_progress|completed|failed|rolled_back
    batches: List[DeploymentBatch] = field(default_factory=list)
    progress: Dict = field(default_factory=lambda: {
        'total': 0,
        'succeeded': 0,
        'failed': 0,
        'inProgress': 0,
        'pending': 0
    })
    scheduled_at: datetime = None
    started_at: datetime = None
    completed_at: datetime = None
    created_by: str = ""
    created_at: datetime = None

    def can_proceed_to_next_batch(self, success_threshold: float = 95.0) -> bool:
        """Check if deployment can proceed to next batch"""
        if not self.batches:
            return True

        # Get last completed batch
        completed_batches = [b for b in self.batches if b.status == 'completed']
        if not completed_batches:
            return True

        last_batch = completed_batches[-1]
        success_rate = last_batch.calculate_success_rate()

        return success_rate >= success_threshold

    def calculate_overall_success_rate(self) -> float:
        """Calculate overall deployment success rate"""
        total = self.progress['succeeded'] + self.progress['failed']
        return (self.progress['succeeded'] / total * 100) if total > 0 else 0.0

    def update_progress(self):
        """Update deployment progress from batches"""
        self.progress['total'] = len(self.target_devices)
        self.progress['succeeded'] = sum(b.success_count for b in self.batches)
        self.progress['failed'] = sum(b.failure_count for b in self.batches)

        in_progress_batches = [b for b in self.batches if b.status == 'in_progress']
        self.progress['inProgress'] = len(in_progress_batches)

        pending_batches = [b for b in self.batches if b.status == 'pending']
        self.progress['pending'] = sum(len(b.devices) for b in pending_batches)

    def to_dict(self) -> Dict:
        return {
            'deploymentId': self.deployment_id,
            'firmwareId': self.firmware_id,
            'strategy': self.strategy,
            'targetDevices': self.target_devices,
            'status': self.status,
            'batches': [b.to_dict() for b in self.batches],
            'progress': self.progress,
            'scheduledAt': int(self.scheduled_at.timestamp() * 1000) if self.scheduled_at else None,
            'startedAt': int(self.started_at.timestamp() * 1000) if self.started_at else None,
            'completedAt': int(self.completed_at.timestamp() * 1000) if self.completed_at else None,
            'createdBy': self.created_by,
            'createdAt': int(self.created_at.timestamp() * 1000) if self.created_at else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Deployment':
        return cls(
            deployment_id=data['deploymentId'],
            firmware_id=data['firmwareId'],
            strategy=data['strategy'],
            target_devices=data['targetDevices'],
            status=data['status'],
            batches=[DeploymentBatch(**b) for b in data.get('batches', [])],
            progress=data.get('progress', {}),
            scheduled_at=datetime.fromtimestamp(data['scheduledAt'] / 1000) if data.get('scheduledAt') else None,
            started_at=datetime.fromtimestamp(data['startedAt'] / 1000) if data.get('startedAt') else None,
            completed_at=datetime.fromtimestamp(data['completedAt'] / 1000) if data.get('completedAt') else None,
            created_by=data.get('createdBy', ''),
            created_at=datetime.fromtimestamp(data['createdAt'] / 1000) if data.get('createdAt') else None
        )

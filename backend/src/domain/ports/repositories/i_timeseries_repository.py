"""Time Series Repository Interface"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime


class ITimeSeriesRepository(ABC):
    """Interface for time-series data access (Timestream)"""

    @abstractmethod
    def write_sensor_data(self, device_id: str, data: Dict, timestamp: datetime) -> bool:
        """Write sensor data to time-series database"""
        pass

    @abstractmethod
    def query_recent_data(
        self,
        device_id: str,
        metric: str,
        time_range_minutes: int = 5
    ) -> List[Dict]:
        """Query recent sensor data"""
        pass

    @abstractmethod
    def query_aggregated_data(
        self,
        device_id: str,
        metrics: List[str],
        start_time: datetime,
        end_time: datetime,
        aggregation_interval: str = '15m'
    ) -> List[Dict]:
        """Query aggregated sensor data"""
        pass

    @abstractmethod
    def query_multiple_devices(
        self,
        device_ids: List[str],
        metrics: List[str],
        start_time: datetime,
        end_time: datetime
    ) -> Dict:
        """Query data for multiple devices"""
        pass

"""
H Module - Telemetry Data Model
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Telemetry data model for real-time data collection and processing
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TelemetrySource(Enum):
    """Source of telemetry data"""
    GPS = "gps"
    IMU = "imu"
    ENGINE = "engine"
    FUEL = "fuel"
    ELECTRICAL = "electrical"
    HYDRAULIC = "hydraulic"
    CAMERA = "camera"
    SENSOR = "sensor"
    MANUAL = "manual"


class DataQuality(Enum):
    """Data quality indicator"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INVALID = "invalid"


@dataclass
class TelemetryPoint:
    """
    Single telemetry data point
    
    Attributes:
        timestamp: Timestamp of data collection
        source: Source of the data
        source_id: Identifier of the source device
        value: The actual data value
        unit: Unit of measurement
        quality: Data quality indicator
        processed: Whether data has been processed
        processed_at: Timestamp of processing
    """
    timestamp: datetime
    source: TelemetrySource
    source_id: str
    value: float
    unit: str = ""
    quality: DataQuality = DataQuality.GOOD
    processed: bool = False
    processed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "source": self.source.value,
            "source_id": self.source_id,
            "value": self.value,
            "unit": self.unit,
            "quality": self.quality.value,
            "processed": self.processed,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None
        }


@dataclass
class TelemetryStream:
    """
    Continuous stream of telemetry data
    
    Attributes:
        stream_id: Unique identifier for the stream
        entity_id: ID of the entity (helicopter, vehicle, etc.)
        entity_type: Type of entity
        points: List of telemetry data points
        start_time: Start of the stream
        end_time: End of the stream
        sampling_rate: Sampling rate in Hz
        is_active: Whether stream is currently active
    """
    stream_id: str
    entity_id: str
    entity_type: str
    points: List[TelemetryPoint] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = None
    sampling_rate: float = 1.0
    is_active: bool = True
    
    def add_point(self, point: TelemetryPoint) -> None:
        """Add a new telemetry point to the stream"""
        self.points.append(point)
        self.end_time = point.timestamp
    
    def get_latest(self, count: int = 10) -> List[TelemetryPoint]:
        """Get the latest N telemetry points"""
        return self.points[-count:] if self.points else []
    
    def get_by_source(self, source: TelemetrySource) -> List[TelemetryPoint]:
        """Get all points from a specific source"""
        return [p for p in self.points if p.source == source]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "stream_id": self.stream_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "points": [p.to_dict() for p in self.points],
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "sampling_rate": self.sampling_rate,
            "is_active": self.is_active,
            "point_count": len(self.points)
        }


@dataclass
class TelemetryBatch:
    """
    Batch of telemetry data for efficient processing
    
    Attributes:
        batch_id: Unique identifier for the batch
        streams: List of telemetry streams
        created_at: Timestamp of batch creation
        processed: Whether batch has been processed
        processed_at: Timestamp of processing
    """
    batch_id: str
    streams: List[TelemetryStream] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    processed: bool = False
    processed_at: Optional[datetime] = None
    
    def add_stream(self, stream: TelemetryStream) -> None:
        """Add a telemetry stream to the batch"""
        self.streams.append(stream)
    
    def get_total_points(self) -> int:
        """Get total number of telemetry points in the batch"""
        return sum(len(s.points) for s in self.streams)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "batch_id": self.batch_id,
            "streams": [s.to_dict() for s in self.streams],
            "created_at": self.created_at.isoformat(),
            "processed": self.processed,
            "processed_at": self.processed_at.isoformat() if self.processed_at else None,
            "total_points": self.get_total_points(),
            "stream_count": len(self.streams)
        }


@dataclass
class TelemetryStatistics:
    """
    Statistical analysis of telemetry data
    
    Attributes:
        entity_id: ID of the entity
        entity_type: Type of entity
        time_range: Time range of the analysis
        metrics: Dictionary of statistical metrics
    """
    entity_id: str
    entity_type: str
    time_range: Dict[str, datetime]
    metrics: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    def add_metric(self, source: str, metric_name: str, value: float) -> None:
        """Add a metric for a source"""
        if source not in self.metrics:
            self.metrics[source] = {}
        self.metrics[source][metric_name] = value
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "time_range": {
                "start": self.time_range.get("start", datetime.utcnow()).isoformat(),
                "end": self.time_range.get("end", datetime.utcnow()).isoformat()
            },
            "metrics": self.metrics
        }


@dataclass
class TelemetryAlert:
    """
    Alert generated from telemetry data analysis
    
    Attributes:
        alert_id: Unique identifier
        entity_id: ID of the entity
        entity_type: Type of entity
        source: Source of the telemetry data
        condition: Condition that triggered the alert
        value: The value that triggered the alert
        threshold: Threshold that was exceeded
        severity: Severity level
        message: Alert message
        timestamp: Timestamp of the alert
        acknowledged: Whether alert has been acknowledged
    """
    alert_id: str
    entity_id: str
    entity_type: str
    source: TelemetrySource
    condition: str
    value: float
    threshold: float
    severity: str
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "source": self.source.value,
            "condition": self.condition,
            "value": self.value,
            "threshold": self.threshold,
            "severity": self.severity,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }


@dataclass
class TelemetryConfig:
    """
    Configuration for telemetry data collection
    
    Attributes:
        entity_type: Type of entity
        sampling_rate: Sampling rate in Hz
        enabled_sources: List of enabled telemetry sources
        quality_threshold: Minimum quality threshold
        storage_enabled: Whether to store telemetry data
        processing_enabled: Whether to process telemetry data
        alert_thresholds: Thresholds for generating alerts
    """
    entity_type: str
    sampling_rate: float = 1.0
    enabled_sources: List[TelemetrySource] = field(default_factory=list)
    quality_threshold: DataQuality = DataQuality.POOR
    storage_enabled: bool = True
    processing_enabled: bool = True
    alert_thresholds: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entity_type": self.entity_type,
            "sampling_rate": self.sampling_rate,
            "enabled_sources": [s.value for s in self.enabled_sources],
            "quality_threshold": self.quality_threshold.value,
            "storage_enabled": self.storage_enabled,
            "processing_enabled": self.processing_enabled,
            "alert_thresholds": self.alert_thresholds
        }

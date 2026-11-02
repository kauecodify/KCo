"""
Image Processing Models - For AI-powered vehicle image analysis
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


@dataclass
class ImageAnalysisResult:
    """Represents the result of image analysis"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    image_id: str = ""
    image_url: str = ""
    vehicle_id: Optional[str] = None
    analysis_timestamp: datetime = field(default_factory=datetime.utcnow)
    
    # Detection results
    detected_objects: List[Dict[str, Any]] = field(default_factory=list)
    anomalies: List[Dict[str, Any]] = field(default_factory=list)
    damage_assessment: Dict[str, Any] = field(default_factory=dict)
    
    # Image metadata
    image_width: int = 0
    image_height: int = 0
    image_format: str = ""
    image_size_bytes: int = 0
    
    # Processing metadata
    processing_time_ms: float = 0.0
    confidence_score: float = 0.0
    model_version: str = "v1.0"
    
    # Analysis categories
    categories: Dict[str, float] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "image_id": self.image_id,
            "image_url": self.image_url,
            "vehicle_id": self.vehicle_id,
            "analysis_timestamp": self.analysis_timestamp.isoformat(),
            "detected_objects": self.detected_objects,
            "anomalies": self.anomalies,
            "damage_assessment": self.damage_assessment,
            "image_width": self.image_width,
            "image_height": self.image_height,
            "image_format": self.image_format,
            "image_size_bytes": self.image_size_bytes,
            "processing_time_ms": self.processing_time_ms,
            "confidence_score": self.confidence_score,
            "model_version": self.model_version,
            "categories": self.categories
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ImageAnalysisResult":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            image_id=data.get("image_id", ""),
            image_url=data.get("image_url", ""),
            vehicle_id=data.get("vehicle_id"),
            analysis_timestamp=datetime.fromisoformat(data["analysis_timestamp"]) if data.get("analysis_timestamp") else datetime.utcnow(),
            detected_objects=data.get("detected_objects", []),
            anomalies=data.get("anomalies", []),
            damage_assessment=data.get("damage_assessment", {}),
            image_width=data.get("image_width", 0),
            image_height=data.get("image_height", 0),
            image_format=data.get("image_format", ""),
            image_size_bytes=data.get("image_size_bytes", 0),
            processing_time_ms=data.get("processing_time_ms", 0.0),
            confidence_score=data.get("confidence_score", 0.0),
            model_version=data.get("model_version", "v1.0"),
            categories=data.get("categories", {})
        )


@dataclass
class ImageUploadRequest:
    """Represents a request to upload and process an image"""
    image_url: Optional[str] = None
    image_base64: Optional[str] = None
    vehicle_id: Optional[str] = None
    analysis_type: str = "full"  # full, damage, parts, exterior, interior
    priority: str = "normal"  # low, normal, high, critical
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "image_url": self.image_url,
            "image_base64": self.image_base64,
            "vehicle_id": self.vehicle_id,
            "analysis_type": self.analysis_type,
            "priority": self.priority,
            "metadata": self.metadata
        }


@dataclass
class DamageAssessment:
    """Detailed damage assessment from image analysis"""
    damage_type: str = ""
    severity: str = "low"  # low, medium, high, critical
    location: Dict[str, float] = field(default_factory=dict)  # x, y coordinates
    dimensions: Dict[str, float] = field(default_factory=dict)  # width, height
    estimated_repair_cost: float = 0.0
    confidence: float = 0.0
    description: str = ""
    recommended_action: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "damage_type": self.damage_type,
            "severity": self.severity,
            "location": self.location,
            "dimensions": self.dimensions,
            "estimated_repair_cost": self.estimated_repair_cost,
            "confidence": self.confidence,
            "description": self.description,
            "recommended_action": self.recommended_action
        }


@dataclass
class DetectedObject:
    """Represents a detected object in image analysis"""
    object_type: str = ""
    confidence: float = 0.0
    bounding_box: Dict[str, float] = field(default_factory=dict)  # x_min, y_min, x_max, y_max
    location: Dict[str, float] = field(default_factory=dict)  # center x, y
    size: Dict[str, float] = field(default_factory=dict)  # width, height
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "object_type": self.object_type,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box,
            "location": self.location,
            "size": self.size
        }

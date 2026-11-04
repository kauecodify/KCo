"""
H Module - Image Analysis Data Model
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Image analysis data model for AI-powered processing
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import base64


class ImageType(Enum):
    """Type of image"""
    VISIBLE = "visible"
    THERMAL = "thermal"
    NIGHT_VISION = "night_vision"
    INFRARED = "infrared"
    MULTISPECTRAL = "multispectral"
    HYPERSPECTRAL = "hyperspectral"
    SATELLITE = "satellite"
    AERIAL = "aerial"
    GROUND = "ground"


class ImageFormat(Enum):
    """Image file format"""
    JPEG = "jpeg"
    PNG = "png"
    WEBP = "webp"
    TIFF = "tiff"
    BMP = "bmp"
    RAW = "raw"


class AnalysisType(Enum):
    """Type of analysis performed"""
    OBJECT_DETECTION = "object_detection"
    ANOMALY_DETECTION = "anomaly_detection"
    DAMAGE_ASSESSMENT = "damage_assessment"
    VEHICLE_RECOGNITION = "vehicle_recognition"
    LICENSE_PLATE = "license_plate"
    FACIAL_RECOGNITION = "facial_recognition"
    SCENE_SEGMENTATION = "scene_segmentation"
    DEPTH_ESTIMATION = "depth_estimation"
    CLASSIFICATION = "classification"


class AnalysisStatus(Enum):
    """Status of image analysis"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Severity(Enum):
    """Severity level for detected issues"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class ImageMetadata:
    """
    Metadata for an image
    
    Attributes:
        image_id: Unique identifier
        entity_id: ID of the entity (helicopter, vehicle, etc.)
        entity_type: Type of entity
        camera_id: ID of the camera that captured the image
        image_type: Type of image
        image_format: Format of the image
        width: Image width in pixels
        height: Image height in pixels
        timestamp: Timestamp when image was captured
        location: Geographic location where image was captured
        orientation: Camera orientation (yaw, pitch, roll)
        focal_length: Focal length of the camera
        aperture: Aperture setting
        iso: ISO setting
        shutter_speed: Shutter speed
        white_balance: White balance setting
    """
    image_id: str
    entity_id: str
    entity_type: str
    camera_id: str
    image_type: ImageType = ImageType.VISIBLE
    image_format: ImageFormat = ImageFormat.JPEG
    width: int = 1920
    height: int = 1080
    timestamp: datetime = field(default_factory=datetime.utcnow)
    location: Optional[Dict[str, float]] = None
    orientation: Dict[str, float] = field(default_factory=dict)
    focal_length: float = 24.0
    aperture: float = 2.8
    iso: int = 100
    shutter_speed: float = 1.0 / 1000
    white_balance: str = "auto"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "image_id": self.image_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "camera_id": self.camera_id,
            "image_type": self.image_type.value,
            "image_format": self.image_format.value,
            "width": self.width,
            "height": self.height,
            "timestamp": self.timestamp.isoformat(),
            "location": self.location,
            "orientation": self.orientation,
            "focal_length": self.focal_length,
            "aperture": self.aperture,
            "iso": self.iso,
            "shutter_speed": self.shutter_speed,
            "white_balance": self.white_balance
        }


@dataclass
class DetectedObject:
    """
    Object detected in an image
    
    Attributes:
        object_id: Unique identifier for the detected object
        class_name: Name of the detected class
        class_id: ID of the detected class
        confidence: Confidence score (0-1)
        bounding_box: Bounding box coordinates [x, y, width, height]
        center: Center coordinates [x, y]
        area: Area of the bounding box
        color: Color representation (if applicable)
        metadata: Additional metadata
    """
    object_id: str
    class_name: str
    class_id: int
    confidence: float
    bounding_box: List[float] = field(default_factory=list)
    center: List[float] = field(default_factory=list)
    area: float = 0.0
    color: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "object_id": self.object_id,
            "class_name": self.class_name,
            "class_id": self.class_id,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box,
            "center": self.center,
            "area": self.area,
            "color": self.color,
            "metadata": self.metadata
        }


@dataclass
class DetectedAnomaly:
    """
    Anomaly detected in an image
    
    Attributes:
        anomaly_id: Unique identifier
        anomaly_type: Type of anomaly
        severity: Severity level
        description: Description of the anomaly
        confidence: Confidence score (0-1)
        bounding_box: Bounding box coordinates
        affected_area: Percentage of image affected
        recommended_action: Recommended action to address the anomaly
        parts_affected: List of parts affected (for vehicles)
        repair_cost: Estimated repair cost
        repair_time: Estimated repair time in hours
    """
    anomaly_id: str
    anomaly_type: str
    severity: Severity = Severity.MEDIUM
    description: str = ""
    confidence: float = 0.0
    bounding_box: List[float] = field(default_factory=list)
    affected_area: float = 0.0
    recommended_action: str = ""
    parts_affected: List[str] = field(default_factory=list)
    repair_cost: float = 0.0
    repair_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "anomaly_id": self.anomaly_id,
            "anomaly_type": self.anomaly_type,
            "severity": self.severity.value,
            "description": self.description,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box,
            "affected_area": self.affected_area,
            "recommended_action": self.recommended_action,
            "parts_affected": self.parts_affected,
            "repair_cost": self.repair_cost,
            "repair_time": self.repair_time
        }


@dataclass
class ImageAnalysis:
    """
    Image analysis result
    
    Attributes:
        analysis_id: Unique identifier
        image_id: ID of the analyzed image
        analysis_type: Type of analysis performed
        status: Status of the analysis
        started_at: Timestamp when analysis started
        completed_at: Timestamp when analysis completed
        model_version: Version of the AI model used
        processing_time: Time taken to process in milliseconds
        confidence: Overall confidence score
        objects: List of detected objects
        anomalies: List of detected anomalies
        metadata: Additional metadata
        error: Error message if analysis failed
    """
    analysis_id: str
    image_id: str
    analysis_type: AnalysisType
    status: AnalysisStatus = AnalysisStatus.PENDING
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    model_version: str = "1.0.0"
    processing_time: float = 0.0
    confidence: float = 0.0
    objects: List[DetectedObject] = field(default_factory=list)
    anomalies: List[DetectedAnomaly] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    
    def add_object(self, obj: DetectedObject) -> None:
        """Add a detected object"""
        self.objects.append(obj)
    
    def add_anomaly(self, anomaly: DetectedAnomaly) -> None:
        """Add a detected anomaly"""
        self.anomalies.append(anomaly)
    
    def mark_completed(self) -> None:
        """Mark analysis as completed"""
        self.status = AnalysisStatus.COMPLETED
        self.completed_at = datetime.utcnow()
        self.processing_time = (self.completed_at - self.started_at).total_seconds() * 1000
    
    def mark_failed(self, error: str) -> None:
        """Mark analysis as failed"""
        self.status = AnalysisStatus.FAILED
        self.error = error
        self.completed_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "analysis_id": self.analysis_id,
            "image_id": self.image_id,
            "analysis_type": self.analysis_type.value,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "model_version": self.model_version,
            "processing_time": self.processing_time,
            "confidence": self.confidence,
            "objects": [o.to_dict() for o in self.objects],
            "anomalies": [a.to_dict() for a in self.anomalies],
            "metadata": self.metadata,
            "error": self.error,
            "object_count": len(self.objects),
            "anomaly_count": len(self.anomalies),
            "critical_anomalies": len([a for a in self.anomalies if a.severity == Severity.CRITICAL]),
            "high_anomalies": len([a for a in self.anomalies if a.severity == Severity.HIGH])
        }


@dataclass
class ImageData:
    """
    Complete image data including image bytes
    
    Attributes:
        metadata: Image metadata
        data: Image bytes (base64 encoded)
        thumbnail: Thumbnail image bytes (base64 encoded)
        analysis: Image analysis result
    """
    metadata: ImageMetadata
    data: Optional[str] = None
    thumbnail: Optional[str] = None
    analysis: Optional[ImageAnalysis] = None
    
    def set_image_data(self, image_bytes: bytes) -> None:
        """Set image data as base64 encoded string"""
        self.data = base64.b64encode(image_bytes).decode("utf-8")
    
    def set_thumbnail(self, thumbnail_bytes: bytes) -> None:
        """Set thumbnail data as base64 encoded string"""
        self.thumbnail = base64.b64encode(thumbnail_bytes).decode("utf-8")
    
    def get_image_bytes(self) -> Optional[bytes]:
        """Get image bytes from base64"""
        if self.data:
            return base64.b64decode(self.data)
        return None
    
    def get_thumbnail_bytes(self) -> Optional[bytes]:
        """Get thumbnail bytes from base64"""
        if self.thumbnail:
            return base64.b64decode(self.thumbnail)
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary (without large image data)"""
        return {
            "metadata": self.metadata.to_dict(),
            "has_image": self.data is not None,
            "has_thumbnail": self.thumbnail is not None,
            "analysis": self.analysis.to_dict() if self.analysis else None
        }


@dataclass
class BatchAnalysis:
    """
    Batch processing of multiple images
    
    Attributes:
        batch_id: Unique identifier
        image_ids: List of image IDs in the batch
        analyses: List of analysis results
        created_at: Timestamp of batch creation
        completed_at: Timestamp of batch completion
        total_images: Total number of images
        processed_images: Number of images processed
        failed_images: Number of images that failed
    """
    batch_id: str
    image_ids: List[str] = field(default_factory=list)
    analyses: List[ImageAnalysis] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    total_images: int = 0
    processed_images: int = 0
    failed_images: int = 0
    
    def add_image(self, image_id: str) -> None:
        """Add an image to the batch"""
        self.image_ids.append(image_id)
        self.total_images += 1
    
    def add_analysis(self, analysis: ImageAnalysis) -> None:
        """Add an analysis result"""
        self.analyses.append(analysis)
        if analysis.status == AnalysisStatus.COMPLETED:
            self.processed_images += 1
        elif analysis.status == AnalysisStatus.FAILED:
            self.failed_images += 1
    
    def mark_completed(self) -> None:
        """Mark batch as completed"""
        self.completed_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "batch_id": self.batch_id,
            "image_ids": self.image_ids,
            "analyses": [a.to_dict() for a in self.analyses],
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_images": self.total_images,
            "processed_images": self.processed_images,
            "failed_images": self.failed_images,
            "success_rate": self.processed_images / self.total_images if self.total_images > 0 else 0
        }


@dataclass
class AnalysisConfig:
    """
    Configuration for image analysis
    
    Attributes:
        analysis_type: Type of analysis to perform
        model_name: Name of the AI model to use
        confidence_threshold: Minimum confidence threshold
        min_object_size: Minimum object size to detect
        max_objects: Maximum number of objects to detect
        enable_anomaly_detection: Whether to detect anomalies
        enable_classification: Whether to classify objects
        enable_segmentation: Whether to perform segmentation
        gpu_enabled: Whether to use GPU acceleration
        batch_size: Batch size for processing
    """
    analysis_type: AnalysisType = AnalysisType.OBJECT_DETECTION
    model_name: str = "yolov8x"
    confidence_threshold: float = 0.5
    min_object_size: float = 0.01
    max_objects: int = 100
    enable_anomaly_detection: bool = True
    enable_classification: bool = True
    enable_segmentation: bool = False
    gpu_enabled: bool = True
    batch_size: int = 8
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "analysis_type": self.analysis_type.value,
            "model_name": self.model_name,
            "confidence_threshold": self.confidence_threshold,
            "min_object_size": self.min_object_size,
            "max_objects": self.max_objects,
            "enable_anomaly_detection": self.enable_anomaly_detection,
            "enable_classification": self.enable_classification,
            "enable_segmentation": self.enable_segmentation,
            "gpu_enabled": self.gpu_enabled,
            "batch_size": self.batch_size
        }

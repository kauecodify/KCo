"""
H Module - Aerial Image Processor
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

AI-powered aerial image processing for helicopters
"""

import asyncio
import logging
import cv2
import numpy as np
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Union
import base64
import io
from PIL import Image

from ..models.image_analysis import (
    ImageAnalysis,
    ImageMetadata,
    DetectedObject,
    DetectedAnomaly,
    AnalysisType,
    AnalysisStatus,
    Severity,
    ImageType,
    ImageFormat
)
from ..models.helicopter import Helicopter, CameraSettings
from ..models.telemetry import TelemetryPoint, TelemetrySource

logger = logging.getLogger(__name__)


@dataclass
class AerialProcessingConfig:
    """Configuration for aerial image processing"""
    model_path: str = "models/yolov8x.pt"
    confidence_threshold: float = 0.5
    iou_threshold: float = 0.45
    image_size: int = 640
    batch_size: int = 8
    use_gpu: bool = True
    enable_anomaly_detection: bool = True
    enable_object_tracking: bool = True
    max_objects: int = 100
    min_object_size: float = 0.01


@dataclass
class ProcessingResult:
    """Result of aerial image processing"""
    analysis_id: str
    image_id: str
    helicopter_id: str
    camera_id: str
    timestamp: datetime
    objects: List[DetectedObject] = field(default_factory=list)
    anomalies: List[DetectedAnomaly] = field(default_factory=list)
    processing_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "analysis_id": self.analysis_id,
            "image_id": self.image_id,
            "helicopter_id": self.helicopter_id,
            "camera_id": self.camera_id,
            "timestamp": self.timestamp.isoformat(),
            "objects": [o.to_dict() for o in self.objects],
            "anomalies": [a.to_dict() for a in self.anomalies],
            "processing_time": self.processing_time,
            "metadata": self.metadata,
            "object_count": len(self.objects),
            "anomaly_count": len(self.anomalies)
        }


class AerialImageProcessor:
    """
    AI-powered aerial image processor for helicopters
    
    Features:
    - Real-time object detection from aerial imagery
    - Anomaly detection (damage, obstacles, etc.)
    - Object tracking across frames
    - Multi-camera support
    - Thermal and night vision processing
    - Geospatial tagging
    """
    
    def __init__(self, config: Optional[AerialProcessingConfig] = None):
        """
        Initialize aerial image processor
        
        Args:
            config: Processing configuration
        """
        self.config = config or AerialProcessingConfig()
        self.is_loaded = False
        self.model = None
        self.tracker = None
        self.anomaly_detector = None
        self.processing_queue = asyncio.Queue()
        self.is_processing = False
        self.stats = {
            "total_images": 0,
            "processed_images": 0,
            "failed_images": 0,
            "total_objects": 0,
            "total_anomalies": 0,
            "avg_processing_time": 0.0
        }
        
        logger.info("Aerial Image Processor initialized")
    
    async def load_model(self) -> bool:
        """Load the AI model"""
        try:
            # Try to load YOLOv8 model
            try:
                from ultralytics import YOLO
                self.model = YOLO(self.config.model_path)
                logger.info(f"Loaded YOLOv8 model from {self.config.model_path}")
            except ImportError:
                # Fallback to OpenCV DNN
                logger.warning("Ultralytics not available, using OpenCV DNN")
                self.model = cv2.dnn.readNet(self.config.model_path)
            
            self.is_loaded = True
            logger.info("Aerial Image Processor model loaded successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    async def start(self) -> None:
        """Start the processing queue"""
        if self.is_processing:
            logger.warning("Aerial Image Processor is already running")
            return
        
        if not self.is_loaded:
            await self.load_model()
        
        self.is_processing = True
        logger.info("Aerial Image Processor started")
        
        while self.is_processing:
            try:
                # Get next image from queue
                task = await self.processing_queue.get()
                image_data, metadata, config = task
                
                # Process the image
                result = await self.process_image(image_data, metadata, config)
                
                # Mark task as done
                self.processing_queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing image: {e}")
    
    async def stop(self) -> None:
        """Stop the processing queue"""
        self.is_processing = False
        logger.info("Aerial Image Processor stopped")
    
    async def process_image(self, image_data: Union[bytes, str], 
                            metadata: Optional[ImageMetadata] = None,
                            config: Optional[AerialProcessingConfig] = None) -> ImageAnalysis:
        """
        Process an aerial image
        
        Args:
            image_data: Image bytes or base64 encoded string
            metadata: Image metadata
            config: Processing configuration (overrides default)
            
        Returns:
            ImageAnalysis result
        """
        start_time = datetime.utcnow()
        
        # Use provided config or default
        processing_config = config or self.config
        
        # Create analysis object
        analysis_id = f"aerial_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        image_id = metadata.image_id if metadata else f"img_{analysis_id}"
        
        analysis = ImageAnalysis(
            analysis_id=analysis_id,
            image_id=image_id,
            analysis_type=AnalysisType.OBJECT_DETECTION,
            status=AnalysisStatus.PROCESSING,
            started_at=start_time,
            model_version=self.config.model_path
        )
        
        try:
            # Decode image
            if isinstance(image_data, str):
                # Base64 encoded
                image_bytes = base64.b64decode(image_data)
            else:
                image_bytes = image_data
            
            # Convert to OpenCV format
            image = self._decode_image(image_bytes)
            if image is None:
                analysis.mark_failed("Failed to decode image")
                self.stats["failed_images"] += 1
                return analysis
            
            # Preprocess image
            processed_image = self._preprocess(image, metadata)
            
            # Detect objects
            objects = await self._detect_objects(processed_image, processing_config)
            
            # Detect anomalies
            anomalies = []
            if processing_config.enable_anomaly_detection:
                anomalies = await self._detect_anomalies(processed_image, objects, processing_config)
            
            # Add results to analysis
            for obj in objects:
                analysis.add_object(obj)
            for anomaly in anomalies:
                analysis.add_anomaly(anomaly)
            
            # Mark as completed
            analysis.mark_completed()
            self.stats["processed_images"] += 1
            self.stats["total_objects"] += len(objects)
            self.stats["total_anomalies"] += len(anomalies)
            
            # Update average processing time
            processing_time = analysis.processing_time
            if self.stats["processed_images"] == 1:
                self.stats["avg_processing_time"] = processing_time
            else:
                self.stats["avg_processing_time"] = (
                    (self.stats["avg_processing_time"] * (self.stats["processed_images"] - 1)) + processing_time
                ) / self.stats["processed_images"]
            
            logger.info(f"Processed aerial image {image_id}: {len(objects)} objects, {len(anomalies)} anomalies")
            
        except Exception as e:
            analysis.mark_failed(str(e))
            self.stats["failed_images"] += 1
            logger.error(f"Failed to process image {image_id}: {e}")
        
        self.stats["total_images"] += 1
        return analysis
    
    async def process_batch(self, images: List[Tuple[Union[bytes, str], ImageMetadata]]) -> List[ImageAnalysis]:
        """
        Process a batch of images
        
        Args:
            images: List of (image_data, metadata) tuples
            
        Returns:
            List of ImageAnalysis results
        """
        results = []
        for image_data, metadata in images:
            result = await self.process_image(image_data, metadata)
            results.append(result)
        return results
    
    async def process_stream(self, helicopter: Helicopter, camera: CameraSettings,
                            stream_callback: Optional[Callable] = None) -> None:
        """
        Process a live video stream from a helicopter camera
        
        Args:
            helicopter: Helicopter object
            camera: Camera settings
            stream_callback: Callback for processed frames
        """
        logger.info(f"Starting aerial stream processing for {helicopter.helicopter_id}/{camera.camera_id}")
        
        # This would be connected to actual camera stream
        # For now, we simulate processing
        while True:
            try:
                # Simulate frame capture
                # In real implementation, this would come from camera
                frame = self._simulate_frame(helicopter, camera)
                
                # Create metadata
                metadata = ImageMetadata(
                    image_id=f"{helicopter.helicopter_id}_{camera.camera_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
                    entity_id=helicopter.helicopter_id,
                    entity_type="helicopter",
                    camera_id=camera.camera_id,
                    image_type=ImageType.AERIAL,
                    timestamp=datetime.utcnow(),
                    location={
                        "latitude": helicopter.location.latitude,
                        "longitude": helicopter.location.longitude,
                        "altitude": helicopter.location.altitude
                    },
                    orientation={
                        "yaw": helicopter.location.heading,
                        "pitch": 0.0,
                        "roll": 0.0
                    },
                    focal_length=camera.focal_length,
                    aperture=camera.aperture,
                    iso=camera.iso,
                    shutter_speed=camera.shutter_speed
                )
                
                # Process frame
                result = await self.process_image(frame, metadata)
                
                # Call callback if provided
                if stream_callback:
                    await stream_callback(result)
                
                # Small delay to simulate frame rate
                await asyncio.sleep(1.0 / camera.fps)
                
            except Exception as e:
                logger.error(f"Error in stream processing: {e}")
                break
    
    def _decode_image(self, image_bytes: bytes) -> Optional[np.ndarray]:
        """Decode image bytes to OpenCV format"""
        try:
            # Try to decode as JPEG
            image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is not None:
                return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Try PIL
            image = Image.open(io.BytesIO(image_bytes))
            return np.array(image)
            
        except Exception as e:
            logger.error(f"Failed to decode image: {e}")
            return None
    
    def _preprocess(self, image: np.ndarray, metadata: Optional[ImageMetadata] = None) -> np.ndarray:
        """
        Preprocess image for AI model
        
        Args:
            image: Input image
            metadata: Optional metadata for camera-specific processing
            
        Returns:
            Processed image
        """
        # Convert to RGB if needed
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif image.shape[2] == 4:
            image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
        
        # Apply camera-specific processing if metadata available
        if metadata:
            # Thermal image processing
            if metadata.image_type == ImageType.THERMAL:
                image = self._process_thermal(image)
            
            # Night vision processing
            elif metadata.image_type == ImageType.NIGHT_VISION:
                image = self._process_night_vision(image)
            
            # Apply exposure correction based on camera settings
            if metadata.iso > 400:
                image = self._correct_exposure(image, 1.2)
        
        # Resize to model input size
        if self.config.image_size:
            image = cv2.resize(image, (self.config.image_size, self.config.image_size))
        
        return image
    
    def _process_thermal(self, image: np.ndarray) -> np.ndarray:
        """Process thermal imagery"""
        # Apply histogram equalization for better contrast
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        equalized = cv2.equalizeHist(gray)
        return cv2.cvtColor(equalized, cv2.COLOR_GRAY2RGB)
    
    def _process_night_vision(self, image: np.ndarray) -> np.ndarray:
        """Process night vision imagery"""
        # Apply denoising
        denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        
        # Enhance contrast
        lab = cv2.cvtColor(denoised, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    
    def _correct_exposure(self, image: np.ndarray, gamma: float = 1.0) -> np.ndarray:
        """Correct exposure using gamma correction"""
        inv_gamma = 1.0 / gamma
        table = np.array([(i / 255.0) ** inv_gamma * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(image, table)
    
    async def _detect_objects(self, image: np.ndarray, config: AerialProcessingConfig) -> List[DetectedObject]:
        """
        Detect objects in the image using AI model
        
        Args:
            image: Input image
            config: Processing configuration
            
        Returns:
            List of detected objects
        """
        objects = []
        
        try:
            if self.model is None:
                # Fallback to simple detection if model not loaded
                logger.warning("Model not loaded, using simple detection")
                objects = self._simple_detection(image)
            else:
                # Use AI model
                if hasattr(self.model, 'predict'):
                    # YOLOv8
                    results = self.model.predict(image, conf=config.confidence_threshold, iou=config.iou_threshold)
                    for result in results:
                        for box in result.boxes:
                            if box.conf[0] >= config.confidence_threshold:
                                obj = DetectedObject(
                                    object_id=str(len(objects)),
                                    class_name=self.model.names[int(box.cls[0])],
                                    class_id=int(box.cls[0]),
                                    confidence=float(box.conf[0]),
                                    bounding_box=[float(box.xyxy[0][0]), float(box.xyxy[0][1]), 
                                                  float(box.xyxy[0][2] - box.xyxy[0][0]), 
                                                  float(box.xyxy[0][3] - box.xyxy[0][1])],
                                    center=[float((box.xyxy[0][0] + box.xyxy[0][2]) / 2), 
                                            float((box.xyxy[0][1] + box.xyxy[0][3]) / 2)],
                                    area=float((box.xyxy[0][2] - box.xyxy[0][0]) * 
                                               (box.xyxy[0][3] - box.xyxy[0][1]))
                                )
                                objects.append(obj)
                else:
                    # OpenCV DNN
                    blob = cv2.dnn.blobFromImage(image, 1/255.0, (config.image_size, config.image_size), swapRB=True)
                    self.model.setInput(blob)
                    outputs = self.model.forward()
                    
                    # Process outputs (simplified)
                    for output in outputs:
                        for detection in output:
                            scores = detection[5:]
                            class_id = np.argmax(scores)
                            confidence = scores[class_id]
                            
                            if confidence >= config.confidence_threshold:
                                # Get bounding box
                                center_x = int(detection[0] * image.shape[1])
                                center_y = int(detection[1] * image.shape[0])
                                width = int(detection[2] * image.shape[1])
                                height = int(detection[3] * image.shape[0])
                                
                                obj = DetectedObject(
                                    object_id=str(len(objects)),
                                    class_name=str(class_id),
                                    class_id=int(class_id),
                                    confidence=float(confidence),
                                    bounding_box=[center_x - width/2, center_y - height/2, width, height],
                                    center=[center_x, center_y],
                                    area=width * height
                                )
                                objects.append(obj)
            
            # Limit number of objects
            if config.max_objects and len(objects) > config.max_objects:
                objects = objects[:config.max_objects]
            
            # Filter by minimum size
            if config.min_object_size:
                objects = [o for o in objects if o.area >= config.min_object_size * image.size]
            
        except Exception as e:
            logger.error(f"Error detecting objects: {e}")
        
        return objects
    
    async def _detect_anomalies(self, image: np.ndarray, objects: List[DetectedObject],
                                config: AerialProcessingConfig) -> List[DetectedAnomaly]:
        """
        Detect anomalies in the image
        
        Args:
            image: Input image
            objects: Detected objects
            config: Processing configuration
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        try:
            # Check for known anomaly patterns
            
            # 1. Check for damage on vehicles
            vehicle_objects = [o for o in objects if "car" in o.class_name.lower() or 
                             "truck" in o.class_name.lower() or "vehicle" in o.class_name.lower()]
            
            for vehicle in vehicle_objects:
                # Analyze vehicle region for damage
                x, y, w, h = map(int, vehicle.bounding_box)
                vehicle_region = image[y:y+h, x:x+w]
                
                # Check for damage indicators (simplified)
                damage_score = self._detect_damage(vehicle_region)
                if damage_score > 0.7:
                    anomaly = DetectedAnomaly(
                        anomaly_id=f"damage_{len(anomalies)}",
                        anomaly_type="vehicle_damage",
                        severity=Severity.HIGH if damage_score > 0.9 else Severity.MEDIUM,
                        description=f"Potential damage detected on {vehicle.class_name}",
                        confidence=damage_score,
                        bounding_box=vehicle.bounding_box,
                        affected_area=vehicle.area / (image.shape[0] * image.shape[1]),
                        recommended_action="Inspect vehicle for damage",
                        parts_affected=["exterior"],
                        repair_cost=500.0 if damage_score > 0.9 else 200.0,
                        repair_time=2.0 if damage_score > 0.9 else 1.0
                    )
                    anomalies.append(anomaly)
            
            # 2. Check for obstacles on runways/roads
            obstacle_classes = ["person", "animal", "debris", "obstacle"]
            obstacles = [o for o in objects if any(obs in o.class_name.lower() for obs in obstacle_classes)]
            
            for obstacle in obstacles:
                anomaly = DetectedAnomaly(
                    anomaly_id=f"obstacle_{len(anomalies)}",
                    anomaly_type="obstacle",
                    severity=Severity.CRITICAL if obstacle.confidence > 0.9 else Severity.HIGH,
                    description=f"Obstacle detected: {obstacle.class_name}",
                    confidence=obstacle.confidence,
                    bounding_box=obstacle.bounding_box,
                    affected_area=obstacle.area / (image.shape[0] * image.shape[1]),
                    recommended_action="Avoid obstacle or remove if safe",
                    repair_cost=0.0,
                    repair_time=0.0
                )
                anomalies.append(anomaly)
            
            # 3. Check for unusual patterns (anomaly detection)
            if len(objects) == 0:
                # Empty area - could be anomaly depending on context
                pass
            
        except Exception as e:
            logger.error(f"Error detecting anomalies: {e}")
        
        return anomalies
    
    def _detect_damage(self, region: np.ndarray) -> float:
        """
        Detect damage in a vehicle region (simplified)
        
        Args:
            region: Image region to analyze
            
        Returns:
            Damage confidence score (0-1)
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
            
            # Edge detection
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / edges.size
            
            # Color analysis - look for rust, dents, etc.
            hsv = cv2.cvtColor(region, cv2.COLOR_RGB2HSV)
            
            # Rust color range (orange-brown)
            lower_rust = np.array([0, 50, 50])
            upper_rust = np.array([20, 255, 255])
            mask_rust = cv2.inRange(hsv, lower_rust, upper_rust)
            rust_density = np.sum(mask_rust > 0) / mask_rust.size
            
            # Dent detection - look for circular edges
            circles = cv2.HoughCircles(edges, cv2.HOUGH_GRADIENT, dp=1, minDist=20, 
                                       param1=50, param2=30, minRadius=5, maxRadius=50)
            circle_count = 0 if circles is None else len(circles[0])
            
            # Combine scores
            damage_score = (edge_density * 0.4 + rust_density * 0.4 + 
                           min(circle_count / 10, 1.0) * 0.2)
            
            return min(damage_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error detecting damage: {e}")
            return 0.0
    
    def _simulate_frame(self, helicopter: Helicopter, camera: CameraSettings) -> bytes:
        """Simulate a camera frame (for testing)"""
        # Create a simple test image
        height, width = 480, 640
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add some objects
        cv2.rectangle(image, (100, 100), (200, 200), (255, 0, 0), 2)
        cv2.rectangle(image, (300, 150), (400, 250), (0, 255, 0), 2)
        cv2.circle(image, (500, 200), 30, (0, 0, 255), 2)
        
        # Add some text
        cv2.putText(image, f"H: {helicopter.helicopter_id}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(image, f"Cam: {camera.camera_id}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Encode as JPEG
        _, buffer = cv2.imencode('.jpg', image)
        return buffer.tobytes()
    
    async def queue_image(self, image_data: Union[bytes, str], 
                         metadata: Optional[ImageMetadata] = None,
                         config: Optional[AerialProcessingConfig] = None) -> str:
        """
        Queue an image for processing
        
        Args:
            image_data: Image bytes or base64 encoded string
            metadata: Image metadata
            config: Processing configuration
            
        Returns:
            Task ID
        """
        task_id = f"task_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}"
        await self.processing_queue.put((image_data, metadata, config))
        return task_id
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return self.stats.copy()
    
    def reset_stats(self) -> None:
        """Reset processing statistics"""
        self.stats = {
            "total_images": 0,
            "processed_images": 0,
            "failed_images": 0,
            "total_objects": 0,
            "total_anomalies": 0,
            "avg_processing_time": 0.0
        }


# Create global aerial image processor instance
aerial_processor = AerialImageProcessor()

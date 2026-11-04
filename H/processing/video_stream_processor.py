"""
H Module - Video Stream Processor
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Real-time video stream processing for helicopters and vehicles
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple
import cv2
import numpy as np

from .aerial_image_processor import AerialImageProcessor, ProcessingResult
from ..models.helicopter import Helicopter, CameraSettings
from ..models.vehicle import Vehicle, VehicleCamera
from ..models.image_analysis import ImageAnalysis, ImageMetadata, ImageType

logger = logging.getLogger(__name__)


@dataclass
class VideoStreamConfig:
    """Configuration for video stream processing"""
    source: str = ""
    stream_type: str = "rtsp"
    resolution: Tuple[int, int] = (1920, 1080)
    fps: int = 30
    bitrate: int = 8000000
    codec: str = "h264"
    enable_audio: bool = False
    buffer_size: int = 1024
    
    # Processing settings
    process_every_nth_frame: int = 1
    enable_object_detection: bool = True
    enable_anomaly_detection: bool = True
    enable_tracking: bool = True
    
    # Storage settings
    save_frames: bool = False
    save_processed: bool = False
    storage_path: str = "storage/videos"


@dataclass
class StreamStats:
    """Statistics for video stream processing"""
    stream_id: str
    total_frames: int = 0
    processed_frames: int = 0
    skipped_frames: int = 0
    dropped_frames: int = 0
    total_objects: int = 0
    total_anomalies: int = 0
    avg_fps: float = 0.0
    last_frame_time: Optional[datetime] = None
    started_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "stream_id": self.stream_id,
            "total_frames": self.total_frames,
            "processed_frames": self.processed_frames,
            "skipped_frames": self.skipped_frames,
            "dropped_frames": self.dropped_frames,
            "total_objects": self.total_objects,
            "total_anomalies": self.total_anomalies,
            "avg_fps": self.avg_fps,
            "last_frame_time": self.last_frame_time.isoformat() if self.last_frame_time else None,
            "started_at": self.started_at.isoformat(),
            "uptime": (datetime.utcnow() - self.started_at).total_seconds()
        }


@dataclass
class TrackedObject:
    """Object being tracked across frames"""
    track_id: str
    class_name: str
    class_id: int
    confidence: float
    bounding_box: List[float]
    first_seen: datetime = field(default_factory=datetime.utcnow)
    last_seen: datetime = field(default_factory=datetime.utcnow)
    frame_count: int = 0
    trajectory: List[Tuple[float, float]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def update(self, bounding_box: List[float], confidence: float) -> None:
        """Update object with new detection"""
        self.bounding_box = bounding_box
        self.confidence = confidence
        self.last_seen = datetime.utcnow()
        self.frame_count += 1
        
        # Add center to trajectory
        center_x = bounding_box[0] + bounding_box[2] / 2
        center_y = bounding_box[1] + bounding_box[3] / 2
        self.trajectory.append((center_x, center_y))
        
        # Limit trajectory size
        if len(self.trajectory) > 100:
            self.trajectory = self.trajectory[-100:]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "track_id": self.track_id,
            "class_name": self.class_name,
            "class_id": self.class_id,
            "confidence": self.confidence,
            "bounding_box": self.bounding_box,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "frame_count": self.frame_count,
            "trajectory": self.trajectory
        }


class VideoStreamProcessor:
    """
    Real-time video stream processor for helicopters and vehicles
    
    Features:
    - Multi-stream support
    - Frame-by-frame processing
    - Object tracking across frames
    - Anomaly detection
    - Performance monitoring
    - Frame skipping for performance
    """
    
    def __init__(self, image_processor: Optional[AerialImageProcessor] = None):
        """
        Initialize video stream processor
        
        Args:
            image_processor: Image processor instance
        """
        self.image_processor = image_processor or AerialImageProcessor()
        self.streams: Dict[str, VideoStreamConfig] = {}
        self.stats: Dict[str, StreamStats] = {}
        self.tracked_objects: Dict[str, Dict[str, TrackedObject]] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        self.is_running = False
        self.tasks: Dict[str, asyncio.Task] = {}
        
        logger.info("Video Stream Processor initialized")
    
    async def start(self) -> None:
        """Start all video streams"""
        if self.is_running:
            logger.warning("Video Stream Processor is already running")
            return
        
        self.is_running = True
        logger.info("Video Stream Processor started")
        
        # Start all registered streams
        for stream_id, config in self.streams.items():
            await self.start_stream(stream_id, config)
    
    async def stop(self) -> None:
        """Stop all video streams"""
        self.is_running = False
        
        # Cancel all stream tasks
        for stream_id, task in self.tasks.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self.tasks.clear()
        logger.info("Video Stream Processor stopped")
    
    async def start_stream(self, stream_id: str, config: VideoStreamConfig) -> None:
        """
        Start a specific video stream
        
        Args:
            stream_id: Stream identifier
            config: Stream configuration
        """
        if stream_id in self.tasks:
            logger.warning(f"Stream {stream_id} is already running")
            return
        
        self.streams[stream_id] = config
        self.stats[stream_id] = StreamStats(stream_id=stream_id)
        self.tracked_objects[stream_id] = {}
        
        # Create stream task
        task = asyncio.create_task(self._process_stream(stream_id))
        self.tasks[stream_id] = task
        
        logger.info(f"Started video stream {stream_id}")
    
    async def stop_stream(self, stream_id: str) -> None:
        """Stop a specific video stream"""
        if stream_id in self.tasks:
            task = self.tasks[stream_id]
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
            
            del self.tasks[stream_id]
            del self.stats[stream_id]
            del self.tracked_objects[stream_id]
            
            logger.info(f"Stopped video stream {stream_id}")
    
    async def _process_stream(self, stream_id: str) -> None:
        """Process a video stream"""
        config = self.streams[stream_id]
        stats = self.stats[stream_id]
        
        # Open video capture
        cap = None
        try:
            # Try to open the stream
            if config.stream_type == "rtsp":
                cap = cv2.VideoCapture(config.source)
            elif config.stream_type == "file":
                cap = cv2.VideoCapture(config.source)
            elif config.stream_type == "camera":
                cap = cv2.VideoCapture(int(config.source))
            else:
                logger.error(f"Unsupported stream type: {config.stream_type}")
                return
            
            if not cap.isOpened():
                logger.error(f"Failed to open stream {stream_id}: {config.source}")
                return
            
            # Set resolution if specified
            if config.resolution:
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.resolution[0])
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.resolution[1])
            
            # Set FPS if specified
            if config.fps:
                cap.set(cv2.CAP_PROP_FPS, config.fps)
            
            # Set buffer size
            if config.buffer_size:
                cap.set(cv2.CAP_PROP_BUFFERSIZE, config.buffer_size)
            
            frame_count = 0
            last_processed_frame = 0
            
            while self.is_running and stream_id in self.tasks:
                try:
                    # Read frame
                    ret, frame = cap.read()
                    
                    if not ret:
                        stats.dropped_frames += 1
                        await asyncio.sleep(0.01)
                        continue
                    
                    stats.total_frames += 1
                    stats.last_frame_time = datetime.utcnow()
                    
                    # Skip frames if configured
                    if config.process_every_nth_frame > 1:
                        if frame_count % config.process_every_nth_frame != 0:
                            stats.skipped_frames += 1
                            frame_count += 1
                            continue
                    
                    # Process the frame
                    await self._process_frame(stream_id, frame, frame_count)
                    
                    stats.processed_frames += 1
                    last_processed_frame = frame_count
                    frame_count += 1
                    
                    # Calculate FPS
                    if frame_count % 10 == 0:
                        elapsed = (datetime.utcnow() - stats.started_at).total_seconds()
                        stats.avg_fps = frame_count / elapsed if elapsed > 0 else 0
                    
                    # Small delay to maintain frame rate
                    await asyncio.sleep(0.001)
                    
                except Exception as e:
                    logger.error(f"Error processing stream {stream_id}: {e}")
                    break
            
        except Exception as e:
            logger.error(f"Stream {stream_id} error: {e}")
        finally:
            if cap:
                cap.release()
            
            logger.info(f"Stream {stream_id} stopped")
    
    async def _process_frame(self, stream_id: str, frame: np.ndarray, frame_count: int) -> None:
        """Process a single frame"""
        config = self.streams[stream_id]
        stats = self.stats[stream_id]
        
        try:
            # Convert frame to RGB
            if len(frame.shape) == 2:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            else:
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create metadata
            metadata = ImageMetadata(
                image_id=f"{stream_id}_frame_{frame_count}",
                entity_id=stream_id,
                entity_type="stream",
                camera_id=stream_id,
                image_type=ImageType.AERIAL,
                timestamp=datetime.utcnow(),
                width=frame.shape[1],
                height=frame.shape[0]
            )
            
            # Process with image processor
            if config.enable_object_detection or config.enable_anomaly_detection:
                # Convert to bytes
                _, buffer = cv2.imencode('.jpg', frame_rgb)
                image_bytes = buffer.tobytes()
                
                # Process image
                result = await self.image_processor.process_image(
                    image_bytes,
                    metadata
                )
                
                # Update tracked objects
                if config.enable_tracking:
                    await self._update_tracked_objects(stream_id, result.objects, frame_count)
                
                # Update stats
                stats.total_objects += len(result.objects)
                stats.total_anomalies += len(result.anomalies)
                
                # Notify callbacks
                await self._notify_callbacks(stream_id, result, frame_rgb)
            
            # Save frame if configured
            if config.save_frames:
                self._save_frame(stream_id, frame_count, frame_rgb)
            
        except Exception as e:
            logger.error(f"Error processing frame {frame_count} from {stream_id}: {e}")
    
    async def _update_tracked_objects(self, stream_id: str, objects: List, frame_count: int) -> None:
        """Update tracked objects with new detections"""
        tracked = self.tracked_objects[stream_id]
        
        # Simple tracking - match objects by position
        for obj in objects:
            # Calculate center
            center_x = obj.bounding_box[0] + obj.bounding_box[2] / 2
            center_y = obj.bounding_box[1] + obj.bounding_box[3] / 2
            
            # Find closest existing track
            closest_track_id = None
            min_distance = float('inf')
            
            for track_id, track in tracked.items():
                if track.class_id == obj.class_id:
                    # Calculate distance to last position
                    if track.trajectory:
                        last_x, last_y = track.trajectory[-1]
                        distance = math.sqrt((center_x - last_x) ** 2 + (center_y - last_y) ** 2)
                        if distance < min_distance and distance < 50:  # 50px threshold
                            min_distance = distance
                            closest_track_id = track_id
            
            if closest_track_id:
                # Update existing track
                tracked[closest_track_id].update(obj.bounding_box, obj.confidence)
            else:
                # Create new track
                track_id = f"{stream_id}_track_{len(tracked)}"
                tracked[track_id] = TrackedObject(
                    track_id=track_id,
                    class_name=obj.class_name,
                    class_id=obj.class_id,
                    confidence=obj.confidence,
                    bounding_box=obj.bounding_box
                )
        
        # Remove old tracks (not seen for 30 frames)
        to_remove = []
        for track_id, track in tracked.items():
            if (datetime.utcnow() - track.last_seen).total_seconds() > 1:  # 1 second at 30fps
                to_remove.append(track_id)
        
        for track_id in to_remove:
            del tracked[track_id]
    
    async def _notify_callbacks(self, stream_id: str, result: ImageAnalysis, frame: np.ndarray) -> None:
        """Notify stream callbacks"""
        if stream_id in self.callbacks:
            for callback in self.callbacks[stream_id]:
                try:
                    await callback(stream_id, result, frame)
                except Exception as e:
                    logger.error(f"Callback error for {stream_id}: {e}")
    
    def _save_frame(self, stream_id: str, frame_count: int, frame: np.ndarray) -> None:
        """Save a frame to storage"""
        config = self.streams[stream_id]
        import os
        
        # Create directory if not exists
        os.makedirs(config.storage_path, exist_ok=True)
        
        # Save frame
        filename = f"{config.storage_path}/{stream_id}_frame_{frame_count:06d}.jpg"
        cv2.imwrite(filename, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
    
    def add_callback(self, stream_id: str, callback: Callable) -> None:
        """Add a callback for a specific stream"""
        if stream_id not in self.callbacks:
            self.callbacks[stream_id] = []
        self.callbacks[stream_id].append(callback)
        logger.info(f"Added callback for stream {stream_id}")
    
    def remove_callback(self, stream_id: str, callback: Callable) -> None:
        """Remove a callback from a stream"""
        if stream_id in self.callbacks and callback in self.callbacks[stream_id]:
            self.callbacks[stream_id].remove(callback)
            logger.info(f"Removed callback from stream {stream_id}")
    
    def get_stats(self, stream_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for a stream or all streams
        
        Args:
            stream_id: Specific stream ID or None for all streams
            
        Returns:
            Dictionary of statistics
        """
        if stream_id:
            if stream_id in self.stats:
                return self.stats[stream_id].to_dict()
            return {}
        
        return {sid: stats.to_dict() for sid, stats in self.stats.items()}
    
    def get_tracked_objects(self, stream_id: str) -> Dict[str, TrackedObject]:
        """Get all tracked objects for a stream"""
        return self.tracked_objects.get(stream_id, {}).copy()
    
    def get_object_trajectory(self, stream_id: str, track_id: str) -> List[Tuple[float, float]]:
        """Get trajectory for a tracked object"""
        tracked = self.tracked_objects.get(stream_id, {})
        obj = tracked.get(track_id)
        return obj.trajectory if obj else []
    
    async def start_helicopter_stream(self, helicopter: Helicopter, 
                                     camera: CameraSettings,
                                     callback: Optional[Callable] = None) -> str:
        """
        Start a video stream from a helicopter camera
        
        Args:
            helicopter: Helicopter object
            camera: Camera settings
            callback: Callback for processed frames
            
        Returns:
            Stream ID
        """
        stream_id = f"helicopter_{helicopter.helicopter_id}_cam_{camera.camera_id}"
        
        # Create stream config
        config = VideoStreamConfig(
            source=f"helicopter://{helicopter.helicopter_id}/{camera.camera_id}",
            stream_type="simulated",
            resolution=(camera.resolution.split('x')[0], camera.resolution.split('x')[1]),
            fps=camera.fps,
            enable_object_detection=True,
            enable_anomaly_detection=True,
            enable_tracking=True
        )
        
        # Register stream
        self.streams[stream_id] = config
        self.stats[stream_id] = StreamStats(stream_id=stream_id)
        self.tracked_objects[stream_id] = {}
        
        # Add callback if provided
        if callback:
            self.add_callback(stream_id, callback)
        
        # Start stream task
        task = asyncio.create_task(self._simulate_helicopter_stream(stream_id, helicopter, camera))
        self.tasks[stream_id] = task
        
        logger.info(f"Started helicopter stream {stream_id}")
        return stream_id
    
    async def _simulate_helicopter_stream(self, stream_id: str, helicopter: Helicopter, 
                                         camera: CameraSettings) -> None:
        """Simulate a helicopter video stream"""
        config = self.streams[stream_id]
        stats = self.stats[stream_id]
        
        frame_count = 0
        
        while self.is_running and stream_id in self.tasks:
            try:
                # Simulate frame capture
                frame = self._simulate_frame(helicopter, camera, frame_count)
                
                # Process frame
                await self._process_frame(stream_id, frame, frame_count)
                
                stats.total_frames += 1
                stats.processed_frames += 1
                frame_count += 1
                
                # Delay based on FPS
                await asyncio.sleep(1.0 / camera.fps)
                
            except Exception as e:
                logger.error(f"Error in simulated helicopter stream {stream_id}: {e}")
                break
    
    def _simulate_frame(self, helicopter: Helicopter, camera: CameraSettings, 
                       frame_count: int) -> np.ndarray:
        """Simulate a camera frame from a helicopter"""
        height = int(camera.resolution.split('x')[1])
        width = int(camera.resolution.split('x')[0])
        
        # Create a simple test frame
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add helicopter info
        cv2.putText(frame, f"H: {helicopter.helicopter_id}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Cam: {camera.camera_id}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Alt: {helicopter.location.altitude:.1f}m", (10, 90), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(frame, f"Spd: {helicopter.location.speed:.1f}km/h", (10, 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add some simulated objects
        if frame_count % 30 < 15:
            # Car
            cv2.rectangle(frame, (300, 200), (400, 300), (255, 0, 0), 2)
            cv2.putText(frame, "Car", (300, 190), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        if frame_count % 20 < 10:
            # Person
            cv2.rectangle(frame, (500, 250), (550, 350), (0, 255, 0), 2)
            cv2.putText(frame, "Person", (500, 240), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Add camera grid overlay (green and purple lines)
        if camera.night_vision or camera.thermal:
            # Add grid lines
            for i in range(0, width, width // 10):
                color = (0, 255, 0) if (i // (width // 10)) % 2 == 0 else (255, 0, 255)
                cv2.line(frame, (i, 0), (i, height), color, 1)
            for i in range(0, height, height // 10):
                color = (0, 255, 0) if (i // (height // 10)) % 2 == 0 else (255, 0, 255)
                cv2.line(frame, (0, i), (width, i), color, 1)
        
        return frame


# Import math for distance calculation
import math


# Create global video stream processor instance
video_processor = VideoStreamProcessor()

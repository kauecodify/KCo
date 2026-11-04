"""
H Module - Helicopter Service
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Business logic for helicopter operations
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple
import uuid

from ..models.helicopter import (
    Helicopter,
    HelicopterStatus,
    HelicopterModel,
    Location,
    EngineTelemetry,
    FuelSystem,
    HydraulicSystem,
    ElectricalSystem,
    CameraSettings,
    Mission,
    Pilot,
    MaintenanceLog,
    Alert
)
from ..models.telemetry import TelemetryPoint, TelemetrySource, TelemetryStream
from ..models.image_analysis import ImageAnalysis, ImageMetadata, ImageType
from ..geographic.gps_tracker import gps_tracker
from ..geographic.geofencing import geofencing_system
from ..control.fleet_manager import fleet_manager
from ..control.monitoring import monitoring_system
from ..control.alert_system import alert_system, AlertCategory, AlertPriority
from ..processing.aerial_image_processor import aerial_processor
from ..processing.video_stream_processor import video_processor
from ..cloud.cloud_sync import cloud_sync
from ..cloud.image_storage import image_storage
from .real_time_service import real_time_service

logger = logging.getLogger(__name__)


@dataclass
class HelicopterServiceConfig:
    """Configuration for helicopter service"""
    max_flight_time: float = 4.0  # hours
    max_fuel_consumption: float = 200.0  # liters/hour
    maintenance_interval: float = 100.0  # hours
    inspection_interval: float = 500.0  # hours
    min_fuel_for_takeoff: float = 20.0  # percentage
    max_altitude: float = 3000.0  # meters
    max_speed: float = 250.0  # km/h


@dataclass
class FlightPlan:
    """Flight plan for a helicopter"""
    flight_id: str
    helicopter_id: str
    mission_id: str
    waypoints: List[Dict[str, float]]
    altitude: float
    speed: float
    estimated_duration: float
    estimated_fuel: float
    pilot_id: str
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "flight_id": self.flight_id,
            "helicopter_id": self.helicopter_id,
            "mission_id": self.mission_id,
            "waypoints": self.waypoints,
            "altitude": self.altitude,
            "speed": self.speed,
            "estimated_duration": self.estimated_duration,
            "estimated_fuel": self.estimated_fuel,
            "pilot_id": self.pilot_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class HelicopterService:
    """
    Business logic service for helicopter operations
    
    Features:
    - Flight planning and management
    - Pre-flight checks
    - In-flight monitoring
    - Post-flight processing
    - Maintenance scheduling
    - Pilot management
    """
    
    def __init__(self, config: Optional[HelicopterServiceConfig] = None):
        """
        Initialize helicopter service
        
        Args:
            config: Service configuration
        """
        self.config = config or HelicopterServiceConfig()
        self.flight_plans: Dict[str, FlightPlan] = {}
        self.pilots: Dict[str, Pilot] = {}
        self.maintenance_schedules: Dict[str, List[MaintenanceLog]] = {}
        self.callbacks: Dict[str, List[Callable]] = {}
        
        logger.info("Helicopter Service initialized")
    
    async def start(self) -> None:
        """Start the helicopter service"""
        logger.info("Helicopter Service started")
    
    async def stop(self) -> None:
        """Stop the helicopter service"""
        logger.info("Helicopter Service stopped")
    
    def add_pilot(self, pilot: Pilot) -> None:
        """Add a pilot to the system"""
        self.pilots[pilot.pilot_id] = pilot
        logger.info(f"Added pilot {pilot.pilot_id}: {pilot.name}")
    
    def get_pilot(self, pilot_id: str) -> Optional[Pilot]:
        """Get a pilot by ID"""
        return self.pilots.get(pilot_id)
    
    def list_pilots(self) -> List[Pilot]:
        """List all pilots"""
        return list(self.pilots.values())
    
    def assign_pilot(self, helicopter_id: str, pilot_id: str) -> bool:
        """Assign a pilot to a helicopter"""
        helicopter = fleet_manager.get_helicopter(helicopter_id)
        pilot = self.get_pilot(pilot_id)
        
        if helicopter and pilot:
            helicopter.pilot = pilot
            logger.info(f"Assigned pilot {pilot_id} to helicopter {helicopter_id}")
            return True
        return False
    
    def create_flight_plan(self, helicopter_id: str, mission_id: str,
                         waypoints: List[Dict[str, float]], altitude: float,
                         speed: float, pilot_id: str) -> Optional[FlightPlan]:
        """
        Create a flight plan
        
        Args:
            helicopter_id: Helicopter ID
            mission_id: Mission ID
            waypoints: List of waypoints
            altitude: Flight altitude
            speed: Flight speed
            pilot_id: Pilot ID
            
        Returns:
            FlightPlan if created successfully
        """
        helicopter = fleet_manager.get_helicopter(helicopter_id)
        pilot = self.get_pilot(pilot_id)
        
        if not helicopter:
            logger.error(f"Helicopter {helicopter_id} not found")
            return None
        
        if not pilot:
            logger.error(f"Pilot {pilot_id} not found")
            return None
        
        # Calculate estimated duration and fuel
        estimated_duration = self._calculate_duration(waypoints, speed)
        estimated_fuel = self._calculate_fuel(helicopter, estimated_duration)
        
        # Check pre-flight conditions
        if not self._check_pre_flight(helicopter, estimated_fuel):
            logger.error("Pre-flight check failed")
            return None
        
        flight_id = str(uuid.uuid4())
        flight_plan = FlightPlan(
            flight_id=flight_id,
            helicopter_id=helicopter_id,
            mission_id=mission_id,
            waypoints=waypoints,
            altitude=altitude,
            speed=speed,
            estimated_duration=estimated_duration,
            estimated_fuel=estimated_fuel,
            pilot_id=pilot_id
        )
        
        self.flight_plans[flight_id] = flight_plan
        logger.info(f"Created flight plan {flight_id} for helicopter {helicopter_id}")
        
        return flight_plan
    
    def _calculate_duration(self, waypoints: List[Dict[str, float]], speed: float) -> float:
        """Calculate estimated flight duration"""
        if len(waypoints) < 2:
            return 0.0
        
        total_distance = 0.0
        for i in range(1, len(waypoints)):
            lat1 = waypoints[i-1]["latitude"]
            lng1 = waypoints[i-1]["longitude"]
            lat2 = waypoints[i]["latitude"]
            lng2 = waypoints[i]["longitude"]
            
            distance = self._haversine(lat1, lng1, lat2, lng2)
            total_distance += distance
        
        # Convert distance to hours (speed is in km/h, distance in meters)
        distance_km = total_distance / 1000
        return distance_km / speed
    
    def _calculate_fuel(self, helicopter: Helicopter, duration: float) -> float:
        """Calculate estimated fuel consumption"""
        # Use configured fuel consumption rate
        return self.config.max_fuel_consumption * duration
    
    def _check_pre_flight(self, helicopter: Helicopter, estimated_fuel: float) -> bool:
        """Perform pre-flight checks"""
        # Check fuel level
        fuel_percentage = (helicopter.fuel.level / helicopter.fuel.capacity) * 100
        if fuel_percentage < self.config.min_fuel_for_takeoff:
            logger.warning(f"Insufficient fuel: {fuel_percentage:.1f}% < {self.config.min_fuel_for_takeoff}%")
            return False
        
        # Check if fuel is enough for the flight
        if estimated_fuel > helicopter.fuel.level:
            logger.warning(f"Insufficient fuel for flight: {estimated_fuel:.1f}L > {helicopter.fuel.level:.1f}L")
            return False
        
        # Check maintenance status
        if helicopter.status == HelicopterStatus.MAINTENANCE:
            logger.warning("Helicopter is in maintenance")
            return False
        
        # Check engine hours
        if helicopter.engine.engine_hours > self.config.maintenance_interval:
            logger.warning("Helicopter needs maintenance")
            return False
        
        return True
    
    def start_flight(self, flight_id: str) -> bool:
        """Start a flight"""
        flight_plan = self.flight_plans.get(flight_id)
        if not flight_plan:
            logger.error(f"Flight plan {flight_id} not found")
            return False
        
        helicopter = fleet_manager.get_helicopter(flight_plan.helicopter_id)
        if not helicopter:
            logger.error(f"Helicopter {flight_plan.helicopter_id} not found")
            return False
        
        # Update flight plan status
        flight_plan.status = "in_progress"
        flight_plan.started_at = datetime.utcnow()
        
        # Update helicopter status
        fleet_manager.update_helicopter_status(helicopter.helicopter_id, HelicopterStatus.IN_FLIGHT)
        
        # Assign mission to helicopter
        mission = fleet_manager.missions.get(flight_plan.mission_id)
        if mission:
            helicopter.mission = mission
        
        # Assign pilot
        pilot = self.get_pilot(flight_plan.pilot_id)
        if pilot:
            helicopter.pilot = pilot
        
        logger.info(f"Started flight {flight_id} for helicopter {flight_plan.helicopter_id}")
        return True
    
    def complete_flight(self, flight_id: str) -> bool:
        """Complete a flight"""
        flight_plan = self.flight_plans.get(flight_id)
        if not flight_plan:
            logger.error(f"Flight plan {flight_id} not found")
            return False
        
        helicopter = fleet_manager.get_helicopter(flight_plan.helicopter_id)
        if not helicopter:
            logger.error(f"Helicopter {flight_plan.helicopter_id} not found")
            return False
        
        # Update flight plan status
        flight_plan.status = "completed"
        flight_plan.completed_at = datetime.utcnow()
        
        # Update helicopter status
        fleet_manager.update_helicopter_status(helicopter.helicopter_id, HelicopterStatus.GROUNDED)
        
        # Update engine hours
        duration = (datetime.utcnow() - flight_plan.started_at).total_seconds() / 3600
        helicopter.engine.engine_hours += duration
        
        # Update fuel level
        helicopter.fuel.level -= self.config.max_fuel_consumption * duration
        
        # Check for maintenance needs
        if helicopter.engine.engine_hours >= self.config.maintenance_interval:
            fleet_manager.update_helicopter_status(helicopter.helicopter_id, HelicopterStatus.MAINTENANCE)
            alert_system.create_alert(
                alert_type="maintenance_required",
                message=f"Helicopter {helicopter.helicopter_id} requires maintenance",
                entity_id=helicopter.helicopter_id,
                entity_type="helicopter",
                category=AlertCategory.MAINTENANCE,
                priority=AlertPriority.HIGH
            )
        
        logger.info(f"Completed flight {flight_id} for helicopter {flight_plan.helicopter_id}")
        return True
    
    def cancel_flight(self, flight_id: str) -> bool:
        """Cancel a flight"""
        flight_plan = self.flight_plans.get(flight_id)
        if not flight_plan:
            logger.error(f"Flight plan {flight_id} not found")
            return False
        
        flight_plan.status = "cancelled"
        logger.info(f"Cancelled flight {flight_id}")
        return True
    
    def get_flight_plan(self, flight_id: str) -> Optional[FlightPlan]:
        """Get a flight plan by ID"""
        return self.flight_plans.get(flight_id)
    
    def list_flight_plans(self, helicopter_id: Optional[str] = None) -> List[FlightPlan]:
        """List flight plans with optional filter"""
        if helicopter_id:
            return [fp for fp in self.flight_plans.values() if fp.helicopter_id == helicopter_id]
        return list(self.flight_plans.values())
    
    async def start_camera_stream(self, helicopter_id: str, camera_id: str,
                                  callback: Optional[Callable] = None) -> str:
        """
        Start a camera stream from a helicopter
        
        Args:
            helicopter_id: Helicopter ID
            camera_id: Camera ID
            callback: Callback for processed frames
            
        Returns:
            Stream ID
        """
        helicopter = fleet_manager.get_helicopter(helicopter_id)
        if not helicopter:
            raise ValueError(f"Helicopter {helicopter_id} not found")
        
        # Find camera
        camera = None
        for cam in helicopter.cameras:
            if cam.camera_id == camera_id:
                camera = cam
                break
        
        if not camera:
            raise ValueError(f"Camera {camera_id} not found on helicopter {helicopter_id}")
        
        # Start stream
        stream_id = await video_processor.start_helicopter_stream(helicopter, camera, callback)
        logger.info(f"Started camera stream {stream_id} for {helicopter_id}/{camera_id}")
        
        return stream_id
    
    async def stop_camera_stream(self, stream_id: str) -> None:
        """Stop a camera stream"""
        await video_processor.stop_stream(stream_id)
        logger.info(f"Stopped camera stream {stream_id}")
    
    async def capture_image(self, helicopter_id: str, camera_id: str) -> Optional[ImageData]:
        """
        Capture an image from a helicopter camera
        
        Args:
            helicopter_id: Helicopter ID
            camera_id: Camera ID
            
        Returns:
            ImageData if capture was successful
        """
        helicopter = fleet_manager.get_helicopter(helicopter_id)
        if not helicopter:
            logger.error(f"Helicopter {helicopter_id} not found")
            return None
        
        # Find camera
        camera = None
        for cam in helicopter.cameras:
            if cam.camera_id == camera_id:
                camera = cam
                break
        
        if not camera:
            logger.error(f"Camera {camera_id} not found on helicopter {helicopter_id}")
            return None
        
        # Simulate image capture
        import cv2
        import numpy as np
        
        # Create a test image
        height, width = 480, 640
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add some content
        cv2.putText(image, f"H: {helicopter.helicopter_id}", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.putText(image, f"Cam: {camera.camera_id}", (10, 60), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
        # Add grid overlay (green and purple lines)
        for i in range(0, width, width // 10):
            color = (0, 255, 0) if (i // (width // 10)) % 2 == 0 else (255, 0, 255)
            cv2.line(image, (i, 0), (i, height), color, 1)
        for i in range(0, height, height // 10):
            color = (0, 255, 0) if (i // (height // 10)) % 2 == 0 else (255, 0, 255)
            cv2.line(image, (0, i), (width, i), color, 1)
        
        # Encode as JPEG
        _, buffer = cv2.imencode('.jpg', image)
        image_bytes = buffer.tobytes()
        
        # Create metadata
        metadata = ImageMetadata(
            image_id=str(uuid.uuid4()),
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
        
        # Create ImageData
        from ..models.image_analysis import ImageData
        image_data = ImageData(metadata=metadata)
        image_data.set_image_data(image_bytes)
        
        # Save to storage
        await image_storage.save_image(image_data)
        
        logger.info(f"Captured image from {helicopter_id}/{camera_id}")
        return image_data
    
    async def process_image(self, image_data: ImageData) -> Optional[ImageAnalysis]:
        """
        Process an image from a helicopter
        
        Args:
            image_data: Image data to process
            
        Returns:
            ImageAnalysis result
        """
        try:
            # Process with aerial processor
            analysis = await aerial_processor.process_image(
                image_data.data,
                image_data.metadata
            )
            
            # Save analysis
            await cloud_sync.sync_analysis(analysis)
            
            logger.info(f"Processed image {image_data.metadata.image_id}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error processing image {image_data.metadata.image_id}: {e}")
            return None
    
    async def monitor_flight(self, flight_id: str) -> None:
        """Monitor a flight in real-time"""
        flight_plan = self.flight_plans.get(flight_id)
        if not flight_plan:
            logger.error(f"Flight plan {flight_id} not found")
            return
        
        helicopter = fleet_manager.get_helicopter(flight_plan.helicopter_id)
        if not helicopter:
            logger.error(f"Helicopter {flight_plan.helicopter_id} not found")
            return
        
        # Monitor the helicopter
        while flight_plan.status == "in_progress":
            try:
                # Check fuel level
                fuel_percentage = (helicopter.fuel.level / helicopter.fuel.capacity) * 100
                if fuel_percentage < 10:
                    alert_system.create_alert(
                        alert_type="low_fuel",
                        message=f"Low fuel: {fuel_percentage:.1f}%",
                        entity_id=helicopter.helicopter_id,
                        entity_type="helicopter",
                        category=AlertCategory.SAFETY,
                        priority=AlertPriority.CRITICAL
                    )
                
                # Check altitude
                if helicopter.location.altitude > self.config.max_altitude:
                    alert_system.create_alert(
                        alert_type="high_altitude",
                        message=f"High altitude: {helicopter.location.altitude:.1f}m",
                        entity_id=helicopter.helicopter_id,
                        entity_type="helicopter",
                        category=AlertCategory.SAFETY,
                        priority=AlertPriority.HIGH
                    )
                
                # Check speed
                if helicopter.location.speed > self.config.max_speed:
                    alert_system.create_alert(
                        alert_type="high_speed",
                        message=f"High speed: {helicopter.location.speed:.1f}km/h",
                        entity_id=helicopter.helicopter_id,
                        entity_type="helicopter",
                        category=AlertCategory.SAFETY,
                        priority=AlertPriority.HIGH
                    )
                
                # Small delay
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error monitoring flight {flight_id}: {e}")
                break
    
    def schedule_maintenance(self, helicopter_id: str, maintenance_type: str,
                            description: str, performed_by: str) -> bool:
        """Schedule maintenance for a helicopter"""
        helicopter = fleet_manager.get_helicopter(helicopter_id)
        if not helicopter:
            logger.error(f"Helicopter {helicopter_id} not found")
            return False
        
        maintenance_id = str(uuid.uuid4())
        maintenance = MaintenanceLog(
            log_id=maintenance_id,
            maintenance_type=maintenance_type,
            description=description,
            performed_date=datetime.utcnow(),
            next_due_date=datetime.utcnow(),
            hours_interval=self.config.maintenance_interval,
            performed_by=performed_by
        )
        
        helicopter.maintenance_logs.append(maintenance)
        
        # Update status if needed
        if maintenance_type == "major":
            fleet_manager.update_helicopter_status(helicopter_id, HelicopterStatus.MAINTENANCE)
        
        logger.info(f"Scheduled maintenance {maintenance_id} for helicopter {helicopter_id}")
        return True
    
    def get_maintenance_status(self, helicopter_id: str) -> Dict[str, Any]:
        """Get maintenance status for a helicopter"""
        helicopter = fleet_manager.get_helicopter(helicopter_id)
        if not helicopter:
            return {}
        
        return {
            "engine_hours": helicopter.engine.engine_hours,
            "next_maintenance": self.config.maintenance_interval - helicopter.engine.engine_hours,
            "next_inspection": self.config.inspection_interval - helicopter.engine.engine_hours,
            "maintenance_logs": len(helicopter.maintenance_logs)
        }
    
    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance using Haversine formula"""
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_phi / 2) ** 2) + \
            math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def add_callback(self, event_type: str, callback: Callable) -> None:
        """Add a callback for specific events"""
        if event_type not in self.callbacks:
            self.callbacks[event_type] = []
        self.callbacks[event_type].append(callback)
        logger.info(f"Added callback for {event_type}")
    
    def remove_callback(self, event_type: str, callback: Callable) -> None:
        """Remove a callback"""
        if event_type in self.callbacks and callback in self.callbacks[event_type]:
            self.callbacks[event_type].remove(callback)
            logger.info(f"Removed callback for {event_type}")


# Import math for distance calculation
import math


# Create global helicopter service instance
helicopter_service = HelicopterService()

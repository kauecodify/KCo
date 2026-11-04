"""
H Module - GPS Tracker
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

GPS tracking system for helicopters and vehicles
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple
import random
import math

from ..models.helicopter import Helicopter, HelicopterStatus, Location
from ..models.vehicle import Vehicle, VehicleStatus, VehicleLocation
from ..models.telemetry import TelemetryPoint, TelemetrySource, DataQuality

logger = logging.getLogger(__name__)


@dataclass
class GPSSatellite:
    """GPS satellite information"""
    prn: int
    azimuth: float
    elevation: float
    signal_strength: float
    used: bool = True


@dataclass
class GPSFix:
    """GPS fix information"""
    latitude: float
    longitude: float
    altitude: float
    accuracy: float
    satellites: List[GPSSatellite] = field(default_factory=list)
    hdop: float = 0.0
    vdop: float = 0.0
    pdop: float = 0.0
    fix_type: str = "3D"
    timestamp: datetime = field(default_factory=datetime.utcnow)


class GPSTracker:
    """
    GPS tracking system for helicopters and vehicles
    
    Features:
    - Real-time GPS position tracking
    - Multi-constellation support (GPS, GLONASS, Galileo, BeiDou)
    - Signal quality monitoring
    - Geofencing support
    - Movement detection
    - Speed and heading calculation
    """
    
    def __init__(self, update_interval: float = 1.0):
        """
        Initialize GPS tracker
        
        Args:
            update_interval: Update interval in seconds
        """
        self.update_interval = update_interval
        self.is_running = False
        self.entities: Dict[str, Dict[str, Any]] = {}
        self.callbacks: List[Callable] = []
        self.geofences: Dict[str, Dict[str, Any]] = {}
        self.simulate = True
        
        logger.info(f"GPS Tracker initialized with {update_interval}s update interval")
    
    async def start(self) -> None:
        """Start GPS tracking"""
        if self.is_running:
            logger.warning("GPS Tracker is already running")
            return
        
        self.is_running = True
        logger.info("GPS Tracker started")
        
        while self.is_running:
            await self._update_positions()
            await asyncio.sleep(self.update_interval)
    
    async def stop(self) -> None:
        """Stop GPS tracking"""
        self.is_running = False
        logger.info("GPS Tracker stopped")
    
    async def _update_positions(self) -> None:
        """Update positions for all tracked entities"""
        for entity_id, entity_data in self.entities.items():
            try:
                if self.simulate:
                    await self._simulate_position(entity_id, entity_data)
                else:
                    await self._read_real_position(entity_id, entity_data)
                
                # Notify callbacks
                for callback in self.callbacks:
                    try:
                        await callback(entity_id, entity_data)
                    except Exception as e:
                        logger.error(f"Callback error for {entity_id}: {e}")
                        
            except Exception as e:
                logger.error(f"Error updating position for {entity_id}: {e}")
    
    async def _simulate_position(self, entity_id: str, entity_data: Dict[str, Any]) -> None:
        """Simulate position updates for testing"""
        entity_type = entity_data.get("type", "vehicle")
        
        # Get current position
        if entity_type == "helicopter":
            current_lat = entity_data.get("location", {}).get("latitude", -23.5505)
            current_lng = entity_data.get("location", {}).get("longitude", -46.6333)
            current_alt = entity_data.get("location", {}).get("altitude", 0.0)
            current_heading = entity_data.get("location", {}).get("heading", 0.0)
            current_speed = entity_data.get("location", {}).get("speed", 0.0)
            status = entity_data.get("status", HelicopterStatus.GROUNDED.value)
            
            # Simulate movement based on status
            if status == HelicopterStatus.IN_FLIGHT.value:
                # Helicopter in flight - move in a pattern
                angle = datetime.utcnow().timestamp() * 0.1
                lat_offset = math.sin(angle) * 0.01
                lng_offset = math.cos(angle) * 0.01
                new_lat = current_lat + lat_offset
                new_lng = current_lng + lng_offset
                new_alt = 500 + math.sin(angle * 2) * 100
                new_heading = (current_heading + 5) % 360
                new_speed = 120 + random.uniform(-10, 10)
                
            elif status == HelicopterStatus.TAXIING.value:
                # Taxiing - slow movement
                new_lat = current_lat + random.uniform(-0.0001, 0.0001)
                new_lng = current_lng + random.uniform(-0.0001, 0.0001)
                new_alt = current_alt
                new_heading = (current_heading + random.uniform(-10, 10)) % 360
                new_speed = random.uniform(0, 20)
                
            else:
                # Grounded - small position variations
                new_lat = current_lat + random.uniform(-0.00001, 0.00001)
                new_lng = current_lng + random.uniform(-0.00001, 0.00001)
                new_alt = current_alt
                new_heading = current_heading
                new_speed = 0
            
            # Update entity data
            entity_data["location"] = {
                "latitude": new_lat,
                "longitude": new_lng,
                "altitude": new_alt,
                "heading": new_heading,
                "speed": new_speed,
                "accuracy": random.uniform(1, 5),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Create telemetry point
            telemetry = TelemetryPoint(
                timestamp=datetime.utcnow(),
                source=TelemetrySource.GPS,
                source_id=entity_id,
                value=new_speed,
                unit="km/h",
                quality=DataQuality.GOOD,
                processed=False
            )
            entity_data.setdefault("telemetry", []).append(telemetry)
            
        else:  # Vehicle
            current_lat = entity_data.get("location", {}).get("latitude", -23.5505)
            current_lng = entity_data.get("location", {}).get("longitude", -46.6333)
            current_alt = entity_data.get("location", {}).get("altitude", 0.0)
            current_heading = entity_data.get("location", {}).get("heading", 0.0)
            current_speed = entity_data.get("location", {}).get("speed", 0.0)
            status = entity_data.get("status", VehicleStatus.PARKED.value)
            
            # Simulate movement based on status
            if status == VehicleStatus.DRIVING.value:
                # Driving - move along a route
                angle = datetime.utcnow().timestamp() * 0.05
                lat_offset = math.sin(angle) * 0.001
                lng_offset = math.cos(angle) * 0.001
                new_lat = current_lat + lat_offset
                new_lng = current_lng + lng_offset
                new_alt = current_alt
                new_heading = (current_heading + random.uniform(-5, 5)) % 360
                new_speed = 60 + random.uniform(-10, 10)
                
            elif status == VehicleStatus.IDLE.value:
                # Idle - small movements
                new_lat = current_lat + random.uniform(-0.00005, 0.00005)
                new_lng = current_lng + random.uniform(-0.00005, 0.00005)
                new_alt = current_alt
                new_heading = current_heading
                new_speed = random.uniform(0, 5)
                
            else:
                # Parked - minimal movement
                new_lat = current_lat + random.uniform(-0.000001, 0.000001)
                new_lng = current_lng + random.uniform(-0.000001, 0.000001)
                new_alt = current_alt
                new_heading = current_heading
                new_speed = 0
            
            # Update entity data
            entity_data["location"] = {
                "latitude": new_lat,
                "longitude": new_lng,
                "altitude": new_alt,
                "heading": new_heading,
                "speed": new_speed,
                "accuracy": random.uniform(1, 10),
                "gps_fix": True,
                "satellites": random.randint(6, 12),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Create telemetry point
            telemetry = TelemetryPoint(
                timestamp=datetime.utcnow(),
                source=TelemetrySource.GPS,
                source_id=entity_id,
                value=new_speed,
                unit="km/h",
                quality=DataQuality.GOOD,
                processed=False
            )
            entity_data.setdefault("telemetry", []).append(telemetry)
    
    async def _read_real_position(self, entity_id: str, entity_data: Dict[str, Any]) -> None:
        """Read real GPS position (placeholder for actual implementation)"""
        # This would be replaced with actual GPS hardware integration
        logger.warning(f"Real GPS reading not implemented for {entity_id}")
    
    def add_entity(self, entity_id: str, entity_type: str, initial_location: Dict[str, float], 
                   status: str = "parked") -> None:
        """
        Add an entity to track
        
        Args:
            entity_id: Unique identifier for the entity
            entity_type: Type of entity (helicopter or vehicle)
            initial_location: Initial location with lat, lng, alt
            status: Initial status
        """
        self.entities[entity_id] = {
            "type": entity_type,
            "location": {
                "latitude": initial_location.get("latitude", 0.0),
                "longitude": initial_location.get("longitude", 0.0),
                "altitude": initial_location.get("altitude", 0.0),
                "heading": initial_location.get("heading", 0.0),
                "speed": initial_location.get("speed", 0.0),
                "accuracy": 0.0,
                "timestamp": datetime.utcnow().isoformat()
            },
            "status": status,
            "telemetry": []
        }
        logger.info(f"Added {entity_type} {entity_id} to GPS tracking")
    
    def remove_entity(self, entity_id: str) -> None:
        """Remove an entity from tracking"""
        if entity_id in self.entities:
            del self.entities[entity_id]
            logger.info(f"Removed {entity_id} from GPS tracking")
    
    def get_position(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get current position of an entity"""
        entity_data = self.entities.get(entity_id)
        if entity_data:
            return entity_data.get("location")
        return None
    
    def get_entities_in_area(self, min_lat: float, min_lng: float, max_lat: float, 
                            max_lng: float) -> List[str]:
        """Get all entities within a geographic area"""
        result = []
        for entity_id, entity_data in self.entities.items():
            location = entity_data.get("location", {})
            lat = location.get("latitude", 0.0)
            lng = location.get("longitude", 0.0)
            if (min_lat <= lat <= max_lat) and (min_lng <= lng <= max_lng):
                result.append(entity_id)
        return result
    
    def add_geofence(self, geofence_id: str, name: str, center: Tuple[float, float], 
                     radius: float, callback: Optional[Callable] = None) -> None:
        """
        Add a geofence
        
        Args:
            geofence_id: Unique identifier
            name: Geofence name
            center: Center coordinates (lat, lng)
            radius: Radius in meters
            callback: Callback to trigger when entity enters/exits geofence
        """
        self.geofences[geofence_id] = {
            "name": name,
            "center": {"latitude": center[0], "longitude": center[1]},
            "radius": radius,
            "callback": callback
        }
        logger.info(f"Added geofence {geofence_id}: {name}")
    
    def check_geofences(self, entity_id: str, location: Dict[str, float]) -> List[str]:
        """
        Check which geofences an entity is in
        
        Args:
            entity_id: Entity ID
            location: Current location
            
        Returns:
            List of geofence IDs the entity is currently in
        """
        lat = location.get("latitude", 0.0)
        lng = location.get("longitude", 0.0)
        result = []
        
        for geofence_id, geofence in self.geofences.items():
            center = geofence.get("center", {})
            center_lat = center.get("latitude", 0.0)
            center_lng = center.get("longitude", 0.0)
            radius = geofence.get("radius", 0.0)
            
            # Calculate distance using Haversine formula
            distance = self._haversine(lat, lng, center_lat, center_lng)
            if distance <= radius:
                result.append(geofence_id)
        
        return result
    
    def _haversine(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_phi / 2) ** 2) + \
            math.cos(phi1) * math.cos(phi2) * (math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def add_callback(self, callback: Callable) -> None:
        """Add a callback for position updates"""
        self.callbacks.append(callback)
        logger.info("Added position update callback")
    
    def remove_callback(self, callback: Callable) -> None:
        """Remove a callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            logger.info("Removed position update callback")
    
    def get_telemetry(self, entity_id: str, limit: int = 100) -> List[TelemetryPoint]:
        """Get telemetry data for an entity"""
        entity_data = self.entities.get(entity_id, {})
        telemetry = entity_data.get("telemetry", [])
        return telemetry[-limit:] if telemetry else []
    
    def get_speed_and_heading(self, entity_id: str) -> Tuple[float, float]:
        """Get current speed and heading for an entity"""
        location = self.get_position(entity_id)
        if location:
            return location.get("speed", 0.0), location.get("heading", 0.0)
        return 0.0, 0.0
    
    def calculate_distance(self, entity_id1: str, entity_id2: str) -> float:
        """Calculate distance between two entities"""
        pos1 = self.get_position(entity_id1)
        pos2 = self.get_position(entity_id2)
        
        if pos1 and pos2:
            lat1 = pos1.get("latitude", 0.0)
            lng1 = pos1.get("longitude", 0.0)
            lat2 = pos2.get("latitude", 0.0)
            lng2 = pos2.get("longitude", 0.0)
            return self._haversine(lat1, lng1, lat2, lng2)
        return 0.0
    
    def get_entities_by_status(self, status: str) -> List[str]:
        """Get all entities with a specific status"""
        result = []
        for entity_id, entity_data in self.entities.items():
            if entity_data.get("status") == status:
                result.append(entity_id)
        return result
    
    def get_entities_in_flight(self) -> List[str]:
        """Get all helicopters currently in flight"""
        return self.get_entities_by_status(HelicopterStatus.IN_FLIGHT.value)
    
    def get_entities_driving(self) -> List[str]:
        """Get all vehicles currently driving"""
        return self.get_entities_by_status(VehicleStatus.DRIVING.value)


class MultiConstellationGPS:
    """
    Multi-constellation GPS receiver support
    
    Supports:
    - GPS (United States)
    - GLONASS (Russia)
    - Galileo (European Union)
    - BeiDou (China)
    - SBAS (Satellite-Based Augmentation Systems)
    """
    
    def __init__(self):
        self.constellations = {
            "gps": {"enabled": True, "satellites": 0},
            "glonass": {"enabled": True, "satellites": 0},
            "galileo": {"enabled": True, "satellites": 0},
            "beidou": {"enabled": True, "satellites": 0},
            "sbas": {"enabled": True, "satellites": 0}
        }
        self.total_satellites = 0
        self.fix_type = "No Fix"
        self.accuracy = 0.0
    
    def update_satellite_status(self, constellation: str, satellites: int) -> None:
        """Update satellite count for a constellation"""
        if constellation in self.constellations:
            self.constellations[constellation]["satellites"] = satellites
            self.total_satellites = sum(
                c["satellites"] for c in self.constellations.values()
            )
            self._update_fix_type()
    
    def _update_fix_type(self) -> None:
        """Update fix type based on satellite count"""
        if self.total_satellites >= 8:
            self.fix_type = "3D Fix"
            self.accuracy = 1.0
        elif self.total_satellites >= 4:
            self.fix_type = "2D Fix"
            self.accuracy = 5.0
        elif self.total_satellites >= 3:
            self.fix_type = "Weak Fix"
            self.accuracy = 10.0
        else:
            self.fix_type = "No Fix"
            self.accuracy = 0.0
    
    def get_status(self) -> Dict[str, Any]:
        """Get current GPS status"""
        return {
            "constellations": self.constellations,
            "total_satellites": self.total_satellites,
            "fix_type": self.fix_type,
            "accuracy": self.accuracy
        }
    
    def enable_constellation(self, constellation: str) -> None:
        """Enable a GPS constellation"""
        if constellation in self.constellations:
            self.constellations[constellation]["enabled"] = True
    
    def disable_constellation(self, constellation: str) -> None:
        """Disable a GPS constellation"""
        if constellation in self.constellations:
            self.constellations[constellation]["enabled"] = False


# Create global GPS tracker instance
gps_tracker = GPSTracker()

"""
H Module - Geofencing System
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Geofencing system for geographic boundaries and alerts
"""

import logging
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple
import asyncio
import uuid

from .gps_tracker import GPSTracker, gps_tracker
from ..models.helicopter import HelicopterStatus
from ..models.vehicle import VehicleStatus

logger = logging.getLogger(__name__)


@dataclass
class Geofence:
    """
    Geofence definition
    
    Attributes:
        geofence_id: Unique identifier
        name: Geofence name
        geofence_type: Type of geofence (circle, polygon, rectangle)
        center: Center coordinates (lat, lng)
        radius: Radius in meters (for circle)
        vertices: List of vertices for polygon
        min_lat: Minimum latitude (for rectangle)
        max_lat: Maximum latitude (for rectangle)
        min_lng: Minimum longitude (for rectangle)
        max_lng: Maximum longitude (for rectangle)
        is_active: Whether geofence is active
        alert_on_entry: Whether to alert on entry
        alert_on_exit: Whether to alert on exit
        alert_on_inside: Whether to alert while inside
        created_at: Timestamp of creation
        updated_at: Timestamp of last update
    """
    geofence_id: str
    name: str
    geofence_type: str = "circle"
    center: Tuple[float, float] = (0.0, 0.0)
    radius: float = 1000.0
    vertices: List[Tuple[float, float]] = field(default_factory=list)
    min_lat: float = 0.0
    max_lat: float = 0.0
    min_lng: float = 0.0
    max_lng: float = 0.0
    is_active: bool = True
    alert_on_entry: bool = True
    alert_on_exit: bool = True
    alert_on_inside: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def contains(self, lat: float, lng: float) -> bool:
        """Check if a point is inside the geofence"""
        if self.geofence_type == "circle":
            return self._contains_circle(lat, lng)
        elif self.geofence_type == "polygon":
            return self._contains_polygon(lat, lng)
        elif self.geofence_type == "rectangle":
            return self._contains_rectangle(lat, lng)
        return False
    
    def _contains_circle(self, lat: float, lng: float) -> bool:
        """Check if point is inside circular geofence"""
        distance = self._haversine(lat, lng, self.center[0], self.center[1])
        return distance <= self.radius
    
    def _contains_polygon(self, lat: float, lng: float) -> bool:
        """Check if point is inside polygon geofence using ray casting"""
        if len(self.vertices) < 3:
            return False
        
        x = lng
        y = lat
        inside = False
        
        for i in range(len(self.vertices)):
            j = (i + 1) % len(self.vertices)
            xi = self.vertices[i][1]
            yi = self.vertices[i][0]
            xj = self.vertices[j][1]
            yj = self.vertices[j][0]
            
            intersect = ((yi > y) != (yj > y)) and \
                        (x < (xj - xi) * (y - yi) / (yj - yi) + xi)
            if intersect:
                inside = not inside
        
        return inside
    
    def _contains_rectangle(self, lat: float, lng: float) -> bool:
        """Check if point is inside rectangular geofence"""
        return (self.min_lat <= lat <= self.max_lat and 
                self.min_lng <= lng <= self.max_lng)
    
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "geofence_id": self.geofence_id,
            "name": self.name,
            "geofence_type": self.geofence_type,
            "center": {"latitude": self.center[0], "longitude": self.center[1]},
            "radius": self.radius,
            "vertices": [{"latitude": v[0], "longitude": v[1]} for v in self.vertices],
            "min_lat": self.min_lat,
            "max_lat": self.max_lat,
            "min_lng": self.min_lng,
            "max_lng": self.max_lng,
            "is_active": self.is_active,
            "alert_on_entry": self.alert_on_entry,
            "alert_on_exit": self.alert_on_exit,
            "alert_on_inside": self.alert_on_inside,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


@dataclass
class GeofenceAlert:
    """
    Geofence alert
    
    Attributes:
        alert_id: Unique identifier
        geofence_id: ID of the geofence
        entity_id: ID of the entity
        entity_type: Type of entity
        alert_type: Type of alert (entry, exit, inside)
        timestamp: Timestamp of the alert
        location: Location where alert occurred
        acknowledged: Whether alert has been acknowledged
        acknowledged_by: Who acknowledged the alert
        acknowledged_at: When alert was acknowledged
    """
    alert_id: str
    geofence_id: str
    entity_id: str
    entity_type: str
    alert_type: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    location: Dict[str, float] = field(default_factory=dict)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "geofence_id": self.geofence_id,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "alert_type": self.alert_type,
            "timestamp": self.timestamp.isoformat(),
            "location": self.location,
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None
        }


@dataclass
class EntityGeofenceState:
    """
    Track geofence state for an entity
    
    Attributes:
        entity_id: ID of the entity
        geofence_id: ID of the geofence
        inside: Whether entity is currently inside
        entry_time: When entity entered
        exit_time: When entity exited
        last_alert: Last alert timestamp
    """
    entity_id: str
    geofence_id: str
    inside: bool = False
    entry_time: Optional[datetime] = None
    exit_time: Optional[datetime] = None
    last_alert: Optional[datetime] = None


class GeofencingSystem:
    """
    Geofencing system for managing geographic boundaries
    
    Features:
    - Create and manage geofences
    - Monitor entities in real-time
    - Generate alerts on entry/exit
    - Track geofence state history
    """
    
    def __init__(self, gps_tracker: Optional[GPSTracker] = None):
        """
        Initialize geofencing system
        
        Args:
            gps_tracker: GPS tracker instance
        """
        self.geofences: Dict[str, Geofence] = {}
        self.entity_states: Dict[str, Dict[str, EntityGeofenceState]] = {}
        self.alerts: Dict[str, GeofenceAlert] = {}
        self.alert_callbacks: List[Callable] = []
        self.gps_tracker = gps_tracker or gps_tracker
        self.is_running = False
        self.check_interval = 5.0  # seconds
        
        logger.info("Geofencing System initialized")
    
    async def start(self) -> None:
        """Start geofencing monitoring"""
        if self.is_running:
            logger.warning("Geofencing System is already running")
            return
        
        self.is_running = True
        logger.info("Geofencing System started")
        
        while self.is_running:
            await self._check_entities()
            await asyncio.sleep(self.check_interval)
    
    async def stop(self) -> None:
        """Stop geofencing monitoring"""
        self.is_running = False
        logger.info("Geofencing System stopped")
    
    async def _check_entities(self) -> None:
        """Check all entities against all geofences"""
        if not self.gps_tracker:
            return
        
        for entity_id, entity_data in self.gps_tracker.entities.items():
            location = entity_data.get("location", {})
            lat = location.get("latitude", 0.0)
            lng = location.get("longitude", 0.0)
            entity_type = entity_data.get("type", "vehicle")
            
            for geofence_id, geofence in self.geofences.items():
                if not geofence.is_active:
                    continue
                
                # Initialize state if not exists
                if entity_id not in self.entity_states:
                    self.entity_states[entity_id] = {}
                if geofence_id not in self.entity_states[entity_id]:
                    self.entity_states[entity_id][geofence_id] = EntityGeofenceState(
                        entity_id=entity_id,
                        geofence_id=geofence_id
                    )
                
                state = self.entity_states[entity_id][geofence_id]
                inside = geofence.contains(lat, lng)
                
                # Check for state changes
                if inside and not state.inside:
                    # Entry
                    state.inside = True
                    state.entry_time = datetime.utcnow()
                    state.exit_time = None
                    
                    if geofence.alert_on_entry:
                        await self._generate_alert(
                            geofence_id, entity_id, entity_type, "entry", lat, lng
                        )
                    
                elif not inside and state.inside:
                    # Exit
                    state.inside = False
                    state.exit_time = datetime.utcnow()
                    
                    if geofence.alert_on_exit:
                        await self._generate_alert(
                            geofence_id, entity_id, entity_type, "exit", lat, lng
                        )
                    
                elif inside and state.inside and geofence.alert_on_inside:
                    # Inside and alert on inside enabled
                    # Only alert every 5 minutes to avoid spam
                    if (not state.last_alert or 
                        (datetime.utcnow() - state.last_alert).total_seconds() >= 300):
                        await self._generate_alert(
                            geofence_id, entity_id, entity_type, "inside", lat, lng
                        )
                        state.last_alert = datetime.utcnow()
    
    async def _generate_alert(self, geofence_id: str, entity_id: str, entity_type: str,
                              alert_type: str, lat: float, lng: float) -> None:
        """Generate a geofence alert"""
        alert_id = str(uuid.uuid4())
        alert = GeofenceAlert(
            alert_id=alert_id,
            geofence_id=geofence_id,
            entity_id=entity_id,
            entity_type=entity_type,
            alert_type=alert_type,
            timestamp=datetime.utcnow(),
            location={"latitude": lat, "longitude": lng}
        )
        
        self.alerts[alert_id] = alert
        logger.info(f"Geofence alert: {alert_type} for {entity_type} {entity_id} in {geofence_id}")
        
        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                await callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def create_circle_geofence(self, name: str, center: Tuple[float, float], 
                               radius: float, **kwargs) -> Geofence:
        """
        Create a circular geofence
        
        Args:
            name: Geofence name
            center: Center coordinates (lat, lng)
            radius: Radius in meters
            **kwargs: Additional geofence properties
            
        Returns:
            Created geofence
        """
        geofence_id = str(uuid.uuid4())
        geofence = Geofence(
            geofence_id=geofence_id,
            name=name,
            geofence_type="circle",
            center=center,
            radius=radius,
            **kwargs
        )
        self.geofences[geofence_id] = geofence
        logger.info(f"Created circular geofence {geofence_id}: {name}")
        return geofence
    
    def create_rectangle_geofence(self, name: str, min_lat: float, min_lng: float,
                                  max_lat: float, max_lng: float, **kwargs) -> Geofence:
        """
        Create a rectangular geofence
        
        Args:
            name: Geofence name
            min_lat: Minimum latitude
            min_lng: Minimum longitude
            max_lat: Maximum latitude
            max_lng: Maximum longitude
            **kwargs: Additional geofence properties
            
        Returns:
            Created geofence
        """
        geofence_id = str(uuid.uuid4())
        center = ((min_lat + max_lat) / 2, (min_lng + max_lng) / 2)
        geofence = Geofence(
            geofence_id=geofence_id,
            name=name,
            geofence_type="rectangle",
            center=center,
            min_lat=min_lat,
            max_lat=max_lat,
            min_lng=min_lng,
            max_lng=max_lng,
            **kwargs
        )
        self.geofences[geofence_id] = geofence
        logger.info(f"Created rectangular geofence {geofence_id}: {name}")
        return geofence
    
    def create_polygon_geofence(self, name: str, vertices: List[Tuple[float, float]],
                                **kwargs) -> Geofence:
        """
        Create a polygon geofence
        
        Args:
            name: Geofence name
            vertices: List of vertex coordinates (lat, lng)
            **kwargs: Additional geofence properties
            
        Returns:
            Created geofence
        """
        geofence_id = str(uuid.uuid4())
        
        # Calculate center
        center_lat = sum(v[0] for v in vertices) / len(vertices)
        center_lng = sum(v[1] for v in vertices) / len(vertices)
        
        geofence = Geofence(
            geofence_id=geofence_id,
            name=name,
            geofence_type="polygon",
            center=(center_lat, center_lng),
            vertices=vertices,
            **kwargs
        )
        self.geofences[geofence_id] = geofence
        logger.info(f"Created polygon geofence {geofence_id}: {name}")
        return geofence
    
    def delete_geofence(self, geofence_id: str) -> bool:
        """Delete a geofence"""
        if geofence_id in self.geofences:
            del self.geofences[geofence_id]
            logger.info(f"Deleted geofence {geofence_id}")
            return True
        return False
    
    def get_geofence(self, geofence_id: str) -> Optional[Geofence]:
        """Get a geofence by ID"""
        return self.geofences.get(geofence_id)
    
    def list_geofences(self) -> List[Geofence]:
        """List all geofences"""
        return list(self.geofences.values())
    
    def get_entities_in_geofence(self, geofence_id: str) -> List[str]:
        """Get all entities currently in a geofence"""
        geofence = self.geofences.get(geofence_id)
        if not geofence:
            return []
        
        result = []
        if self.gps_tracker:
            for entity_id, entity_data in self.gps_tracker.entities.items():
                location = entity_data.get("location", {})
                lat = location.get("latitude", 0.0)
                lng = location.get("longitude", 0.0)
                if geofence.contains(lat, lng):
                    result.append(entity_id)
        return result
    
    def get_entity_geofences(self, entity_id: str) -> List[str]:
        """Get all geofences an entity is currently in"""
        if self.gps_tracker:
            location = self.gps_tracker.get_position(entity_id)
            if location:
                lat = location.get("latitude", 0.0)
                lng = location.get("longitude", 0.0)
                return [
                    geofence_id for geofence_id, geofence in self.geofences.items()
                    if geofence.is_active and geofence.contains(lat, lng)
                ]
        return []
    
    def get_alerts(self, entity_id: Optional[str] = None, 
                   geofence_id: Optional[str] = None, 
                   acknowledged: Optional[bool] = None) -> List[GeofenceAlert]:
        """
        Get geofence alerts with optional filters
        
        Args:
            entity_id: Filter by entity ID
            geofence_id: Filter by geofence ID
            acknowledged: Filter by acknowledged status
            
        Returns:
            List of matching alerts
        """
        result = []
        for alert in self.alerts.values():
            if entity_id and alert.entity_id != entity_id:
                continue
            if geofence_id and alert.geofence_id != geofence_id:
                continue
            if acknowledged is not None and alert.acknowledged != acknowledged:
                continue
            result.append(alert)
        
        # Sort by timestamp (newest first)
        result.sort(key=lambda x: x.timestamp, reverse=True)
        return result
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge a geofence alert"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            logger.info(f"Acknowledged alert {alert_id} by {acknowledged_by}")
            return True
        return False
    
    def add_alert_callback(self, callback: Callable) -> None:
        """Add a callback for geofence alerts"""
        self.alert_callbacks.append(callback)
        logger.info("Added geofence alert callback")
    
    def remove_alert_callback(self, callback: Callable) -> None:
        """Remove a callback"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
            logger.info("Removed geofence alert callback")
    
    def clear_alerts(self, older_than_days: Optional[int] = None) -> int:
        """
        Clear old alerts
        
        Args:
            older_than_days: Clear alerts older than this many days
            
        Returns:
            Number of alerts cleared
        """
        if older_than_days:
            cutoff = datetime.utcnow() - timedelta(days=older_than_days)
            to_delete = [
                alert_id for alert_id, alert in self.alerts.items()
                if alert.timestamp < cutoff
            ]
        else:
            to_delete = list(self.alerts.keys())
        
        for alert_id in to_delete:
            del self.alerts[alert_id]
        
        logger.info(f"Cleared {len(to_delete)} alerts")
        return len(to_delete)


# Create global geofencing system instance
geofencing_system = GeofencingSystem()


# Import timedelta for clear_alerts
from datetime import timedelta

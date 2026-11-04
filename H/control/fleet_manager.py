"""
H Module - Fleet Manager
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Fleet management system for helicopters and vehicles
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set
import uuid

from ..models.helicopter import Helicopter, HelicopterStatus, Location, Mission, Pilot
from ..models.vehicle import Vehicle, VehicleStatus, VehicleLocation
from ..models.telemetry import TelemetryPoint, TelemetrySource
from ..geographic.gps_tracker import gps_tracker
from ..geographic.geofencing import geofencing_system

logger = logging.getLogger(__name__)


@dataclass
class FleetStats:
    """Fleet statistics"""
    total_helicopters: int = 0
    total_vehicles: int = 0
    in_flight: int = 0
    driving: int = 0
    grounded: int = 0
    parked: int = 0
    maintenance: int = 0
    offline: int = 0
    active_alerts: int = 0
    total_missions: int = 0
    completed_missions: int = 0
    
    def to_dict(self) -> Dict[str, int]:
        """Convert to dictionary"""
        return {
            "total_helicopters": self.total_helicopters,
            "total_vehicles": self.total_vehicles,
            "in_flight": self.in_flight,
            "driving": self.driving,
            "grounded": self.grounded,
            "parked": self.parked,
            "maintenance": self.maintenance,
            "offline": self.offline,
            "active_alerts": self.active_alerts,
            "total_missions": self.total_missions,
            "completed_missions": self.completed_missions
        }


@dataclass
class FleetAlert:
    """Fleet-level alert"""
    alert_id: str
    alert_type: str
    severity: str
    message: str
    entity_id: str
    entity_type: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "severity": self.severity,
            "message": self.message,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "metadata": self.metadata
        }


class FleetManager:
    """
    Fleet management system for helicopters and vehicles
    
    Features:
    - Unified management of helicopters and vehicles
    - Real-time status monitoring
    - Mission assignment and tracking
    - Alert management
    - Fleet statistics
    - Emergency protocols
    """
    
    def __init__(self):
        """Initialize fleet manager"""
        self.helicopters: Dict[str, Helicopter] = {}
        self.vehicles: Dict[str, Vehicle] = {}
        self.alerts: Dict[str, FleetAlert] = {}
        self.missions: Dict[str, Mission] = {}
        self.alert_callbacks: List[Callable] = []
        self.status_callbacks: List[Callable] = []
        self.is_running = False
        self.update_interval = 5.0
        self.stats = FleetStats()
        
        logger.info("Fleet Manager initialized")
    
    async def start(self) -> None:
        """Start fleet monitoring"""
        if self.is_running:
            logger.warning("Fleet Manager is already running")
            return
        
        self.is_running = True
        logger.info("Fleet Manager started")
        
        while self.is_running:
            await self._update_fleet_status()
            await asyncio.sleep(self.update_interval)
    
    async def stop(self) -> None:
        """Stop fleet monitoring"""
        self.is_running = False
        logger.info("Fleet Manager stopped")
    
    async def _update_fleet_status(self) -> None:
        """Update fleet status and statistics"""
        self.stats = FleetStats()
        
        # Update helicopter stats
        for helicopter in self.helicopters.values():
            self.stats.total_helicopters += 1
            
            if helicopter.status == HelicopterStatus.IN_FLIGHT:
                self.stats.in_flight += 1
            elif helicopter.status == HelicopterStatus.GROUNDED:
                self.stats.grounded += 1
            elif helicopter.status == HelicopterStatus.MAINTENANCE:
                self.stats.maintenance += 1
            elif helicopter.status == HelicopterStatus.EMERGENCY:
                self.stats.offline += 1
            else:
                self.stats.grounded += 1
        
        # Update vehicle stats
        for vehicle in self.vehicles.values():
            self.stats.total_vehicles += 1
            
            if vehicle.status == VehicleStatus.DRIVING:
                self.stats.driving += 1
            elif vehicle.status == VehicleStatus.PARKED:
                self.stats.parked += 1
            elif vehicle.status == VehicleStatus.MAINTENANCE:
                self.stats.maintenance += 1
            elif vehicle.status == VehicleStatus.OFFLINE:
                self.stats.offline += 1
        
        # Update mission stats
        for mission in self.missions.values():
            self.stats.total_missions += 1
            if mission.status == "completed":
                self.stats.completed_missions += 1
        
        # Update alert count
        self.stats.active_alerts = len([a for a in self.alerts.values() if not a.acknowledged])
        
        # Notify status callbacks
        for callback in self.status_callbacks:
            try:
                await callback(self.stats)
            except Exception as e:
                logger.error(f"Status callback error: {e}")
    
    def add_helicopter(self, helicopter: Helicopter) -> None:
        """Add a helicopter to the fleet"""
        self.helicopters[helicopter.helicopter_id] = helicopter
        
        # Add to GPS tracker
        gps_tracker.add_entity(
            entity_id=helicopter.helicopter_id,
            entity_type="helicopter",
            initial_location={
                "latitude": helicopter.location.latitude,
                "longitude": helicopter.location.longitude,
                "altitude": helicopter.location.altitude,
                "heading": helicopter.location.heading,
                "speed": helicopter.location.speed
            },
            status=helicopter.status.value
        )
        
        logger.info(f"Added helicopter {helicopter.helicopter_id} to fleet")
    
    def add_vehicle(self, vehicle: Vehicle) -> None:
        """Add a vehicle to the fleet"""
        self.vehicles[vehicle.vehicle_id] = vehicle
        
        # Add to GPS tracker
        gps_tracker.add_entity(
            entity_id=vehicle.vehicle_id,
            entity_type="vehicle",
            initial_location={
                "latitude": vehicle.location.latitude,
                "longitude": vehicle.location.longitude,
                "altitude": vehicle.location.altitude,
                "heading": vehicle.location.heading,
                "speed": vehicle.location.speed
            },
            status=vehicle.status.value
        )
        
        logger.info(f"Added vehicle {vehicle.vehicle_id} to fleet")
    
    def remove_helicopter(self, helicopter_id: str) -> bool:
        """Remove a helicopter from the fleet"""
        if helicopter_id in self.helicopters:
            del self.helicopters[helicopter_id]
            gps_tracker.remove_entity(helicopter_id)
            logger.info(f"Removed helicopter {helicopter_id} from fleet")
            return True
        return False
    
    def remove_vehicle(self, vehicle_id: str) -> bool:
        """Remove a vehicle from the fleet"""
        if vehicle_id in self.vehicles:
            del self.vehicles[vehicle_id]
            gps_tracker.remove_entity(vehicle_id)
            logger.info(f"Removed vehicle {vehicle_id} from fleet")
            return True
        return False
    
    def get_helicopter(self, helicopter_id: str) -> Optional[Helicopter]:
        """Get a helicopter by ID"""
        return self.helicopters.get(helicopter_id)
    
    def get_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        """Get a vehicle by ID"""
        return self.vehicles.get(vehicle_id)
    
    def list_helicopters(self) -> List[Helicopter]:
        """List all helicopters"""
        return list(self.helicopters.values())
    
    def list_vehicles(self) -> List[Vehicle]:
        """List all vehicles"""
        return list(self.vehicles.values())
    
    def get_all_entities(self) -> Dict[str, Dict[str, Any]]:
        """Get all entities (helicopters and vehicles)"""
        entities = {}
        
        for helicopter in self.helicopters.values():
            entities[helicopter.helicopter_id] = {
                "type": "helicopter",
                "data": helicopter.to_dict()
            }
        
        for vehicle in self.vehicles.values():
            entities[vehicle.vehicle_id] = {
                "type": "vehicle",
                "data": vehicle.to_dict()
            }
        
        return entities
    
    def update_helicopter_status(self, helicopter_id: str, status: HelicopterStatus) -> bool:
        """Update helicopter status"""
        helicopter = self.helicopters.get(helicopter_id)
        if helicopter:
            old_status = helicopter.status
            helicopter.status = status
            
            # Update GPS tracker
            gps_tracker.entities[helicopter_id]["status"] = status.value
            
            # Check for status change alerts
            if old_status != status:
                self._check_status_alert(helicopter_id, "helicopter", old_status.value, status.value)
            
            logger.info(f"Updated helicopter {helicopter_id} status to {status.value}")
            return True
        return False
    
    def update_vehicle_status(self, vehicle_id: str, status: VehicleStatus) -> bool:
        """Update vehicle status"""
        vehicle = self.vehicles.get(vehicle_id)
        if vehicle:
            old_status = vehicle.status
            vehicle.status = status
            
            # Update GPS tracker
            gps_tracker.entities[vehicle_id]["status"] = status.value
            
            # Check for status change alerts
            if old_status != status:
                self._check_status_alert(vehicle_id, "vehicle", old_status.value, status.value)
            
            logger.info(f"Updated vehicle {vehicle_id} status to {status.value}")
            return True
        return False
    
    def _check_status_alert(self, entity_id: str, entity_type: str, 
                           old_status: str, new_status: str) -> None:
        """Check if status change should generate an alert"""
        # Emergency status change
        if new_status == "emergency":
            self.create_alert(
                alert_type="emergency",
                severity="critical",
                message=f"{entity_type.capitalize()} {entity_id} entered EMERGENCY status",
                entity_id=entity_id,
                entity_type=entity_type,
                metadata={"old_status": old_status, "new_status": new_status}
            )
        
        # In flight status
        elif new_status == "in_flight":
            self.create_alert(
                alert_type="status_change",
                severity="info",
                message=f"{entity_type.capitalize()} {entity_id} took off",
                entity_id=entity_id,
                entity_type=entity_type,
                metadata={"old_status": old_status, "new_status": new_status}
            )
        
        # Landing
        elif new_status == "landing":
            self.create_alert(
                alert_type="status_change",
                severity="info",
                message=f"{entity_type.capitalize()} {entity_id} is landing",
                entity_id=entity_id,
                entity_type=entity_type,
                metadata={"old_status": old_status, "new_status": new_status}
            )
    
    def create_alert(self, alert_type: str, severity: str, message: str,
                     entity_id: str, entity_type: str, 
                     metadata: Optional[Dict[str, Any]] = None) -> FleetAlert:
        """Create a fleet alert"""
        alert_id = str(uuid.uuid4())
        alert = FleetAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            severity=severity,
            message=message,
            entity_id=entity_id,
            entity_type=entity_type,
            metadata=metadata or {}
        )
        
        self.alerts[alert_id] = alert
        logger.warning(f"Fleet alert: {severity.upper()} - {message}")
        
        # Notify callbacks
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
        
        return alert
    
    def get_alerts(self, acknowledged: Optional[bool] = None, 
                   severity: Optional[str] = None) -> List[FleetAlert]:
        """Get fleet alerts with optional filters"""
        result = []
        for alert in self.alerts.values():
            if acknowledged is not None and alert.acknowledged != acknowledged:
                continue
            if severity and alert.severity != severity:
                continue
            result.append(alert)
        
        # Sort by timestamp (newest first)
        result.sort(key=lambda x: x.timestamp, reverse=True)
        return result
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """Acknowledge a fleet alert"""
        alert = self.alerts.get(alert_id)
        if alert:
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            logger.info(f"Acknowledged alert {alert_id} by {acknowledged_by}")
            return True
        return False
    
    def add_alert_callback(self, callback: Callable) -> None:
        """Add a callback for fleet alerts"""
        self.alert_callbacks.append(callback)
        logger.info("Added fleet alert callback")
    
    def remove_alert_callback(self, callback: Callable) -> None:
        """Remove a callback"""
        if callback in self.alert_callbacks:
            self.alert_callbacks.remove(callback)
            logger.info("Removed fleet alert callback")
    
    def add_status_callback(self, callback: Callable) -> None:
        """Add a callback for fleet status updates"""
        self.status_callbacks.append(callback)
        logger.info("Added fleet status callback")
    
    def remove_status_callback(self, callback: Callable) -> None:
        """Remove a status callback"""
        if callback in self.status_callbacks:
            self.status_callbacks.remove(callback)
            logger.info("Removed fleet status callback")
    
    def create_mission(self, mission_type: str, helicopter_id: str, 
                       waypoints: List[Dict[str, float]], 
                       priority: str = "normal") -> Optional[Mission]:
        """Create a new mission for a helicopter"""
        helicopter = self.helicopters.get(helicopter_id)
        if not helicopter:
            logger.error(f"Helicopter {helicopter_id} not found")
            return None
        
        mission_id = str(uuid.uuid4())
        mission = Mission(
            mission_id=mission_id,
            mission_type=mission_type,
            start_time=datetime.utcnow(),
            waypoints=waypoints,
            priority=priority,
            status="pending"
        )
        
        self.missions[mission_id] = mission
        helicopter.mission = mission
        
        logger.info(f"Created mission {mission_id} for helicopter {helicopter_id}")
        return mission
    
    def assign_mission(self, mission_id: str, helicopter_id: str) -> bool:
        """Assign a mission to a helicopter"""
        mission = self.missions.get(mission_id)
        helicopter = self.helicopters.get(helicopter_id)
        
        if mission and helicopter:
            helicopter.mission = mission
            mission.status = "assigned"
            logger.info(f"Assigned mission {mission_id} to helicopter {helicopter_id}")
            return True
        return False
    
    def start_mission(self, mission_id: str) -> bool:
        """Start a mission"""
        mission = self.missions.get(mission_id)
        if mission:
            mission.status = "in_progress"
            mission.start_time = datetime.utcnow()
            logger.info(f"Started mission {mission_id}")
            return True
        return False
    
    def complete_mission(self, mission_id: str) -> bool:
        """Complete a mission"""
        mission = self.missions.get(mission_id)
        if mission:
            mission.status = "completed"
            mission.end_time = datetime.utcnow()
            logger.info(f"Completed mission {mission_id}")
            return True
        return False
    
    def cancel_mission(self, mission_id: str) -> bool:
        """Cancel a mission"""
        mission = self.missions.get(mission_id)
        if mission:
            mission.status = "cancelled"
            mission.end_time = datetime.utcnow()
            logger.info(f"Cancelled mission {mission_id}")
            return True
        return False
    
    def get_mission(self, mission_id: str) -> Optional[Mission]:
        """Get a mission by ID"""
        return self.missions.get(mission_id)
    
    def list_missions(self) -> List[Mission]:
        """List all missions"""
        return list(self.missions.values())
    
    def get_helicopters_in_flight(self) -> List[Helicopter]:
        """Get all helicopters currently in flight"""
        return [h for h in self.helicopters.values() if h.status == HelicopterStatus.IN_FLIGHT]
    
    def get_helicopters_grounded(self) -> List[Helicopter]:
        """Get all helicopters currently grounded"""
        return [h for h in self.helicopters.values() if h.status == HelicopterStatus.GROUNDED]
    
    def get_vehicles_driving(self) -> List[Vehicle]:
        """Get all vehicles currently driving"""
        return [v for v in self.vehicles.values() if v.status == VehicleStatus.DRIVING]
    
    def get_vehicles_parked(self) -> List[Vehicle]:
        """Get all vehicles currently parked"""
        return [v for v in self.vehicles.values() if v.status == VehicleStatus.PARKED]
    
    def get_entities_near_location(self, lat: float, lng: float, radius: float) -> List[Dict[str, Any]]:
        """Get all entities near a specific location"""
        result = []
        
        for helicopter in self.helicopters.values():
            distance = self._haversine(
                lat, lng,
                helicopter.location.latitude,
                helicopter.location.longitude
            )
            if distance <= radius:
                result.append({
                    "type": "helicopter",
                    "id": helicopter.helicopter_id,
                    "name": helicopter.name,
                    "distance": distance,
                    "status": helicopter.status.value
                })
        
        for vehicle in self.vehicles.values():
            distance = self._haversine(
                lat, lng,
                vehicle.location.latitude,
                vehicle.location.longitude
            )
            if distance <= radius:
                result.append({
                    "type": "vehicle",
                    "id": vehicle.vehicle_id,
                    "name": f"{vehicle.make} {vehicle.model}",
                    "distance": distance,
                    "status": vehicle.status.value
                })
        
        # Sort by distance
        result.sort(key=lambda x: x["distance"])
        return result
    
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
    
    def get_fleet_health(self) -> Dict[str, Any]:
        """Get overall fleet health status"""
        total = len(self.helicopters) + len(self.vehicles)
        if total == 0:
            return {"status": "empty", "score": 0}
        
        operational = 0
        maintenance = 0
        emergency = 0
        
        for helicopter in self.helicopters.values():
            if helicopter.status == HelicopterStatus.IN_FLIGHT:
                operational += 1
            elif helicopter.status == HelicopterStatus.MAINTENANCE:
                maintenance += 1
            elif helicopter.status == HelicopterStatus.EMERGENCY:
                emergency += 1
            else:
                operational += 1
        
        for vehicle in self.vehicles.values():
            if vehicle.status == VehicleStatus.DRIVING:
                operational += 1
            elif vehicle.status == VehicleStatus.MAINTENANCE:
                maintenance += 1
            elif vehicle.status == VehicleStatus.EMERGENCY:
                emergency += 1
            else:
                operational += 1
        
        # Calculate health score (0-100)
        score = 100
        if maintenance > 0:
            score -= (maintenance / total) * 30
        if emergency > 0:
            score -= (emergency / total) * 50
        
        # Adjust based on alerts
        active_alerts = len([a for a in self.alerts.values() if not a.acknowledged])
        if active_alerts > 0:
            score -= min(active_alerts * 5, 20)
        
        status = "excellent" if score >= 90 else \
                "good" if score >= 70 else \
                "fair" if score >= 50 else \
                "poor" if score >= 30 else "critical"
        
        return {
            "status": status,
            "score": round(score, 1),
            "operational": operational,
            "maintenance": maintenance,
            "emergency": emergency,
            "total": total,
            "active_alerts": active_alerts
        }
    
    def get_entity_count(self) -> Dict[str, int]:
        """Get count of all entities"""
        return {
            "helicopters": len(self.helicopters),
            "vehicles": len(self.vehicles),
            "total": len(self.helicopters) + len(self.vehicles)
        }


# Import math for distance calculation
import math


# Create global fleet manager instance
fleet_manager = FleetManager()

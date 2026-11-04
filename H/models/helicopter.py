"""
H Module - Helicopter Data Model
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Helicopter data model for fleet tracking and management
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class HelicopterStatus(Enum):
    """Helicopter operational status"""
    GROUNDED = "grounded"
    TAXIING = "taxiing"
    IN_FLIGHT = "in_flight"
    LANDING = "landing"
    MAINTENANCE = "maintenance"
    EMERGENCY = "emergency"


class HelicopterModel(Enum):
    """Supported helicopter models"""
    BELL_407 = "Bell 407"
    BELL_412 = "Bell 412"
    AIRBUS_H125 = "Airbus H125"
    AIRBUS_H145 = "Airbus H145"
    SIKORSKY_S76 = "Sikorsky S-76"
    ROBINSON_R44 = "Robinson R44"
    ROBINSON_R66 = "Robinson R66"
    LEONARDO_AW109 = "Leonardo AW109"
    LEONARDO_AW139 = "Leonardo AW139"
    CUSTOM = "Custom"


@dataclass
class Location:
    """Geographic location with altitude"""
    latitude: float
    longitude: float
    altitude: float
    heading: float
    speed: float
    accuracy: float = 0.0


@dataclass
class EngineTelemetry:
    """Engine telemetry data"""
    rpm: float
    oil_pressure: float
    oil_temperature: float
    fuel_flow: float
    torque: float
    engine_hours: float
    status: str = "normal"


@dataclass
class FuelSystem:
    """Fuel system data"""
    level: float
    capacity: float
    flow_rate: float
    pressure: float
    temperature: float
    remaining: float


@dataclass
class HydraulicSystem:
    """Hydraulic system data"""
    pressure: float
    temperature: float
    fluid_level: float
    status: str = "normal"


@dataclass
class ElectricalSystem:
    """Electrical system data"""
    battery_voltage: float
    alternator_voltage: float
    battery_current: float
    alternator_current: float
    battery_temperature: float
    status: str = "normal"


@dataclass
class CameraSettings:
    """Onboard camera configuration"""
    camera_id: str
    resolution: str = "1920x1080"
    fps: int = 30
    focal_length: float = 24.0
    aperture: float = 2.8
    iso: int = 100
    shutter_speed: float = 1.0 / 1000
    white_balance: str = "auto"
    night_vision: bool = False
    thermal: bool = False
    zoom_level: float = 1.0
    stabilization: bool = True


@dataclass
class Mission:
    """Flight mission data"""
    mission_id: str
    mission_type: str
    start_time: datetime
    end_time: Optional[datetime] = None
    waypoints: List[Dict[str, float]] = field(default_factory=list)
    current_waypoint: int = 0
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: str = "normal"
    status: str = "pending"


@dataclass
class Pilot:
    """Pilot information"""
    pilot_id: str
    name: str
    license_number: str
    license_type: str
    flight_hours: float
    medical_expiry: datetime
    certification_level: str = "commercial"


@dataclass
class MaintenanceLog:
    """Maintenance record"""
    log_id: str
    maintenance_type: str
    description: str
    performed_date: datetime
    next_due_date: datetime
    hours_interval: float
    performed_by: str
    cost: float = 0.0
    status: str = "completed"


@dataclass
class Alert:
    """System alert"""
    alert_id: str
    alert_type: str
    severity: str
    message: str
    timestamp: datetime
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_time: Optional[datetime] = None


@dataclass
class Helicopter:
    """
    Helicopter data model for fleet tracking and management
    
    Attributes:
        helicopter_id: Unique identifier
        registration: Registration number
        model: Helicopter model
        name: Display name
        location: Current geographic location
        engine: Engine telemetry data
        fuel: Fuel system data
        hydraulics: Hydraulic system data
        electrical: Electrical system data
        cameras: List of onboard cameras
        status: Current operational status
        pilot: Pilot information (if assigned)
        mission: Current mission (if any)
        maintenance_logs: Maintenance history
        alerts: Active alerts
        last_update: Timestamp of last data update
        created_at: Timestamp of creation
    """
    helicopter_id: str
    registration: str
    model: HelicopterModel
    name: str
    location: Location
    engine: EngineTelemetry
    fuel: FuelSystem
    hydraulics: HydraulicSystem
    electrical: ElectricalSystem
    cameras: List[CameraSettings] = field(default_factory=list)
    status: HelicopterStatus = HelicopterStatus.GROUNDED
    pilot: Optional[Pilot] = None
    mission: Optional[Mission] = None
    maintenance_logs: List[MaintenanceLog] = field(default_factory=list)
    alerts: List[Alert] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "helicopter_id": self.helicopter_id,
            "registration": self.registration,
            "model": self.model.value,
            "name": self.name,
            "location": {
                "latitude": self.location.latitude,
                "longitude": self.location.longitude,
                "altitude": self.location.altitude,
                "heading": self.location.heading,
                "speed": self.location.speed,
                "accuracy": self.location.accuracy
            },
            "engine": {
                "rpm": self.engine.rpm,
                "oil_pressure": self.engine.oil_pressure,
                "oil_temperature": self.engine.oil_temperature,
                "fuel_flow": self.engine.fuel_flow,
                "torque": self.engine.torque,
                "engine_hours": self.engine.engine_hours,
                "status": self.engine.status
            },
            "fuel": {
                "level": self.fuel.level,
                "capacity": self.fuel.capacity,
                "flow_rate": self.fuel.flow_rate,
                "pressure": self.fuel.pressure,
                "temperature": self.fuel.temperature,
                "remaining": self.fuel.remaining
            },
            "hydraulics": {
                "pressure": self.hydraulics.pressure,
                "temperature": self.hydraulics.temperature,
                "fluid_level": self.hydraulics.fluid_level,
                "status": self.hydraulics.status
            },
            "electrical": {
                "battery_voltage": self.electrical.battery_voltage,
                "alternator_voltage": self.electrical.alternator_voltage,
                "battery_current": self.electrical.battery_current,
                "alternator_current": self.electrical.alternator_current,
                "battery_temperature": self.electrical.battery_temperature,
                "status": self.electrical.status
            },
            "cameras": [
                {
                    "camera_id": cam.camera_id,
                    "resolution": cam.resolution,
                    "fps": cam.fps,
                    "night_vision": cam.night_vision,
                    "thermal": cam.thermal
                } for cam in self.cameras
            ],
            "status": self.status.value,
            "pilot": {
                "pilot_id": self.pilot.pilot_id,
                "name": self.pilot.name,
                "license_number": self.pilot.license_number
            } if self.pilot else None,
            "mission": {
                "mission_id": self.mission.mission_id,
                "mission_type": self.mission.mission_type,
                "status": self.mission.status
            } if self.mission else None,
            "maintenance_count": len(self.maintenance_logs),
            "active_alerts": len([a for a in self.alerts if not a.acknowledged]),
            "last_update": self.last_update.isoformat(),
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Helicopter":
        """Create Helicopter from dictionary"""
        location_data = data.get("location", {})
        location = Location(
            latitude=location_data.get("latitude", 0.0),
            longitude=location_data.get("longitude", 0.0),
            altitude=location_data.get("altitude", 0.0),
            heading=location_data.get("heading", 0.0),
            speed=location_data.get("speed", 0.0),
            accuracy=location_data.get("accuracy", 0.0)
        )
        
        engine_data = data.get("engine", {})
        engine = EngineTelemetry(
            rpm=engine_data.get("rpm", 0.0),
            oil_pressure=engine_data.get("oil_pressure", 0.0),
            oil_temperature=engine_data.get("oil_temperature", 0.0),
            fuel_flow=engine_data.get("fuel_flow", 0.0),
            torque=engine_data.get("torque", 0.0),
            engine_hours=engine_data.get("engine_hours", 0.0),
            status=engine_data.get("status", "normal")
        )
        
        fuel_data = data.get("fuel", {})
        fuel = FuelSystem(
            level=fuel_data.get("level", 0.0),
            capacity=fuel_data.get("capacity", 100.0),
            flow_rate=fuel_data.get("flow_rate", 0.0),
            pressure=fuel_data.get("pressure", 0.0),
            temperature=fuel_data.get("temperature", 0.0),
            remaining=fuel_data.get("remaining", 0.0)
        )
        
        hydraulics_data = data.get("hydraulics", {})
        hydraulics = HydraulicSystem(
            pressure=hydraulics_data.get("pressure", 0.0),
            temperature=hydraulics_data.get("temperature", 0.0),
            fluid_level=hydraulics_data.get("fluid_level", 0.0),
            status=hydraulics_data.get("status", "normal")
        )
        
        electrical_data = data.get("electrical", {})
        electrical = ElectricalSystem(
            battery_voltage=electrical_data.get("battery_voltage", 0.0),
            alternator_voltage=electrical_data.get("alternator_voltage", 0.0),
            battery_current=electrical_data.get("battery_current", 0.0),
            alternator_current=electrical_data.get("alternator_current", 0.0),
            battery_temperature=electrical_data.get("battery_temperature", 0.0),
            status=electrical_data.get("status", "normal")
        )
        
        cameras = []
        for cam_data in data.get("cameras", []):
            cameras.append(CameraSettings(
                camera_id=cam_data.get("camera_id", ""),
                resolution=cam_data.get("resolution", "1920x1080"),
                fps=cam_data.get("fps", 30),
                night_vision=cam_data.get("night_vision", False),
                thermal=cam_data.get("thermal", False)
            ))
        
        pilot = None
        pilot_data = data.get("pilot")
        if pilot_data:
            pilot = Pilot(
                pilot_id=pilot_data.get("pilot_id", ""),
                name=pilot_data.get("name", ""),
                license_number=pilot_data.get("license_number", ""),
                license_type=pilot_data.get("license_type", ""),
                flight_hours=pilot_data.get("flight_hours", 0.0),
                medical_expiry=datetime.fromisoformat(pilot_data.get("medical_expiry", datetime.utcnow().isoformat()))
            )
        
        mission = None
        mission_data = data.get("mission")
        if mission_data:
            mission = Mission(
                mission_id=mission_data.get("mission_id", ""),
                mission_type=mission_data.get("mission_type", ""),
                start_time=datetime.fromisoformat(mission_data.get("start_time", datetime.utcnow().isoformat()))
            )
        
        return cls(
            helicopter_id=data.get("helicopter_id", ""),
            registration=data.get("registration", ""),
            model=HelicopterModel(data.get("model", "Custom")),
            name=data.get("name", ""),
            location=location,
            engine=engine,
            fuel=fuel,
            hydraulics=hydraulics,
            electrical=electrical,
            cameras=cameras,
            status=HelicopterStatus(data.get("status", "grounded")),
            pilot=pilot,
            mission=mission,
            last_update=datetime.fromisoformat(data.get("last_update", datetime.utcnow().isoformat()))
        )

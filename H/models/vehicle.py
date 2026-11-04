"""
H Module - Vehicle Data Model
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Vehicle data model for ground fleet tracking and management
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class VehicleStatus(Enum):
    """Vehicle operational status"""
    PARKED = "parked"
    IDLE = "idle"
    DRIVING = "driving"
    MAINTENANCE = "maintenance"
    CHARGING = "charging"
    OFFLINE = "offline"
    EMERGENCY = "emergency"


class VehicleType(Enum):
    """Vehicle types"""
    SEDAN = "sedan"
    SUV = "suv"
    TRUCK = "truck"
    VAN = "van"
    BUS = "bus"
    MOTORCYCLE = "motorcycle"
    ELECTRIC = "electric"
    HYBRID = "hybrid"
    CUSTOM = "custom"


class FuelType(Enum):
    """Fuel types"""
    GASOLINE = "gasoline"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"
    HYDROGEN = "hydrogen"
    NATURAL_GAS = "natural_gas"


@dataclass
class VehicleLocation:
    """Vehicle geographic location"""
    latitude: float
    longitude: float
    altitude: float = 0.0
    heading: float = 0.0
    speed: float = 0.0
    accuracy: float = 0.0
    gps_fix: bool = True
    satellites: int = 0


@dataclass
class VehicleEngine:
    """Vehicle engine telemetry"""
    rpm: float = 0.0
    oil_pressure: float = 0.0
    oil_temperature: float = 0.0
    coolant_temperature: float = 0.0
    throttle_position: float = 0.0
    engine_load: float = 0.0
    engine_hours: float = 0.0
    status: str = "normal"


@dataclass
class VehicleFuel:
    """Vehicle fuel system"""
    level: float = 0.0
    capacity: float = 50.0
    consumption_rate: float = 0.0
    range: float = 0.0
    fuel_type: FuelType = FuelType.GASOLINE
    voltage: float = 0.0


@dataclass
class VehicleBattery:
    """Vehicle battery system"""
    voltage: float = 0.0
    current: float = 0.0
    temperature: float = 0.0
    state_of_charge: float = 0.0
    health: float = 100.0
    status: str = "normal"


@dataclass
class VehicleTires:
    """Tire monitoring system"""
    front_left_pressure: float = 0.0
    front_right_pressure: float = 0.0
    rear_left_pressure: float = 0.0
    rear_right_pressure: float = 0.0
    front_left_temperature: float = 0.0
    front_right_temperature: float = 0.0
    rear_left_temperature: float = 0.0
    rear_right_temperature: float = 0.0
    status: str = "normal"


@dataclass
class VehicleBrakes:
    """Brake system monitoring"""
    front_wear: float = 0.0
    rear_wear: float = 0.0
    brake_fluid_level: float = 0.0
    brake_fluid_pressure: float = 0.0
    abs_status: bool = True
    status: str = "normal"


@dataclass
class VehicleCamera:
    """Onboard vehicle camera"""
    camera_id: str
    camera_type: str = "front"
    resolution: str = "1920x1080"
    fps: int = 30
    night_vision: bool = False
    thermal: bool = False
    status: str = "active"
    last_image_timestamp: Optional[datetime] = None


@dataclass
class VehicleAnomaly:
    """Detected vehicle anomaly"""
    anomaly_id: str
    anomaly_type: str
    severity: str
    description: str
    detected_at: datetime = field(default_factory=datetime.utcnow)
    image_path: Optional[str] = None
    confidence: float = 0.0
    status: str = "pending"
    resolved_at: Optional[datetime] = None


@dataclass
class VehicleMaintenance:
    """Vehicle maintenance record"""
    maintenance_id: str
    maintenance_type: str
    description: str
    performed_date: datetime
    next_due_date: datetime
    mileage_interval: float
    time_interval: float
    performed_by: str
    cost: float = 0.0
    status: str = "completed"


@dataclass
class VehicleDriver:
    """Driver information"""
    driver_id: str
    name: str
    license_number: str
    license_type: str
    driving_hours: float = 0.0
    status: str = "active"


@dataclass
class VehicleRoute:
    """Route information"""
    route_id: str
    start_location: Dict[str, float]
    end_location: Dict[str, float]
    waypoints: List[Dict[str, float]] = field(default_factory=list)
    distance: float = 0.0
    duration: float = 0.0
    status: str = "planned"


@dataclass
class Vehicle:
    """
    Vehicle data model for ground fleet tracking and management
    
    Attributes:
        vehicle_id: Unique identifier
        license_plate: Vehicle license plate
        vin: Vehicle Identification Number
        vehicle_type: Type of vehicle
        make: Manufacturer
        model: Model name
        year: Manufacturing year
        location: Current geographic location
        engine: Engine telemetry data
        fuel: Fuel system data
        battery: Battery system data
        tires: Tire monitoring data
        brakes: Brake system data
        cameras: List of onboard cameras
        anomalies: Detected anomalies
        maintenance: Maintenance records
        driver: Driver information
        route: Current route
        status: Current operational status
        odometer: Current odometer reading
        last_update: Timestamp of last data update
        created_at: Timestamp of creation
    """
    vehicle_id: str
    license_plate: str
    vin: str
    vehicle_type: VehicleType
    make: str
    model: str
    year: int
    location: VehicleLocation
    engine: VehicleEngine = field(default_factory=VehicleEngine)
    fuel: VehicleFuel = field(default_factory=VehicleFuel)
    battery: VehicleBattery = field(default_factory=VehicleBattery)
    tires: VehicleTires = field(default_factory=VehicleTires)
    brakes: VehicleBrakes = field(default_factory=VehicleBrakes)
    cameras: List[VehicleCamera] = field(default_factory=list)
    anomalies: List[VehicleAnomaly] = field(default_factory=list)
    maintenance: List[VehicleMaintenance] = field(default_factory=list)
    driver: Optional[VehicleDriver] = None
    route: Optional[VehicleRoute] = None
    status: VehicleStatus = VehicleStatus.PARKED
    odometer: float = 0.0
    last_update: datetime = field(default_factory=datetime.utcnow)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "vehicle_id": self.vehicle_id,
            "license_plate": self.license_plate,
            "vin": self.vin,
            "vehicle_type": self.vehicle_type.value,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "location": {
                "latitude": self.location.latitude,
                "longitude": self.location.longitude,
                "altitude": self.location.altitude,
                "heading": self.location.heading,
                "speed": self.location.speed,
                "accuracy": self.location.accuracy,
                "gps_fix": self.location.gps_fix,
                "satellites": self.location.satellites
            },
            "engine": {
                "rpm": self.engine.rpm,
                "oil_pressure": self.engine.oil_pressure,
                "oil_temperature": self.engine.oil_temperature,
                "coolant_temperature": self.engine.coolant_temperature,
                "throttle_position": self.engine.throttle_position,
                "engine_load": self.engine.engine_load,
                "engine_hours": self.engine.engine_hours,
                "status": self.engine.status
            },
            "fuel": {
                "level": self.fuel.level,
                "capacity": self.fuel.capacity,
                "consumption_rate": self.fuel.consumption_rate,
                "range": self.fuel.range,
                "fuel_type": self.fuel.fuel_type.value,
                "voltage": self.fuel.voltage
            },
            "battery": {
                "voltage": self.battery.voltage,
                "current": self.battery.current,
                "temperature": self.battery.temperature,
                "state_of_charge": self.battery.state_of_charge,
                "health": self.battery.health,
                "status": self.battery.status
            },
            "tires": {
                "front_left_pressure": self.tires.front_left_pressure,
                "front_right_pressure": self.tires.front_right_pressure,
                "rear_left_pressure": self.tires.rear_left_pressure,
                "rear_right_pressure": self.tires.rear_right_pressure,
                "front_left_temperature": self.tires.front_left_temperature,
                "front_right_temperature": self.tires.front_right_temperature,
                "rear_left_temperature": self.tires.rear_left_temperature,
                "rear_right_temperature": self.tires.rear_right_temperature,
                "status": self.tires.status
            },
            "brakes": {
                "front_wear": self.brakes.front_wear,
                "rear_wear": self.brakes.rear_wear,
                "brake_fluid_level": self.brakes.brake_fluid_level,
                "brake_fluid_pressure": self.brakes.brake_fluid_pressure,
                "abs_status": self.brakes.abs_status,
                "status": self.brakes.status
            },
            "cameras": [
                {
                    "camera_id": cam.camera_id,
                    "camera_type": cam.camera_type,
                    "resolution": cam.resolution,
                    "night_vision": cam.night_vision,
                    "thermal": cam.thermal,
                    "status": cam.status
                } for cam in self.cameras
            ],
            "anomalies": [
                {
                    "anomaly_id": a.anomaly_id,
                    "anomaly_type": a.anomaly_type,
                    "severity": a.severity,
                    "description": a.description,
                    "detected_at": a.detected_at.isoformat(),
                    "confidence": a.confidence,
                    "status": a.status
                } for a in self.anomalies
            ],
            "maintenance_count": len(self.maintenance),
            "driver": {
                "driver_id": self.driver.driver_id,
                "name": self.driver.name,
                "license_number": self.driver.license_number
            } if self.driver else None,
            "route": {
                "route_id": self.route.route_id,
                "start_location": self.route.start_location,
                "end_location": self.route.end_location,
                "distance": self.route.distance,
                "status": self.route.status
            } if self.route else None,
            "status": self.status.value,
            "odometer": self.odometer,
            "active_anomalies": len([a for a in self.anomalies if a.status == "pending"]),
            "last_update": self.last_update.isoformat(),
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Vehicle":
        """Create Vehicle from dictionary"""
        location_data = data.get("location", {})
        location = VehicleLocation(
            latitude=location_data.get("latitude", 0.0),
            longitude=location_data.get("longitude", 0.0),
            altitude=location_data.get("altitude", 0.0),
            heading=location_data.get("heading", 0.0),
            speed=location_data.get("speed", 0.0),
            accuracy=location_data.get("accuracy", 0.0),
            gps_fix=location_data.get("gps_fix", True),
            satellites=location_data.get("satellites", 0)
        )
        
        engine_data = data.get("engine", {})
        engine = VehicleEngine(
            rpm=engine_data.get("rpm", 0.0),
            oil_pressure=engine_data.get("oil_pressure", 0.0),
            oil_temperature=engine_data.get("oil_temperature", 0.0),
            coolant_temperature=engine_data.get("coolant_temperature", 0.0),
            throttle_position=engine_data.get("throttle_position", 0.0),
            engine_load=engine_data.get("engine_load", 0.0),
            engine_hours=engine_data.get("engine_hours", 0.0),
            status=engine_data.get("status", "normal")
        )
        
        fuel_data = data.get("fuel", {})
        fuel = VehicleFuel(
            level=fuel_data.get("level", 0.0),
            capacity=fuel_data.get("capacity", 50.0),
            consumption_rate=fuel_data.get("consumption_rate", 0.0),
            range=fuel_data.get("range", 0.0),
            fuel_type=FuelType(fuel_data.get("fuel_type", "gasoline")),
            voltage=fuel_data.get("voltage", 0.0)
        )
        
        battery_data = data.get("battery", {})
        battery = VehicleBattery(
            voltage=battery_data.get("voltage", 0.0),
            current=battery_data.get("current", 0.0),
            temperature=battery_data.get("temperature", 0.0),
            state_of_charge=battery_data.get("state_of_charge", 0.0),
            health=battery_data.get("health", 100.0),
            status=battery_data.get("status", "normal")
        )
        
        tires_data = data.get("tires", {})
        tires = VehicleTires(
            front_left_pressure=tires_data.get("front_left_pressure", 0.0),
            front_right_pressure=tires_data.get("front_right_pressure", 0.0),
            rear_left_pressure=tires_data.get("rear_left_pressure", 0.0),
            rear_right_pressure=tires_data.get("rear_right_pressure", 0.0),
            front_left_temperature=tires_data.get("front_left_temperature", 0.0),
            front_right_temperature=tires_data.get("front_right_temperature", 0.0),
            rear_left_temperature=tires_data.get("rear_left_temperature", 0.0),
            rear_right_temperature=tires_data.get("rear_right_temperature", 0.0),
            status=tires_data.get("status", "normal")
        )
        
        brakes_data = data.get("brakes", {})
        brakes = VehicleBrakes(
            front_wear=brakes_data.get("front_wear", 0.0),
            rear_wear=brakes_data.get("rear_wear", 0.0),
            brake_fluid_level=brakes_data.get("brake_fluid_level", 0.0),
            brake_fluid_pressure=brakes_data.get("brake_fluid_pressure", 0.0),
            abs_status=brakes_data.get("abs_status", True),
            status=brakes_data.get("status", "normal")
        )
        
        cameras = []
        for cam_data in data.get("cameras", []):
            cameras.append(VehicleCamera(
                camera_id=cam_data.get("camera_id", ""),
                camera_type=cam_data.get("camera_type", "front"),
                resolution=cam_data.get("resolution", "1920x1080"),
                night_vision=cam_data.get("night_vision", False),
                thermal=cam_data.get("thermal", False),
                status=cam_data.get("status", "active")
            ))
        
        anomalies = []
        for anomaly_data in data.get("anomalies", []):
            anomalies.append(VehicleAnomaly(
                anomaly_id=anomaly_data.get("anomaly_id", ""),
                anomaly_type=anomaly_data.get("anomaly_type", ""),
                severity=anomaly_data.get("severity", "low"),
                description=anomaly_data.get("description", ""),
                confidence=anomaly_data.get("confidence", 0.0),
                status=anomaly_data.get("status", "pending")
            ))
        
        driver = None
        driver_data = data.get("driver")
        if driver_data:
            driver = VehicleDriver(
                driver_id=driver_data.get("driver_id", ""),
                name=driver_data.get("name", ""),
                license_number=driver_data.get("license_number", ""),
                license_type=driver_data.get("license_type", ""),
                driving_hours=driver_data.get("driving_hours", 0.0),
                status=driver_data.get("status", "active")
            )
        
        route = None
        route_data = data.get("route")
        if route_data:
            route = VehicleRoute(
                route_id=route_data.get("route_id", ""),
                start_location=route_data.get("start_location", {}),
                end_location=route_data.get("end_location", {}),
                waypoints=route_data.get("waypoints", []),
                distance=route_data.get("distance", 0.0),
                duration=route_data.get("duration", 0.0),
                status=route_data.get("status", "planned")
            )
        
        return cls(
            vehicle_id=data.get("vehicle_id", ""),
            license_plate=data.get("license_plate", ""),
            vin=data.get("vin", ""),
            vehicle_type=VehicleType(data.get("vehicle_type", "custom")),
            make=data.get("make", ""),
            model=data.get("model", ""),
            year=data.get("year", 2024),
            location=location,
            engine=engine,
            fuel=fuel,
            battery=battery,
            tires=tires,
            brakes=brakes,
            cameras=cameras,
            anomalies=anomalies,
            driver=driver,
            route=route,
            status=VehicleStatus(data.get("status", "parked")),
            odometer=data.get("odometer", 0.0),
            last_update=datetime.fromisoformat(data.get("last_update", datetime.utcnow().isoformat()))
        )

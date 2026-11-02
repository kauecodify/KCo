"""
Fleet Management Models - Vehicle, Telemetry, Anomaly
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid


@dataclass
class Vehicle:
    """Represents a vehicle in the fleet"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    vin: str = ""
    license_plate: str = ""
    make: str = ""
    model: str = ""
    year: int = 0
    country: str = "br"  # br or mx
    status: str = "active"  # active, maintenance, retired
    subscription_plan: str = "standard"
    monthly_cost: float = 0.0
    instrumented: bool = False
    instrumentation_date: Optional[datetime] = None
    telemetry_enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "vin": self.vin,
            "license_plate": self.license_plate,
            "make": self.make,
            "model": self.model,
            "year": self.year,
            "country": self.country,
            "status": self.status,
            "subscription_plan": self.subscription_plan,
            "monthly_cost": self.monthly_cost,
            "instrumented": self.instrumented,
            "instrumentation_date": self.instrumentation_date.isoformat() if self.instrumentation_date else None,
            "telemetry_enabled": self.telemetry_enabled,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Vehicle":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            vin=data.get("vin", ""),
            license_plate=data.get("license_plate", ""),
            make=data.get("make", ""),
            model=data.get("model", ""),
            year=data.get("year", 0),
            country=data.get("country", "br"),
            status=data.get("status", "active"),
            subscription_plan=data.get("subscription_plan", "standard"),
            monthly_cost=data.get("monthly_cost", 0.0),
            instrumented=data.get("instrumented", False),
            instrumentation_date=datetime.fromisoformat(data["instrumentation_date"]) if data.get("instrumentation_date") else None,
            telemetry_enabled=data.get("telemetry_enabled", True)
        )


@dataclass
class TelemetryData:
    """Represents telemetry data from a vehicle"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    vehicle_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    location: Dict[str, float] = field(default_factory=dict)
    speed: float = 0.0
    engine_rpm: float = 0.0
    engine_temperature: float = 0.0
    oil_pressure: float = 0.0
    battery_voltage: float = 0.0
    fuel_level: float = 0.0
    fuel_efficiency: float = 0.0
    vibration: Dict[str, float] = field(default_factory=dict)
    gps_coordinates: Dict[str, float] = field(default_factory=dict)
    obd_codes: List[str] = field(default_factory=list)
    driver_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "vehicle_id": self.vehicle_id,
            "timestamp": self.timestamp.isoformat(),
            "location": self.location,
            "speed": self.speed,
            "engine_rpm": self.engine_rpm,
            "engine_temperature": self.engine_temperature,
            "oil_pressure": self.oil_pressure,
            "battery_voltage": self.battery_voltage,
            "fuel_level": self.fuel_level,
            "fuel_efficiency": self.fuel_efficiency,
            "vibration": self.vibration,
            "gps_coordinates": self.gps_coordinates,
            "obd_codes": self.obd_codes,
            "driver_id": self.driver_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TelemetryData":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            vehicle_id=data.get("vehicle_id", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.utcnow(),
            location=data.get("location", {}),
            speed=data.get("speed", 0.0),
            engine_rpm=data.get("engine_rpm", 0.0),
            engine_temperature=data.get("engine_temperature", 0.0),
            oil_pressure=data.get("oil_pressure", 0.0),
            battery_voltage=data.get("battery_voltage", 0.0),
            fuel_level=data.get("fuel_level", 0.0),
            fuel_efficiency=data.get("fuel_efficiency", 0.0),
            vibration=data.get("vibration", {}),
            gps_coordinates=data.get("gps_coordinates", {}),
            obd_codes=data.get("obd_codes", []),
            driver_id=data.get("driver_id")
        )


@dataclass
class Anomaly:
    """Represents a detected anomaly in a vehicle"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    vehicle_id: str = ""
    telemetry_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    anomaly_type: str = ""
    severity: str = "low"  # low, medium, high, critical
    description: str = ""
    value: float = 0.0
    threshold: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    resolved: bool = False
    resolution_notes: str = ""
    resolved_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "vehicle_id": self.vehicle_id,
            "telemetry_id": self.telemetry_id,
            "timestamp": self.timestamp.isoformat(),
            "anomaly_type": self.anomaly_type,
            "severity": self.severity,
            "description": self.description,
            "value": self.value,
            "threshold": self.threshold,
            "metadata": self.metadata,
            "resolved": self.resolved,
            "resolution_notes": self.resolution_notes,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Anomaly":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            vehicle_id=data.get("vehicle_id", ""),
            telemetry_id=data.get("telemetry_id", ""),
            timestamp=datetime.fromisoformat(data["timestamp"]) if data.get("timestamp") else datetime.utcnow(),
            anomaly_type=data.get("anomaly_type", ""),
            severity=data.get("severity", "low"),
            description=data.get("description", ""),
            value=data.get("value", 0.0),
            threshold=data.get("threshold", 0.0),
            metadata=data.get("metadata", {}),
            resolved=data.get("resolved", False),
            resolution_notes=data.get("resolution_notes", ""),
            resolved_at=datetime.fromisoformat(data["resolved_at"]) if data.get("resolved_at") else None
        )


@dataclass
class MaintenanceRecord:
    """Represents a maintenance record for a vehicle"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    vehicle_id: str = ""
    maintenance_type: str = ""
    description: str = ""
    cost: float = 0.0
    parts_replaced: List[str] = field(default_factory=list)
    labor_hours: float = 0.0
    scheduled_date: Optional[datetime] = None
    completed_date: Optional[datetime] = None
    status: str = "scheduled"  # scheduled, in_progress, completed, cancelled
    notes: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "vehicle_id": self.vehicle_id,
            "maintenance_type": self.maintenance_type,
            "description": self.description,
            "cost": self.cost,
            "parts_replaced": self.parts_replaced,
            "labor_hours": self.labor_hours,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "completed_date": self.completed_date.isoformat() if self.completed_date else None,
            "status": self.status,
            "notes": self.notes
        }

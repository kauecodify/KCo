"""
Fleet Service - Manages vehicle fleet operations
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from backend.models.fleet import Vehicle, TelemetryData, Anomaly, MaintenanceRecord
from backend.config.settings import settings

logger = logging.getLogger(__name__)


class FleetService:
    """Service for managing vehicle fleet"""
    
    def __init__(self):
        # In-memory storage for demo (replace with database in production)
        self.vehicles: Dict[str, Vehicle] = {}
        self.telemetry: Dict[str, TelemetryData] = {}
        self.anomalies: Dict[str, Anomaly] = {}
        self.maintenance: Dict[str, MaintenanceRecord] = {}
        self._initialize_sample_data()
    
    def _initialize_sample_data(self):
        """Initialize with sample data for demo"""
        # Sample vehicles for Brazil
        br_vehicles = [
            Vehicle(
                id="BR-001",
                vin="9BWZZZ45Z7G123456",
                license_plate="ABC1234",
                make="Volkswagen",
                model="Gol",
                year=2022,
                country="br",
                status="active",
                subscription_plan="premium",
                monthly_cost=8500.0,
                instrumented=True,
                instrumentation_date=datetime(2024, 1, 15)
            ),
            Vehicle(
                id="BR-002",
                vin="9C2ZZZ45Z8G234567",
                license_plate="DEF5678",
                make="Chevrolet",
                model="Onix",
                year=2023,
                country="br",
                status="active",
                subscription_plan="standard",
                monthly_cost=7500.0,
                instrumented=True,
                instrumentation_date=datetime(2024, 1, 20)
            )
        ]
        
        # Sample vehicles for Mexico
        mx_vehicles = [
            Vehicle(
                id="MX-001",
                vin="3VWLL7AJ7BM123456",
                license_plate="GHI9012",
                make="Nissan",
                model="Versa",
                year=2022,
                country="mx",
                status="active",
                subscription_plan="premium",
                monthly_cost=12000.0,
                instrumented=True,
                instrumentation_date=datetime(2024, 2, 1)
            ),
            Vehicle(
                id="MX-002",
                vin="3VWLL7AJ8CM234567",
                license_plate="JKL3456",
                make="Volkswagen",
                model="Jetta",
                year=2023,
                country="mx",
                status="active",
                subscription_plan="standard",
                monthly_cost=10000.0,
                instrumented=True,
                instrumentation_date=datetime(2024, 2, 10)
            )
        ]
        
        for v in br_vehicles + mx_vehicles:
            self.vehicles[v.id] = v
        
        logger.info(f"Initialized {len(self.vehicles)} sample vehicles")
    
    def get_all_vehicles(self, country: Optional[str] = None) -> List[Vehicle]:
        """Get all vehicles, optionally filtered by country"""
        if country:
            return [v for v in self.vehicles.values() if v.country == country]
        return list(self.vehicles.values())
    
    def get_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        """Get specific vehicle by ID"""
        return self.vehicles.get(vehicle_id)
    
    def create_vehicle(self, vehicle: Vehicle) -> Vehicle:
        """Create new vehicle in fleet"""
        self.vehicles[vehicle.id] = vehicle
        logger.info(f"Created vehicle {vehicle.id}")
        return vehicle
    
    def update_vehicle(self, vehicle_id: str, updates: Dict[str, Any]) -> Optional[Vehicle]:
        """Update vehicle information"""
        vehicle = self.vehicles.get(vehicle_id)
        if not vehicle:
            return None
        
        for key, value in updates.items():
            if hasattr(vehicle, key):
                setattr(vehicle, key, value)
        
        vehicle.updated_at = datetime.utcnow()
        logger.info(f"Updated vehicle {vehicle_id}")
        return vehicle
    
    def submit_telemetry(self, telemetry: TelemetryData) -> TelemetryData:
        """Submit telemetry data from vehicle"""
        self.telemetry[telemetry.id] = telemetry
        logger.debug(f"Received telemetry from vehicle {telemetry.vehicle_id}")
        return telemetry
    
    def get_telemetry(self, vehicle_id: str, limit: int = 100) -> List[TelemetryData]:
        """Get telemetry data for specific vehicle"""
        return [t for t in self.telemetry.values() if t.vehicle_id == vehicle_id][-limit:]
    
    def log_anomaly(self, anomaly: Anomaly) -> Anomaly:
        """Log detected anomaly"""
        self.anomalies[anomaly.id] = anomaly
        logger.warning(f"Anomaly detected: {anomaly.anomaly_type} on vehicle {anomaly.vehicle_id}")
        return anomaly
    
    def get_anomalies(self, vehicle_id: Optional[str] = None, limit: int = 100) -> List[Anomaly]:
        """Get anomalies, optionally filtered by vehicle"""
        if vehicle_id:
            return [a for a in self.anomalies.values() if a.vehicle_id == vehicle_id][-limit:]
        return list(self.anomalies.values())[-limit:]
    
    def create_maintenance_record(self, record: MaintenanceRecord) -> MaintenanceRecord:
        """Create maintenance record"""
        self.maintenance[record.id] = record
        logger.info(f"Created maintenance record {record.id} for vehicle {record.vehicle_id}")
        return record
    
    def get_fleet_stats(self) -> Dict[str, Any]:
        """Get fleet statistics"""
        br_vehicles = [v for v in self.vehicles.values() if v.country == "br"]
        mx_vehicles = [v for v in self.vehicles.values() if v.country == "mx"]
        
        return {
            "total_vehicles": len(self.vehicles),
            "brazil": {
                "count": len(br_vehicles),
                "active": len([v for v in br_vehicles if v.status == "active"]),
                "instrumented": len([v for v in br_vehicles if v.instrumented])
            },
            "mexico": {
                "count": len(mx_vehicles),
                "active": len([v for v in mx_vehicles if v.status == "active"]),
                "instrumented": len([v for v in mx_vehicles if v.instrumented])
            },
            "total_telemetry_points": len(self.telemetry),
            "total_anomalies": len(self.anomalies)
        }

"""
H Module - Helicopter API Routes
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

FastAPI routes for helicopter management
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
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
from ..control.fleet_manager import fleet_manager
from ..geographic.gps_tracker import gps_tracker

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/h/helicopters", tags=["Helicopters"])


@router.get("/", summary="List all helicopters")
async def list_helicopters(
    status: Optional[str] = None,
    model: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    List all helicopters with optional filters
    
    Parameters:
    - status: Filter by status (in_flight, grounded, maintenance, etc.)
    - model: Filter by helicopter model
    """
    helicopters = fleet_manager.list_helicopters()
    
    # Apply filters
    if status:
        helicopters = [h for h in helicopters if h.status.value == status]
    if model:
        helicopters = [h for h in helicopters if h.model.value == model]
    
    return [h.to_dict() for h in helicopters]


@router.get("/{helicopter_id}", summary="Get helicopter by ID")
async def get_helicopter(helicopter_id: str) -> Dict[str, Any]:
    """Get a specific helicopter by ID"""
    helicopter = fleet_manager.get_helicopter(helicopter_id)
    if not helicopter:
        raise HTTPException(status_code=404, detail="Helicopter not found")
    return helicopter.to_dict()


@router.post("/", summary="Create a new helicopter")
async def create_helicopter(helicopter_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new helicopter
    
    Request body:
    - registration: Helicopter registration number
    - model: Helicopter model
    - name: Display name
    - location: Initial location (lat, lng, alt, heading, speed)
    - cameras: List of camera configurations
    """
    try:
        # Create location
        location_data = helicopter_data.get("location", {})
        location = Location(
            latitude=location_data.get("latitude", 0.0),
            longitude=location_data.get("longitude", 0.0),
            altitude=location_data.get("altitude", 0.0),
            heading=location_data.get("heading", 0.0),
            speed=location_data.get("speed", 0.0)
        )
        
        # Create engine telemetry
        engine_data = helicopter_data.get("engine", {})
        engine = EngineTelemetry(
            rpm=engine_data.get("rpm", 0.0),
            oil_pressure=engine_data.get("oil_pressure", 0.0),
            oil_temperature=engine_data.get("oil_temperature", 0.0),
            fuel_flow=engine_data.get("fuel_flow", 0.0),
            torque=engine_data.get("torque", 0.0),
            engine_hours=engine_data.get("engine_hours", 0.0)
        )
        
        # Create fuel system
        fuel_data = helicopter_data.get("fuel", {})
        fuel = FuelSystem(
            level=fuel_data.get("level", 100.0),
            capacity=fuel_data.get("capacity", 100.0),
            flow_rate=fuel_data.get("flow_rate", 0.0),
            pressure=fuel_data.get("pressure", 0.0),
            temperature=fuel_data.get("temperature", 0.0),
            remaining=fuel_data.get("remaining", 100.0)
        )
        
        # Create hydraulic system
        hydraulics_data = helicopter_data.get("hydraulics", {})
        hydraulics = HydraulicSystem(
            pressure=hydraulics_data.get("pressure", 0.0),
            temperature=hydraulics_data.get("temperature", 0.0),
            fluid_level=hydraulics_data.get("fluid_level", 100.0)
        )
        
        # Create electrical system
        electrical_data = helicopter_data.get("electrical", {})
        electrical = ElectricalSystem(
            battery_voltage=electrical_data.get("battery_voltage", 24.0),
            alternator_voltage=electrical_data.get("alternator_voltage", 24.0),
            battery_current=electrical_data.get("battery_current", 0.0),
            alternator_current=electrical_data.get("alternator_current", 0.0),
            battery_temperature=electrical_data.get("battery_temperature", 25.0)
        )
        
        # Create cameras
        cameras = []
        for cam_data in helicopter_data.get("cameras", []):
            cameras.append(CameraSettings(
                camera_id=cam_data.get("camera_id", str(uuid.uuid4())),
                resolution=cam_data.get("resolution", "1920x1080"),
                fps=cam_data.get("fps", 30),
                night_vision=cam_data.get("night_vision", False),
                thermal=cam_data.get("thermal", False)
            ))
        
        # Create helicopter
        helicopter = Helicopter(
            helicopter_id=str(uuid.uuid4()),
            registration=helicopter_data.get("registration", ""),
            model=HelicopterModel(helicopter_data.get("model", "Custom")),
            name=helicopter_data.get("name", ""),
            location=location,
            engine=engine,
            fuel=fuel,
            hydraulics=hydraulics,
            electrical=electrical,
            cameras=cameras,
            status=HelicopterStatus(helicopter_data.get("status", "grounded"))
        )
        
        # Add to fleet
        fleet_manager.add_helicopter(helicopter)
        
        logger.info(f"Created helicopter {helicopter.helicopter_id}")
        return helicopter.to_dict()
        
    except Exception as e:
        logger.error(f"Error creating helicopter: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{helicopter_id}", summary="Update helicopter")
async def update_helicopter(
    helicopter_id: str,
    helicopter_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Update a helicopter"""
    helicopter = fleet_manager.get_helicopter(helicopter_id)
    if not helicopter:
        raise HTTPException(status_code=404, detail="Helicopter not found")
    
    try:
        # Update fields
        if "registration" in helicopter_data:
            helicopter.registration = helicopter_data["registration"]
        if "name" in helicopter_data:
            helicopter.name = helicopter_data["name"]
        if "model" in helicopter_data:
            helicopter.model = HelicopterModel(helicopter_data["model"])
        if "status" in helicopter_data:
            helicopter.status = HelicopterStatus(helicopter_data["status"])
        
        # Update location if provided
        if "location" in helicopter_data:
            location_data = helicopter_data["location"]
            helicopter.location = Location(
                latitude=location_data.get("latitude", helicopter.location.latitude),
                longitude=location_data.get("longitude", helicopter.location.longitude),
                altitude=location_data.get("altitude", helicopter.location.altitude),
                heading=location_data.get("heading", helicopter.location.heading),
                speed=location_data.get("speed", helicopter.location.speed)
            )
        
        # Update GPS tracker
        gps_tracker.entities[helicopter_id]["location"] = {
            "latitude": helicopter.location.latitude,
            "longitude": helicopter.location.longitude,
            "altitude": helicopter.location.altitude,
            "heading": helicopter.location.heading,
            "speed": helicopter.location.speed
        }
        
        logger.info(f"Updated helicopter {helicopter_id}")
        return helicopter.to_dict()
        
    except Exception as e:
        logger.error(f"Error updating helicopter {helicopter_id}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{helicopter_id}", summary="Delete helicopter")
async def delete_helicopter(helicopter_id: str) -> Dict[str, Any]:
    """Delete a helicopter"""
    if not fleet_manager.remove_helicopter(helicopter_id):
        raise HTTPException(status_code=404, detail="Helicopter not found")
    
    logger.info(f"Deleted helicopter {helicopter_id}")
    return {"message": "Helicopter deleted", "helicopter_id": helicopter_id}


@router.get("/{helicopter_id}/location", summary="Get helicopter location")
async def get_helicopter_location(helicopter_id: str) -> Dict[str, Any]:
    """Get current location of a helicopter"""
    helicopter = fleet_manager.get_helicopter(helicopter_id)
    if not helicopter:
        raise HTTPException(status_code=404, detail="Helicopter not found")
    
    return {
        "latitude": helicopter.location.latitude,
        "longitude": helicopter.location.longitude,
        "altitude": helicopter.location.altitude,
        "heading": helicopter.location.heading,
        "speed": helicopter.location.speed,
        "accuracy": helicopter.location.accuracy
    }


@router.get("/{helicopter_id}/status", summary="Get helicopter status")
async def get_helicopter_status(helicopter_id: str) -> Dict[str, Any]:
    """Get current status of a helicopter"""
    helicopter = fleet_manager.get_helicopter(helicopter_id)
    if not helicopter:
        raise HTTPException(status_code=404, detail="Helicopter not found")
    
    return {
        "status": helicopter.status.value,
        "last_update": helicopter.last_update.isoformat()
    }


@router.post("/{helicopter_id}/status", summary="Update helicopter status")
async def update_helicopter_status(
    helicopter_id: str,
    status: str
) -> Dict[str, Any]:
    """Update helicopter status"""
    if not fleet_manager.update_helicopter_status(helicopter_id, HelicopterStatus(status)):
        raise HTTPException(status_code=404, detail="Helicopter not found")
    
    logger.info(f"Updated helicopter {helicopter_id} status to {status}")
    return {"message": "Status updated", "helicopter_id": helicopter_id, "status": status}


@router.get("/{helicopter_id}/telemetry", summary="Get helicopter telemetry")
async def get_helicopter_telemetry(helicopter_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    """Get telemetry data for a helicopter"""
    telemetry = gps_tracker.get_telemetry(helicopter_id, limit)
    return [t.to_dict() for t in telemetry]


@router.get("/in-flight", summary="List helicopters in flight")
async def list_helicopters_in_flight() -> List[Dict[str, Any]]:
    """List all helicopters currently in flight"""
    helicopters = fleet_manager.get_helicopters_in_flight()
    return [h.to_dict() for h in helicopters]


@router.get("/grounded", summary="List grounded helicopters")
async def list_grounded_helicopters() -> List[Dict[str, Any]]:
    """List all helicopters currently grounded"""
    helicopters = fleet_manager.get_helicopters_grounded()
    return [h.to_dict() for h in helicopters]


@router.get("/stats", summary="Get helicopter fleet statistics")
async def get_helicopter_stats() -> Dict[str, Any]:
    """Get statistics for the helicopter fleet"""
    helicopters = fleet_manager.list_helicopters()
    
    stats = {
        "total": len(helicopters),
        "in_flight": len([h for h in helicopters if h.status == HelicopterStatus.IN_FLIGHT]),
        "grounded": len([h for h in helicopters if h.status == HelicopterStatus.GROUNDED]),
        "maintenance": len([h for h in helicopters if h.status == HelicopterStatus.MAINTENANCE]),
        "emergency": len([h for h in helicopters if h.status == HelicopterStatus.EMERGENCY]),
        "models": {}
    }
    
    # Count by model
    for helicopter in helicopters:
        model = helicopter.model.value
        stats["models"][model] = stats["models"].get(model, 0) + 1
    
    return stats


@router.get("/near", summary="Find helicopters near a location")
async def find_helicopters_near(
    lat: float,
    lng: float,
    radius: float = 1000.0
) -> List[Dict[str, Any]]:
    """
    Find helicopters near a specific location
    
    Parameters:
    - lat: Latitude
    - lng: Longitude
    - radius: Search radius in meters
    """
    results = fleet_manager.get_entities_near_location(lat, lng, radius)
    return [r for r in results if r.get("type") == "helicopter"]

"""
H Module - Fleet API Routes
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

FastAPI routes for fleet management
"""

from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

from ..models.helicopter import Helicopter, HelicopterStatus
from ..models.vehicle import Vehicle, VehicleStatus
from ..control.fleet_manager import fleet_manager, FleetStats
from ..geographic.gps_tracker import gps_tracker
from ..control.monitoring import monitoring_system
from ..control.alert_system import alert_system, AlertCategory, AlertPriority

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/h/fleet", tags=["Fleet"])


@router.get("/", summary="Get fleet overview")
async def get_fleet_overview() -> Dict[str, Any]:
    """Get overview of the entire fleet"""
    stats = fleet_manager.stats
    
    return {
        "helicopters": {
            "total": stats.total_helicopters,
            "in_flight": stats.in_flight,
            "grounded": stats.grounded,
            "maintenance": stats.maintenance
        },
        "vehicles": {
            "total": stats.total_vehicles,
            "driving": stats.driving,
            "parked": stats.parked,
            "maintenance": stats.maintenance
        },
        "alerts": {
            "total": stats.active_alerts,
            "unacknowledged": len([a for a in alert_system.alerts.values() if not a.acknowledged])
        },
        "missions": {
            "total": stats.total_missions,
            "completed": stats.completed_missions
        }
    }


@router.get("/stats", summary="Get detailed fleet statistics")
async def get_fleet_stats() -> Dict[str, Any]:
    """Get detailed fleet statistics"""
    stats = fleet_manager.stats
    health = fleet_manager.get_fleet_health()
    
    return {
        "stats": stats.to_dict(),
        "health": health,
        "entity_count": fleet_manager.get_entity_count()
    }


@router.get("/entities", summary="List all fleet entities")
async def list_all_entities() -> Dict[str, Any]:
    """List all entities in the fleet"""
    entities = fleet_manager.get_all_entities()
    
    return {
        "total": len(entities),
        "helicopters": [
            {"id": eid, "type": "helicopter"} 
            for eid, e in entities.items() if e["type"] == "helicopter"
        ],
        "vehicles": [
            {"id": eid, "type": "vehicle"} 
            for eid, e in entities.items() if e["type"] == "vehicle"
        ]
    }


@router.get("/positions", summary="Get all entity positions")
async def get_all_positions() -> Dict[str, Any]:
    """Get current positions of all entities"""
    positions = {}
    
    for entity_id, entity_data in gps_tracker.entities.items():
        location = entity_data.get("location", {})
        positions[entity_id] = {
            "type": entity_data.get("type", "unknown"),
            "latitude": location.get("latitude", 0.0),
            "longitude": location.get("longitude", 0.0),
            "altitude": location.get("altitude", 0.0),
            "heading": location.get("heading", 0.0),
            "speed": location.get("speed", 0.0),
            "status": entity_data.get("status", "unknown"),
            "timestamp": location.get("timestamp", "")
        }
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "positions": positions
    }


@router.get("/status", summary="Get fleet status")
async def get_fleet_status() -> Dict[str, Any]:
    """Get current status of the fleet"""
    return {
        "helicopters": {
            "in_flight": [h.helicopter_id for h in fleet_manager.get_helicopters_in_flight()],
            "grounded": [h.helicopter_id for h in fleet_manager.get_helicopters_grounded()],
            "maintenance": [
                h.helicopter_id for h in fleet_manager.list_helicopters() 
                if h.status == HelicopterStatus.MAINTENANCE
            ]
        },
        "vehicles": {
            "driving": [v.vehicle_id for v in fleet_manager.get_vehicles_driving()],
            "parked": [v.vehicle_id for v in fleet_manager.get_vehicles_parked()],
            "maintenance": [
                v.vehicle_id for v in fleet_manager.list_vehicles() 
                if v.status == VehicleStatus.MAINTENANCE
            ]
        }
    }


@router.get("/near", summary="Find entities near a location")
async def find_entities_near(
    lat: float,
    lng: float,
    radius: float = 1000.0
) -> List[Dict[str, Any]]:
    """
    Find all entities near a specific location
    
    Parameters:
    - lat: Latitude
    - lng: Longitude
    - radius: Search radius in meters
    """
    return fleet_manager.get_entities_near_location(lat, lng, radius)


@router.get("/alerts", summary="List fleet alerts")
async def list_fleet_alerts(
    acknowledged: Optional[bool] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    List fleet alerts with optional filters
    
    Parameters:
    - acknowledged: Filter by acknowledged status
    - priority: Filter by priority
    - category: Filter by category
    - limit: Maximum number of alerts to return
    """
    alerts = alert_system.get_alerts(
        acknowledged=acknowledged,
        priority=AlertPriority(priority) if priority else None,
        category=AlertCategory(category) if category else None,
        limit=limit
    )
    
    return [a.to_dict() for a in alerts]


@router.post("/alerts/{alert_id}/acknowledge", summary="Acknowledge an alert")
async def acknowledge_alert(
    alert_id: str,
    acknowledged_by: str = "system"
) -> Dict[str, Any]:
    """Acknowledge a fleet alert"""
    if not alert_system.acknowledge_alert(alert_id, acknowledged_by):
        raise HTTPException(status_code=404, detail="Alert not found")
    
    logger.info(f"Acknowledged alert {alert_id} by {acknowledged_by}")
    return {"message": "Alert acknowledged", "alert_id": alert_id}


@router.post("/alerts", summary="Create a fleet alert")
async def create_fleet_alert(
    alert_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Create a new fleet alert"""
    alert_id = alert_system.create_alert(
        alert_type=alert_data.get("alert_type", "custom"),
        message=alert_data.get("message", ""),
        entity_id=alert_data.get("entity_id", ""),
        entity_type=alert_data.get("entity_type", ""),
        category=AlertCategory(alert_data.get("category", "custom")),
        priority=AlertPriority(alert_data.get("priority", "medium")),
        severity=alert_data.get("severity", "medium"),
        metadata=alert_data.get("metadata", {}),
        source=alert_data.get("source", "api")
    )
    
    logger.info(f"Created fleet alert {alert_id}")
    return {"alert_id": alert_id}


@router.get("/monitoring", summary="Get monitoring data")
async def get_monitoring_data() -> Dict[str, Any]:
    """Get monitoring data for all entities"""
    monitoring_data = monitoring_system.get_all_monitoring_data()
    
    result = {}
    for entity_id, data in monitoring_data.items():
        result[entity_id] = {
            "entity_type": data.entity_type,
            "last_update": data.last_update.isoformat(),
            "position_count": len(data.position_history),
            "speed_count": len(data.speed_history),
            "alert_count": len(data.alerts)
        }
    
    return {"monitoring": result}


@router.get("/monitoring/{entity_id}", summary="Get monitoring data for entity")
async def get_entity_monitoring_data(entity_id: str) -> Dict[str, Any]:
    """Get monitoring data for a specific entity"""
    data = monitoring_system.get_monitoring_data(entity_id)
    if not data:
        raise HTTPException(status_code=404, detail="Entity not found")
    
    return data.to_dict()


@router.get("/monitoring/stats", summary="Get monitoring statistics")
async def get_monitoring_stats() -> Dict[str, Any]:
    """Get monitoring system statistics"""
    stats = monitoring_system.get_stats()
    
    result = {}
    for stream_id, stream_stats in stats.items():
        result[stream_id] = stream_stats.to_dict()
    
    return result


@router.get("/health", summary="Get fleet health status")
async def get_fleet_health() -> Dict[str, Any]:
    """Get overall fleet health status"""
    return fleet_manager.get_fleet_health()


@router.post("/emergency", summary="Trigger emergency protocol")
async def trigger_emergency(
    entity_id: str,
    entity_type: str,
    reason: str = "Manual trigger"
) -> Dict[str, Any]:
    """
    Trigger emergency protocol for an entity
    
    Parameters:
    - entity_id: ID of the entity
    - entity_type: Type of entity (helicopter or vehicle)
    - reason: Reason for emergency
    """
    # Update entity status to emergency
    if entity_type == "helicopter":
        fleet_manager.update_helicopter_status(entity_id, HelicopterStatus.EMERGENCY)
    elif entity_type == "vehicle":
        fleet_manager.update_vehicle_status(entity_id, VehicleStatus.EMERGENCY)
    
    # Create alert
    alert_id = alert_system.create_alert(
        alert_type="emergency",
        message=f"EMERGENCY: {entity_type} {entity_id} - {reason}",
        entity_id=entity_id,
        entity_type=entity_type,
        category=AlertCategory.SAFETY,
        priority=AlertPriority.CRITICAL,
        severity="critical",
        source="api"
    )
    
    logger.warning(f"Emergency triggered for {entity_type} {entity_id}: {reason}")
    return {
        "message": "Emergency protocol triggered",
        "entity_id": entity_id,
        "entity_type": entity_type,
        "alert_id": alert_id
    }


@router.get("/tracking", summary="Get real-time tracking data")
async def get_tracking_data() -> Dict[str, Any]:
    """Get real-time tracking data for all entities"""
    positions = {}
    
    for entity_id, entity_data in gps_tracker.entities.items():
        location = entity_data.get("location", {})
        positions[entity_id] = {
            "type": entity_data.get("type", "unknown"),
            "lat": location.get("latitude", 0.0),
            "lng": location.get("longitude", 0.0),
            "alt": location.get("altitude", 0.0),
            "speed": location.get("speed", 0.0),
            "heading": location.get("heading", 0.0),
            "status": entity_data.get("status", "unknown"),
            "timestamp": location.get("timestamp", "")
        }
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "entities": positions
    }


@router.get("/flying", summary="List all flying entities")
async def list_flying_entities() -> Dict[str, Any]:
    """List all entities currently flying or driving"""
    return {
        "helicopters": [
            h.to_dict() for h in fleet_manager.get_helicopters_in_flight()
        ],
        "vehicles": [
            v.to_dict() for v in fleet_manager.get_vehicles_driving()
        ]
    }

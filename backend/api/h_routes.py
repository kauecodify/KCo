"""
Backend API - H Module Routes
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

FastAPI routes for H module (Helicopter and Fleet Management)
"""

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from typing import Dict, Any, List, Optional
import logging

from H.api.helicopter_routes import router as helicopter_router
from H.api.fleet_routes import router as fleet_router
from H.control.fleet_manager import fleet_manager
from H.geographic.gps_tracker import gps_tracker
from H.control.monitoring import monitoring_system
from H.control.alert_system import alert_system

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/h", tags=["H Module"])

# Include sub-routers
router.include_router(helicopter_router)
router.include_router(fleet_router)


@router.get("/", summary="H Module Overview")
async def h_module_overview() -> Dict[str, Any]:
    """
    Get overview of H module (Helicopters and Fleet)
    """
    return {
        "module": "H",
        "description": "Helicopter Geographic Processing & Real-Time Control",
        "company": "KCo by Cília | Laboratory of K and RockNewVenture",
        "infrastructure": "Old But Gold TR8 IVSTO",
        "pre_seed_target": "$30M+ USD",
        "helicopters": {
            "total": len(fleet_manager.helicopters),
            "in_flight": len(fleet_manager.get_helicopters_in_flight()),
            "grounded": len(fleet_manager.get_helicopters_grounded())
        },
        "vehicles": {
            "total": len(fleet_manager.vehicles),
            "driving": len(fleet_manager.get_vehicles_driving()),
            "parked": len(fleet_manager.get_vehicles_parked())
        },
        "gps_tracking": {
            "entities": len(gps_tracker.entities),
            "is_running": gps_tracker.is_running
        },
        "monitoring": {
            "entities": len(monitoring_system.monitoring_data),
            "alerts": len(monitoring_system.alerts)
        },
        "fleet_health": fleet_manager.get_fleet_health()
    }


@router.get("/status", summary="H Module Status")
async def h_module_status() -> Dict[str, Any]:
    """
    Get status of H module services
    """
    return {
        "status": "operational",
        "timestamp": "2024-11-04T12:00:00Z",
        "services": {
            "gps_tracker": "running" if gps_tracker.is_running else "stopped",
            "fleet_manager": "running" if fleet_manager.is_running else "stopped",
            "monitoring_system": "running" if monitoring_system.is_running else "stopped",
            "alert_system": "running" if alert_system.is_running else "stopped"
        },
        "statistics": {
            "total_entities": len(gps_tracker.entities),
            "active_alerts": len([a for a in alert_system.alerts.values() if not a.acknowledged]),
            "monitored_entities": len(monitoring_system.monitoring_data)
        }
    }


@router.get("/entities", summary="List all H module entities")
async def list_h_entities() -> Dict[str, Any]:
    """
    List all entities managed by H module
    """
    entities = fleet_manager.get_all_entities()
    
    helicopters = []
    vehicles = []
    
    for entity_id, entity_data in entities.items():
        if entity_data["type"] == "helicopter":
            helicopters.append({
                "id": entity_id,
                "type": "helicopter",
                "data": entity_data["data"]
            })
        elif entity_data["type"] == "vehicle":
            vehicles.append({
                "id": entity_id,
                "type": "vehicle",
                "data": entity_data["data"]
            })
    
    return {
        "helicopters": helicopters,
        "vehicles": vehicles,
        "total": len(entities)
    }


@router.get("/positions", summary="Get all entity positions")
async def get_all_positions() -> Dict[str, Any]:
    """
    Get current positions of all H module entities
    """
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
        "timestamp": "2024-11-04T12:00:00Z",
        "positions": positions,
        "count": len(positions)
    }


@router.get("/alerts", summary="Get H module alerts")
async def get_h_alerts(
    acknowledged: Optional[bool] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Get alerts from H module
    """
    alerts = alert_system.get_alerts(
        acknowledged=acknowledged,
        limit=limit
    )
    
    return [a.to_dict() for a in alerts]


@router.post("/start", summary="Start H module services")
async def start_h_services() -> Dict[str, Any]:
    """
    Start all H module services
    """
    try:
        import asyncio
        
        # Start GPS tracker
        if not gps_tracker.is_running:
            asyncio.create_task(gps_tracker.start())
        
        # Start fleet manager
        if not fleet_manager.is_running:
            asyncio.create_task(fleet_manager.start())
        
        # Start monitoring system
        if not monitoring_system.is_running:
            asyncio.create_task(monitoring_system.start())
        
        # Start alert system
        if not alert_system.is_running:
            asyncio.create_task(alert_system.start())
        
        logger.info("H Module services started")
        return {
            "message": "H Module services started",
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error starting H module services: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stop", summary="Stop H module services")
async def stop_h_services() -> Dict[str, Any]:
    """
    Stop all H module services
    """
    try:
        await gps_tracker.stop()
        await fleet_manager.stop()
        await monitoring_system.stop()
        await alert_system.stop()
        
        logger.info("H Module services stopped")
        return {
            "message": "H Module services stopped",
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error stopping H module services: {e}")
        raise HTTPException(status_code=500, detail=str(e))

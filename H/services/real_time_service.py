"""
H Module - Real-Time Service
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Real-time data processing and WebSocket service
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set
import json
import uuid

from ..models.helicopter import Helicopter, HelicopterStatus
from ..models.vehicle import Vehicle, VehicleStatus
from ..models.telemetry import TelemetryPoint, TelemetrySource
from ..models.image_analysis import ImageAnalysis, ImageMetadata
from ..geographic.gps_tracker import gps_tracker
from ..control.fleet_manager import fleet_manager
from ..control.monitoring import monitoring_system
from ..control.alert_system import alert_system
from ..cloud.cloud_sync import cloud_sync

logger = logging.getLogger(__name__)


@dataclass
class WebSocketClient:
    """WebSocket client connection"""
    client_id: str
    websocket: Any
    subscribed_entities: Set[str] = field(default_factory=set)
    subscribed_types: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_ping: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "client_id": self.client_id,
            "subscribed_entities": list(self.subscribed_entities),
            "subscribed_types": list(self.subscribed_types),
            "connected_at": self.connected_at.isoformat(),
            "last_ping": self.last_ping.isoformat()
        }


@dataclass
class RealTimeEvent:
    """Real-time event for WebSocket broadcast"""
    event_type: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = field(default_factory=dict)
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "event_type": self.event_type,
            "timestamp": self.timestamp.isoformat(),
            "data": self.data
        }
        if self.entity_id:
            result["entity_id"] = self.entity_id
        if self.entity_type:
            result["entity_type"] = self.entity_type
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())


class RealTimeService:
    """
    Real-time service for WebSocket connections and live data
    
    Features:
    - WebSocket server for real-time updates
    - Entity subscription system
    - Event broadcasting
    - Connection management
    - Heartbeat monitoring
    """
    
    def __init__(self):
        """Initialize real-time service"""
        self.clients: Dict[str, WebSocketClient] = {}
        self.event_queue = asyncio.Queue()
        self.is_running = False
        self.broadcast_interval = 0.1  # seconds
        self.ping_interval = 30.0  # seconds
        self.max_inactive = 60.0  # seconds
        
        logger.info("Real-Time Service initialized")
    
    async def start(self) -> None:
        """Start the real-time service"""
        if self.is_running:
            logger.warning("Real-Time Service is already running")
            return
        
        self.is_running = True
        logger.info("Real-Time Service started")
        
        # Start event processor
        asyncio.create_task(self._process_events())
        
        # Start ping monitor
        asyncio.create_task(self._monitor_connections())
    
    async def stop(self) -> None:
        """Stop the real-time service"""
        self.is_running = False
        
        # Close all connections
        for client_id, client in self.clients.items():
            try:
                await client.websocket.close()
            except:
                pass
        
        self.clients.clear()
        logger.info("Real-Time Service stopped")
    
    async def _process_events(self) -> None:
        """Process events from the queue"""
        while self.is_running:
            try:
                # Wait for events with timeout
                try:
                    event = await asyncio.wait_for(
                        self.event_queue.get(),
                        timeout=self.broadcast_interval
                    )
                    await self._broadcast_event(event)
                    self.event_queue.task_done()
                except asyncio.TimeoutError:
                    # No events, continue
                    pass
                
                # Always broadcast current state to subscribers
                await self._broadcast_current_state()
                
            except Exception as e:
                logger.error(f"Error processing events: {e}")
    
    async def _broadcast_event(self, event: RealTimeEvent) -> None:
        """Broadcast an event to all subscribed clients"""
        for client_id, client in self.clients.items():
            # Check if client is subscribed to this entity or type
            if (not event.entity_id or 
                event.entity_id in client.subscribed_entities or
                event.entity_type in client.subscribed_types or
                "all" in client.subscribed_types):
                
                try:
                    await client.websocket.send_text(event.to_json())
                except Exception as e:
                    logger.error(f"Error sending to client {client_id}: {e}")
    
    async def _broadcast_current_state(self) -> None:
        """Broadcast current state to all clients"""
        # Get all positions
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
        
        # Create state event
        event = RealTimeEvent(
            event_type="state_update",
            data={
                "positions": positions,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        
        await self._broadcast_event(event)
    
    async def _monitor_connections(self) -> None:
        """Monitor client connections and send pings"""
        while self.is_running:
            try:
                await asyncio.sleep(self.ping_interval)
                
                # Send ping to all clients
                for client_id, client in list(self.clients.items()):
                    try:
                        await client.websocket.send_text(json.dumps({
                            "event_type": "ping",
                            "timestamp": datetime.utcnow().isoformat()
                        }))
                        client.last_ping = datetime.utcnow()
                    except Exception as e:
                        logger.error(f"Error sending ping to {client_id}: {e}")
                        await self._remove_client(client_id)
                
                # Check for inactive clients
                for client_id, client in list(self.clients.items()):
                    inactive = (datetime.utcnow() - client.last_ping).total_seconds()
                    if inactive > self.max_inactive:
                        logger.info(f"Removing inactive client {client_id}")
                        await self._remove_client(client_id)
                
            except Exception as e:
                logger.error(f"Error monitoring connections: {e}")
    
    async def _remove_client(self, client_id: str) -> None:
        """Remove a client connection"""
        if client_id in self.clients:
            client = self.clients[client_id]
            try:
                await client.websocket.close()
            except:
                pass
            del self.clients[client_id]
            logger.info(f"Removed client {client_id}")
    
    async def add_client(self, websocket: Any, client_id: Optional[str] = None) -> str:
        """
        Add a new WebSocket client
        
        Args:
            websocket: WebSocket connection
            client_id: Optional client ID
            
        Returns:
            Client ID
        """
        if client_id is None:
            client_id = str(uuid.uuid4())
        
        client = WebSocketClient(
            client_id=client_id,
            websocket=websocket
        )
        
        self.clients[client_id] = client
        logger.info(f"Added client {client_id}")
        
        return client_id
    
    async def remove_client(self, client_id: str) -> None:
        """Remove a WebSocket client"""
        await self._remove_client(client_id)
    
    async def subscribe(self, client_id: str, entity_id: str) -> None:
        """Subscribe a client to an entity"""
        if client_id in self.clients:
            self.clients[client_id].subscribed_entities.add(entity_id)
            logger.info(f"Client {client_id} subscribed to entity {entity_id}")
    
    async def unsubscribe(self, client_id: str, entity_id: str) -> None:
        """Unsubscribe a client from an entity"""
        if client_id in self.clients:
            self.clients[client_id].subscribed_entities.discard(entity_id)
            logger.info(f"Client {client_id} unsubscribed from entity {entity_id}")
    
    async def subscribe_type(self, client_id: str, entity_type: str) -> None:
        """Subscribe a client to an entity type"""
        if client_id in self.clients:
            self.clients[client_id].subscribed_types.add(entity_type)
            logger.info(f"Client {client_id} subscribed to type {entity_type}")
    
    async def unsubscribe_type(self, client_id: str, entity_type: str) -> None:
        """Unsubscribe a client from an entity type"""
        if client_id in self.clients:
            self.clients[client_id].subscribed_types.discard(entity_type)
            logger.info(f"Client {client_id} unsubscribed from type {entity_type}")
    
    async def publish_event(self, event: RealTimeEvent) -> None:
        """Publish an event to the queue"""
        await self.event_queue.put(event)
    
    async def publish_position_update(self, entity_id: str, entity_type: str,
                                     position: Dict[str, float]) -> None:
        """Publish a position update event"""
        event = RealTimeEvent(
            event_type="position_update",
            entity_id=entity_id,
            entity_type=entity_type,
            data={
                "position": position,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        await self.publish_event(event)
    
    async def publish_status_update(self, entity_id: str, entity_type: str,
                                    status: str) -> None:
        """Publish a status update event"""
        event = RealTimeEvent(
            event_type="status_update",
            entity_id=entity_id,
            entity_type=entity_type,
            data={
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
        await self.publish_event(event)
    
    async def publish_alert(self, alert: Any) -> None:
        """Publish an alert event"""
        event = RealTimeEvent(
            event_type="alert",
            entity_id=alert.entity_id,
            entity_type=alert.entity_type,
            data=alert.to_dict()
        )
        await self.publish_event(event)
    
    async def publish_analysis(self, analysis: ImageAnalysis) -> None:
        """Publish an image analysis event"""
        event = RealTimeEvent(
            event_type="analysis_complete",
            entity_id=analysis.image_id,
            data=analysis.to_dict()
        )
        await self.publish_event(event)
    
    def get_clients(self) -> List[Dict[str, Any]]:
        """Get list of all connected clients"""
        return [client.to_dict() for client in self.clients.values()]
    
    def get_client_count(self) -> int:
        """Get number of connected clients"""
        return len(self.clients)
    
    async def broadcast_message(self, message: str, message_type: str = "message") -> None:
        """Broadcast a custom message to all clients"""
        event = RealTimeEvent(
            event_type=message_type,
            data={"message": message}
        )
        await self.publish_event(event)


class RealTimeDataProcessor:
    """
    Real-time data processor for streaming data
    
    Features:
    - Stream processing
    - Data aggregation
    - Anomaly detection
    - Real-time analytics
    """
    
    def __init__(self):
        """Initialize real-time data processor"""
        self.is_running = False
        self.data_handlers: Dict[str, Callable] = {}
        self.aggregation_interval = 1.0  # seconds
        
        logger.info("Real-Time Data Processor initialized")
    
    async def start(self) -> None:
        """Start the data processor"""
        if self.is_running:
            logger.warning("Real-Time Data Processor is already running")
            return
        
        self.is_running = True
        logger.info("Real-Time Data Processor started")
    
    async def stop(self) -> None:
        """Stop the data processor"""
        self.is_running = False
        logger.info("Real-Time Data Processor stopped")
    
    async def process_telemetry(self, telemetry: TelemetryPoint) -> None:
        """Process telemetry data in real-time"""
        # Check for data handlers
        for handler_id, handler in self.data_handlers.items():
            try:
                await handler(telemetry)
            except Exception as e:
                logger.error(f"Error in telemetry handler {handler_id}: {e}")
        
        # Check for anomalies
        await self._check_anomalies(telemetry)
    
    async def _check_anomalies(self, telemetry: TelemetryPoint) -> None:
        """Check telemetry data for anomalies"""
        # This would use the monitoring system to check thresholds
        pass
    
    async def process_position(self, entity_id: str, entity_type: str,
                              position: Dict[str, float]) -> None:
        """Process position data in real-time"""
        # Update GPS tracker
        gps_tracker.entities[entity_id]["location"] = position
        
        # Check geofences
        geofences = gps_tracker.check_geofences(entity_id, position)
        
        # Publish update
        real_time_service.publish_position_update(entity_id, entity_type, position)
    
    async def process_analysis(self, analysis: ImageAnalysis) -> None:
        """Process image analysis in real-time"""
        # Publish analysis event
        await real_time_service.publish_analysis(analysis)
        
        # Check for anomalies in analysis
        for anomaly in analysis.anomalies:
            if anomaly.severity.value in ["critical", "high"]:
                # Create alert
                alert_system.create_alert(
                    alert_type="anomaly_detected",
                    message=f"Anomaly detected: {anomaly.anomaly_type}",
                    entity_id=analysis.image_id,
                    entity_type="image",
                    severity=anomaly.severity.value,
                    metadata={"analysis_id": analysis.analysis_id}
                )
    
    def add_data_handler(self, handler_id: str, handler: Callable) -> None:
        """Add a custom data handler"""
        self.data_handlers[handler_id] = handler
        logger.info(f"Added data handler {handler_id}")
    
    def remove_data_handler(self, handler_id: str) -> None:
        """Remove a data handler"""
        if handler_id in self.data_handlers:
            del self.data_handlers[handler_id]
            logger.info(f"Removed data handler {handler_id}")


# Create global instances
real_time_service = RealTimeService()
real_time_processor = RealTimeDataProcessor()

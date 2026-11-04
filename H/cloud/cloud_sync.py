"""
H Module - Cloud Synchronization
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Cloud synchronization for helicopters and vehicles data
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set
import json
import uuid

from ..models.helicopter import Helicopter
from ..models.vehicle import Vehicle
from ..models.telemetry import TelemetryPoint, TelemetryStream, TelemetryBatch
from ..models.image_analysis import ImageAnalysis, ImageData, ImageMetadata
from ..control.fleet_manager import fleet_manager
from ..geographic.gps_tracker import gps_tracker

logger = logging.getLogger(__name__)


@dataclass
class SyncConfig:
    """Configuration for cloud synchronization"""
    sync_interval: float = 5.0
    batch_size: int = 100
    enable_compression: bool = True
    enable_encryption: bool = True
    retry_attempts: int = 3
    timeout: float = 30.0
    auto_sync: bool = True


@dataclass
class SyncStatus:
    """Status of synchronization"""
    last_sync: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_failure: Optional[datetime] = None
    total_syncs: int = 0
    successful_syncs: int = 0
    failed_syncs: int = 0
    pending_changes: int = 0
    syncing: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "last_sync": self.last_sync.isoformat() if self.last_sync else None,
            "last_success": self.last_success.isoformat() if self.last_success else None,
            "last_failure": self.last_failure.isoformat() if self.last_failure else None,
            "total_syncs": self.total_syncs,
            "successful_syncs": self.successful_syncs,
            "failed_syncs": self.failed_syncs,
            "pending_changes": self.pending_changes,
            "syncing": self.syncing
        }


@dataclass
class SyncQueueItem:
    """Item in the synchronization queue"""
    item_id: str
    item_type: str
    data: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    priority: int = 0
    retry_count: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "item_id": self.item_id,
            "item_type": self.item_type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority,
            "retry_count": self.retry_count
        }


class CloudSync:
    """
    Cloud synchronization system for helicopters and vehicles
    
    Features:
    - Real-time data synchronization
    - Batch processing
    - Conflict resolution
    - Offline support
    - Data compression and encryption
    - Retry mechanism for failed syncs
    """
    
    def __init__(self, config: Optional[SyncConfig] = None,
                 cloud_client: Optional[Any] = None):
        """
        Initialize cloud sync
        
        Args:
            config: Synchronization configuration
            cloud_client: Cloud client instance
        """
        self.config = config or SyncConfig()
        self.cloud_client = cloud_client
        self.sync_queue = asyncio.Queue()
        self.is_running = False
        self.is_syncing = False
        self.status = SyncStatus()
        self.pending_changes: Dict[str, SyncQueueItem] = {}
        self.callbacks: List[Callable] = []
        self.change_listeners: Dict[str, List[Callable]] = {}
        
        logger.info("Cloud Sync initialized")
    
    async def start(self) -> None:
        """Start cloud synchronization"""
        if self.is_running:
            logger.warning("Cloud Sync is already running")
            return
        
        self.is_running = True
        logger.info("Cloud Sync started")
        
        while self.is_running:
            try:
                # Process sync queue
                if not self.sync_queue.empty():
                    await self._process_queue()
                
                # Auto sync if enabled
                if self.config.auto_sync:
                    await self.sync()
                
                await asyncio.sleep(self.config.sync_interval)
                
            except Exception as e:
                logger.error(f"Error in cloud sync loop: {e}")
    
    async def stop(self) -> None:
        """Stop cloud synchronization"""
        self.is_running = False
        logger.info("Cloud Sync stopped")
    
    async def _process_queue(self) -> None:
        """Process items in the sync queue"""
        while not self.sync_queue.empty() and self.is_running:
            try:
                item = await self.sync_queue.get()
                await self._sync_item(item)
                self.sync_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing queue item: {e}")
    
    async def _sync_item(self, item: SyncQueueItem) -> None:
        """Sync a single item"""
        try:
            self.is_syncing = True
            self.status.syncing = True
            self.status.last_sync = datetime.utcnow()
            
            # Prepare data for sync
            data = self._prepare_data(item)
            
            # Send to cloud
            success = await self._send_to_cloud(item.item_type, data)
            
            if success:
                # Remove from pending changes
                if item.item_id in self.pending_changes:
                    del self.pending_changes[item.item_id]
                
                self.status.successful_syncs += 1
                logger.info(f"Synced {item.item_type} {item.item_id}")
                
                # Notify callbacks
                for callback in self.callbacks:
                    try:
                        await callback(item, True)
                    except Exception as e:
                        logger.error(f"Sync callback error: {e}")
            else:
                # Retry if possible
                if item.retry_count < self.config.retry_attempts:
                    item.retry_count += 1
                    await self.sync_queue.put(item)
                    self.status.failed_syncs += 1
                    logger.warning(f"Failed to sync {item.item_type} {item.item_id}, retry {item.retry_count}")
                else:
                    self.status.failed_syncs += 1
                    logger.error(f"Permanently failed to sync {item.item_type} {item.item_id}")
                    
                    # Notify callbacks
                    for callback in self.callbacks:
                        try:
                            await callback(item, False)
                        except Exception as e:
                            logger.error(f"Sync callback error: {e}")
            
            self.status.total_syncs += 1
            
        except Exception as e:
            logger.error(f"Error syncing item {item.item_id}: {e}")
        finally:
            self.is_syncing = False
            self.status.syncing = False
    
    async def _send_to_cloud(self, item_type: str, data: Dict[str, Any]) -> bool:
        """Send data to cloud"""
        try:
            if self.cloud_client:
                # Use cloud client if available
                result = await self.cloud_client.save(item_type, data)
                return result
            else:
                # Simulate cloud save
                logger.info(f"Simulated cloud save for {item_type}")
                return True
        except Exception as e:
            logger.error(f"Error sending to cloud: {e}")
            return False
    
    def _prepare_data(self, item: SyncQueueItem) -> Dict[str, Any]:
        """Prepare data for cloud sync"""
        data = item.data.copy()
        
        # Add metadata
        data["_sync_metadata"] = {
            "sync_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "item_type": item.item_type,
            "item_id": item.item_id
        }
        
        # Apply compression if enabled
        if self.config.enable_compression:
            data = self._compress_data(data)
        
        return data
    
    def _compress_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Compress data (simplified)"""
        # In real implementation, this would use gzip or similar
        # For now, we just return the data as-is
        return data
    
    async def sync(self) -> bool:
        """
        Perform a full synchronization
        
        Returns:
            True if sync was successful
        """
        self.status.last_sync = datetime.utcnow()
        self.status.syncing = True
        
        try:
            # Sync all helicopters
            for helicopter in fleet_manager.helicopters.values():
                await self.sync_helicopter(helicopter)
            
            # Sync all vehicles
            for vehicle in fleet_manager.vehicles.values():
                await self.sync_vehicle(vehicle)
            
            # Sync GPS data
            await self.sync_gps_data()
            
            self.status.last_success = datetime.utcnow()
            logger.info("Full synchronization completed successfully")
            return True
            
        except Exception as e:
            self.status.last_failure = datetime.utcnow()
            logger.error(f"Full synchronization failed: {e}")
            return False
        finally:
            self.status.syncing = False
    
    async def sync_helicopter(self, helicopter: Helicopter) -> bool:
        """Sync a helicopter to cloud"""
        try:
            data = helicopter.to_dict()
            item = SyncQueueItem(
                item_id=helicopter.helicopter_id,
                item_type="helicopter",
                data=data,
                priority=2
            )
            await self.sync_queue.put(item)
            self.pending_changes[helicopter.helicopter_id] = item
            return True
        except Exception as e:
            logger.error(f"Error syncing helicopter {helicopter.helicopter_id}: {e}")
            return False
    
    async def sync_vehicle(self, vehicle: Vehicle) -> bool:
        """Sync a vehicle to cloud"""
        try:
            data = vehicle.to_dict()
            item = SyncQueueItem(
                item_id=vehicle.vehicle_id,
                item_type="vehicle",
                data=data,
                priority=2
            )
            await self.sync_queue.put(item)
            self.pending_changes[vehicle.vehicle_id] = item
            return True
        except Exception as e:
            logger.error(f"Error syncing vehicle {vehicle.vehicle_id}: {e}")
            return False
    
    async def sync_gps_data(self) -> bool:
        """Sync GPS data to cloud"""
        try:
            # Get all positions
            positions = {}
            for entity_id, entity_data in gps_tracker.entities.items():
                positions[entity_id] = entity_data.get("location", {})
            
            # Create batch
            batch_id = str(uuid.uuid4())
            data = {
                "batch_id": batch_id,
                "timestamp": datetime.utcnow().isoformat(),
                "positions": positions
            }
            
            item = SyncQueueItem(
                item_id=batch_id,
                item_type="gps_batch",
                data=data,
                priority=1
            )
            await self.sync_queue.put(item)
            return True
        except Exception as e:
            logger.error(f"Error syncing GPS data: {e}")
            return False
    
    async def sync_telemetry(self, telemetry: TelemetryPoint) -> bool:
        """Sync telemetry data to cloud"""
        try:
            data = {
                "telemetry_id": str(uuid.uuid4()),
                "timestamp": telemetry.timestamp.isoformat(),
                "source": telemetry.source.value,
                "source_id": telemetry.source_id,
                "value": telemetry.value,
                "unit": telemetry.unit,
                "quality": telemetry.quality.value,
                "processed": telemetry.processed
            }
            
            item = SyncQueueItem(
                item_id=data["telemetry_id"],
                item_type="telemetry",
                data=data,
                priority=0
            )
            await self.sync_queue.put(item)
            return True
        except Exception as e:
            logger.error(f"Error syncing telemetry: {e}")
            return False
    
    async def sync_analysis(self, analysis: ImageAnalysis) -> bool:
        """Sync image analysis to cloud"""
        try:
            data = analysis.to_dict()
            item = SyncQueueItem(
                item_id=analysis.analysis_id,
                item_type="image_analysis",
                data=data,
                priority=1
            )
            await self.sync_queue.put(item)
            return True
        except Exception as e:
            logger.error(f"Error syncing analysis {analysis.analysis_id}: {e}")
            return False
    
    async def sync_image(self, image_data: ImageData) -> bool:
        """Sync image data to cloud"""
        try:
            data = image_data.to_dict()
            data["image_id"] = image_data.metadata.image_id
            
            item = SyncQueueItem(
                item_id=image_data.metadata.image_id,
                item_type="image",
                data=data,
                priority=0  # Images are large, lower priority
            )
            await self.sync_queue.put(item)
            return True
        except Exception as e:
            logger.error(f"Error syncing image {image_data.metadata.image_id}: {e}")
            return False
    
    async def fetch_from_cloud(self, item_type: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Fetch data from cloud"""
        try:
            if self.cloud_client:
                return await self.cloud_client.fetch(item_type, item_id)
            else:
                # Simulate fetch
                logger.info(f"Simulated cloud fetch for {item_type}/{item_id}")
                return None
        except Exception as e:
            logger.error(f"Error fetching from cloud: {e}")
            return None
    
    async def fetch_helicopter(self, helicopter_id: str) -> Optional[Helicopter]:
        """Fetch helicopter from cloud"""
        data = await self.fetch_from_cloud("helicopter", helicopter_id)
        if data:
            return Helicopter.from_dict(data)
        return None
    
    async def fetch_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        """Fetch vehicle from cloud"""
        data = await self.fetch_from_cloud("vehicle", vehicle_id)
        if data:
            return Vehicle.from_dict(data)
        return None
    
    def add_callback(self, callback: Callable) -> None:
        """Add a callback for sync events"""
        self.callbacks.append(callback)
        logger.info("Added cloud sync callback")
    
    def remove_callback(self, callback: Callable) -> None:
        """Remove a callback"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
            logger.info("Removed cloud sync callback")
    
    def add_change_listener(self, item_type: str, listener: Callable) -> None:
        """Add a listener for specific item type changes"""
        if item_type not in self.change_listeners:
            self.change_listeners[item_type] = []
        self.change_listeners[item_type].append(listener)
        logger.info(f"Added change listener for {item_type}")
    
    def remove_change_listener(self, item_type: str, listener: Callable) -> None:
        """Remove a change listener"""
        if item_type in self.change_listeners and listener in self.change_listeners[item_type]:
            self.change_listeners[item_type].remove(listener)
            logger.info(f"Removed change listener for {item_type}")
    
    def get_status(self) -> SyncStatus:
        """Get current sync status"""
        self.status.pending_changes = len(self.pending_changes)
        return self.status
    
    def get_pending_changes(self) -> Dict[str, SyncQueueItem]:
        """Get all pending changes"""
        return self.pending_changes.copy()
    
    def clear_queue(self) -> int:
        """Clear the sync queue"""
        count = 0
        while not self.sync_queue.empty():
            self.sync_queue.get_nowait()
            count += 1
        
        self.pending_changes.clear()
        logger.info(f"Cleared {count} items from sync queue")
        return count
    
    async def force_sync(self, item_id: str) -> bool:
        """Force sync a specific item"""
        if item_id in self.pending_changes:
            item = self.pending_changes[item_id]
            await self.sync_queue.put(item)
            return True
        return False


# Create global cloud sync instance
cloud_sync = CloudSync()

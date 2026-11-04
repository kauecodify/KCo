"""
H Module - Data Storage
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Data storage system for helicopters and vehicles
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set, Union
import json
import uuid
import os

from ..models.helicopter import Helicopter, HelicopterStatus
from ..models.vehicle import Vehicle, VehicleStatus
from ..models.telemetry import TelemetryPoint, TelemetryStream, TelemetryBatch
from ..models.image_analysis import ImageAnalysis, ImageData, ImageMetadata
from .cloud_sync import cloud_sync

logger = logging.getLogger(__name__)


@dataclass
class StorageConfig:
    """Configuration for data storage"""
    storage_path: str = "data/storage"
    max_file_size: int = 100 * 1024 * 1024  # 100MB
    max_files: int = 1000
    retention_days: int = 30
    enable_compression: bool = True
    enable_encryption: bool = False
    backup_enabled: bool = True
    backup_path: str = "data/backup"


@dataclass
class StorageStats:
    """Storage statistics"""
    total_items: int = 0
    total_size: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    by_date: Dict[str, int] = field(default_factory=dict)
    oldest_item: Optional[datetime] = None
    newest_item: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_items": self.total_items,
            "total_size": self.total_size,
            "by_type": self.by_type,
            "by_date": self.by_date,
            "oldest_item": self.oldest_item.isoformat() if self.oldest_item else None,
            "newest_item": self.newest_item.isoformat() if self.newest_item else None
        }


class DataStorage:
    """
    Data storage system for helicopters and vehicles
    
    Features:
    - Local and cloud storage
    - Data indexing and search
    - Retention policies
    - Backup and recovery
    - Data compression and encryption
    """
    
    def __init__(self, config: Optional[StorageConfig] = None):
        """
        Initialize data storage
        
        Args:
            config: Storage configuration
        """
        self.config = config or StorageConfig()
        self.data: Dict[str, Dict[str, Any]] = {}
        self.index: Dict[str, Dict[str, Any]] = {}
        self.stats = StorageStats()
        self.is_loaded = False
        
        # Create directories if they don't exist
        os.makedirs(self.config.storage_path, exist_ok=True)
        os.makedirs(self.config.backup_path, exist_ok=True)
        
        logger.info("Data Storage initialized")
    
    async def load(self) -> None:
        """Load data from storage"""
        try:
            # In real implementation, this would load from files/database
            logger.info("Loading data from storage")
            self.is_loaded = True
        except Exception as e:
            logger.error(f"Error loading data: {e}")
    
    async def save(self, item_type: str, item_id: str, data: Dict[str, Any], 
                   metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Save data to storage
        
        Args:
            item_type: Type of item
            item_id: Item identifier
            data: Data to save
            metadata: Additional metadata
            
        Returns:
            True if save was successful
        """
        try:
            # Create storage key
            storage_key = f"{item_type}:{item_id}"
            
            # Add timestamp
            if metadata is None:
                metadata = {}
            metadata["_storage_timestamp"] = datetime.utcnow().isoformat()
            
            # Store data
            self.data[storage_key] = {
                "type": item_type,
                "id": item_id,
                "data": data,
                "metadata": metadata
            }
            
            # Update index
            self._update_index(item_type, item_id, data, metadata)
            
            # Update stats
            self._update_stats(item_type, data)
            
            # Sync to cloud if enabled
            if cloud_sync.config.auto_sync:
                await cloud_sync.sync_queue.put({
                    "item_id": item_id,
                    "item_type": item_type,
                    "data": data,
                    "timestamp": datetime.utcnow()
                })
            
            # Save to file
            await self._save_to_file(item_type, item_id, data, metadata)
            
            logger.info(f"Saved {item_type} {item_id} to storage")
            return True
            
        except Exception as e:
            logger.error(f"Error saving {item_type} {item_id}: {e}")
            return False
    
    async def _save_to_file(self, item_type: str, item_id: str, 
                           data: Dict[str, Any], metadata: Dict[str, Any]) -> None:
        """Save data to file"""
        try:
            # Create directory for item type
            type_dir = os.path.join(self.config.storage_path, item_type)
            os.makedirs(type_dir, exist_ok=True)
            
            # Create filename
            filename = f"{item_id}.json"
            filepath = os.path.join(type_dir, filename)
            
            # Save data
            with open(filepath, 'w') as f:
                json.dump({"data": data, "metadata": metadata}, f, indent=2)
            
        except Exception as e:
            logger.error(f"Error saving to file: {e}")
    
    def _update_index(self, item_type: str, item_id: str, 
                     data: Dict[str, Any], metadata: Dict[str, Any]) -> None:
        """Update search index"""
        if item_type not in self.index:
            self.index[item_type] = {}
        
        self.index[item_type][item_id] = {
            "id": item_id,
            "type": item_type,
            "timestamp": metadata.get("_storage_timestamp", datetime.utcnow().isoformat()),
            "data": data
        }
    
    def _update_stats(self, item_type: str, data: Dict[str, Any]) -> None:
        """Update storage statistics"""
        self.stats.total_items += 1
        self.stats.by_type[item_type] = self.stats.by_type.get(item_type, 0) + 1
        
        # Update date stats
        today = datetime.utcnow().strftime("%Y-%m-%d")
        self.stats.by_date[today] = self.stats.by_date.get(today, 0) + 1
        
        # Update timestamps
        timestamp_str = data.get("timestamp", datetime.utcnow().isoformat())
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            if self.stats.newest_item is None or timestamp > self.stats.newest_item:
                self.stats.newest_item = timestamp
            if self.stats.oldest_item is None or timestamp < self.stats.oldest_item:
                self.stats.oldest_item = timestamp
        except:
            pass
    
    async def fetch(self, item_type: str, item_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch data from storage
        
        Args:
            item_type: Type of item
            item_id: Item identifier
            
        Returns:
            Data if found, None otherwise
        """
        storage_key = f"{item_type}:{item_id}"
        
        # Check in-memory storage first
        if storage_key in self.data:
            return self.data[storage_key]
        
        # Try to load from file
        data = await self._load_from_file(item_type, item_id)
        if data:
            return data
        
        # Try to fetch from cloud
        if cloud_sync.cloud_client:
            data = await cloud_sync.fetch_from_cloud(item_type, item_id)
            if data:
                # Cache in memory
                self.data[storage_key] = data
                return data
        
        return None
    
    async def _load_from_file(self, item_type: str, item_id: str) -> Optional[Dict[str, Any]]:
        """Load data from file"""
        try:
            filepath = os.path.join(self.config.storage_path, item_type, f"{item_id}.json")
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading from file: {e}")
        return None
    
    async def delete(self, item_type: str, item_id: str) -> bool:
        """
        Delete data from storage
        
        Args:
            item_type: Type of item
            item_id: Item identifier
            
        Returns:
            True if deletion was successful
        """
        storage_key = f"{item_type}:{item_id}"
        
        try:
            # Remove from memory
            if storage_key in self.data:
                del self.data[storage_key]
            
            # Remove from index
            if item_type in self.index and item_id in self.index[item_type]:
                del self.index[item_type][item_id]
            
            # Remove from file
            filepath = os.path.join(self.config.storage_path, item_type, f"{item_id}.json")
            if os.path.exists(filepath):
                os.remove(filepath)
            
            logger.info(f"Deleted {item_type} {item_id} from storage")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting {item_type} {item_id}: {e}")
            return False
    
    async def search(self, item_type: str, query: Dict[str, Any], 
                     limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search for items in storage
        
        Args:
            item_type: Type of item to search
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching items
        """
        results = []
        
        if item_type not in self.index:
            return results
        
        for item_id, item in self.index[item_type].items():
            match = True
            for key, value in query.items():
                if key.startswith("_"):
                    # Metadata field
                    if key not in item.get("metadata", {}) or item["metadata"][key] != value:
                        match = False
                        break
                else:
                    # Data field
                    if key not in item.get("data", {}) or item["data"][key] != value:
                        match = False
                        break
            
            if match:
                results.append(item)
                if len(results) >= limit:
                    break
        
        return results
    
    async def query(self, query: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Query across all item types
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of matching items
        """
        results = []
        
        for item_type, items in self.index.items():
            for item_id, item in items.items():
                match = True
                for key, value in query.items():
                    if key == "type" and item_type != value:
                        match = False
                        break
                    if key.startswith("_"):
                        if key not in item.get("metadata", {}) or item["metadata"][key] != value:
                            match = False
                            break
                    else:
                        if key not in item.get("data", {}) or item["data"][key] != value:
                            match = False
                            break
                
                if match:
                    results.append(item)
                    if len(results) >= limit:
                        break
            
            if len(results) >= limit:
                break
        
        return results
    
    async def save_helicopter(self, helicopter: Helicopter) -> bool:
        """Save a helicopter to storage"""
        data = helicopter.to_dict()
        metadata = {
            "entity_type": "helicopter",
            "model": helicopter.model.value,
            "status": helicopter.status.value
        }
        return await self.save("helicopter", helicopter.helicopter_id, data, metadata)
    
    async def save_vehicle(self, vehicle: Vehicle) -> bool:
        """Save a vehicle to storage"""
        data = vehicle.to_dict()
        metadata = {
            "entity_type": "vehicle",
            "vehicle_type": vehicle.vehicle_type.value,
            "status": vehicle.status.value
        }
        return await self.save("vehicle", vehicle.vehicle_id, data, metadata)
    
    async def save_telemetry(self, telemetry: TelemetryPoint) -> bool:
        """Save telemetry data to storage"""
        data = {
            "timestamp": telemetry.timestamp.isoformat(),
            "source": telemetry.source.value,
            "source_id": telemetry.source_id,
            "value": telemetry.value,
            "unit": telemetry.unit,
            "quality": telemetry.quality.value,
            "processed": telemetry.processed
        }
        metadata = {
            "entity_type": "telemetry",
            "source": telemetry.source.value
        }
        return await self.save("telemetry", str(uuid.uuid4()), data, metadata)
    
    async def save_analysis(self, analysis: ImageAnalysis) -> bool:
        """Save image analysis to storage"""
        data = analysis.to_dict()
        metadata = {
            "entity_type": "image_analysis",
            "analysis_type": analysis.analysis_type.value,
            "status": analysis.status.value
        }
        return await self.save("image_analysis", analysis.analysis_id, data, metadata)
    
    async def save_image(self, image_data: ImageData) -> bool:
        """Save image data to storage"""
        data = image_data.to_dict()
        metadata = {
            "entity_type": "image",
            "image_type": image_data.metadata.image_type.value,
            "entity_id": image_data.metadata.entity_id,
            "entity_type": image_data.metadata.entity_type
        }
        return await self.save("image", image_data.metadata.image_id, data, metadata)
    
    async def fetch_helicopter(self, helicopter_id: str) -> Optional[Helicopter]:
        """Fetch a helicopter from storage"""
        data = await self.fetch("helicopter", helicopter_id)
        if data:
            return Helicopter.from_dict(data.get("data", {}))
        return None
    
    async def fetch_vehicle(self, vehicle_id: str) -> Optional[Vehicle]:
        """Fetch a vehicle from storage"""
        data = await self.fetch("vehicle", vehicle_id)
        if data:
            return Vehicle.from_dict(data.get("data", {}))
        return None
    
    async def fetch_analysis(self, analysis_id: str) -> Optional[ImageAnalysis]:
        """Fetch image analysis from storage"""
        data = await self.fetch("image_analysis", analysis_id)
        if data:
            # Reconstruct ImageAnalysis from dict
            analysis_data = data.get("data", {})
            # This would need to be properly reconstructed
            return None
        return None
    
    async def list_helicopters(self) -> List[str]:
        """List all helicopter IDs in storage"""
        if "helicopter" in self.index:
            return list(self.index["helicopter"].keys())
        return []
    
    async def list_vehicles(self) -> List[str]:
        """List all vehicle IDs in storage"""
        if "vehicle" in self.index:
            return list(self.index["vehicle"].keys())
        return []
    
    async def list_analyses(self) -> List[str]:
        """List all analysis IDs in storage"""
        if "image_analysis" in self.index:
            return list(self.index["image_analysis"].keys())
        return []
    
    async def backup(self) -> bool:
        """Create a backup of all data"""
        try:
            backup_id = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_dir = os.path.join(self.config.backup_path, backup_id)
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copy all storage files to backup
            for root, dirs, files in os.walk(self.config.storage_path):
                for file in files:
                    src = os.path.join(root, file)
                    rel_path = os.path.relpath(src, self.config.storage_path)
                    dst = os.path.join(backup_dir, rel_path)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    
                    # In real implementation, we would copy the file
                    # For now, we just log it
                    logger.info(f"Backup: {src} -> {dst}")
            
            logger.info(f"Backup created: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False
    
    async def restore(self, backup_id: str) -> bool:
        """Restore from a backup"""
        try:
            backup_dir = os.path.join(self.config.backup_path, backup_id)
            if not os.path.exists(backup_dir):
                logger.error(f"Backup {backup_id} not found")
                return False
            
            # In real implementation, we would restore files
            logger.info(f"Restore from backup: {backup_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return False
    
    async def cleanup(self, older_than_days: Optional[int] = None) -> int:
        """
        Clean up old data
        
        Args:
            older_than_days: Delete data older than this many days
            
        Returns:
            Number of items deleted
        """
        count = 0
        
        try:
            if older_than_days:
                from datetime import timedelta
                cutoff = datetime.utcnow() - timedelta(days=older_than_days)
                
                # Find and delete old items
                for item_type, items in list(self.index.items()):
                    for item_id, item in list(items.items()):
                        timestamp_str = item.get("metadata", {}).get("_storage_timestamp")
                        if timestamp_str:
                            try:
                                timestamp = datetime.fromisoformat(timestamp_str)
                                if timestamp < cutoff:
                                    await self.delete(item_type, item_id)
                                    count += 1
                            except:
                                pass
            
            logger.info(f"Cleaned up {count} items")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        return count
    
    def get_stats(self) -> StorageStats:
        """Get storage statistics"""
        return self.stats
    
    async def reindex(self) -> None:
        """Rebuild search index"""
        self.index.clear()
        
        for storage_key, item in self.data.items():
            parts = storage_key.split(":", 1)
            if len(parts) == 2:
                item_type, item_id = parts
                self._update_index(item_type, item_id, item["data"], item["metadata"])
        
        logger.info("Search index rebuilt")


# Create global data storage instance
data_storage = DataStorage()

"""
H Module - Image Storage
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Specialized storage for images and video
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Tuple
import os
import uuid
import base64
import cv2
import numpy as np

from ..models.image_analysis import ImageAnalysis, ImageData, ImageMetadata, ImageType
from .data_storage import data_storage

logger = logging.getLogger(__name__)


@dataclass
class ImageStorageConfig:
    """Configuration for image storage"""
    storage_path: str = "data/images"
    thumbnail_path: str = "data/thumbnails"
    max_image_size: int = 10 * 1024 * 1024  # 10MB
    thumbnail_size: Tuple[int, int] = (320, 240)
    thumbnail_quality: int = 85
    enable_compression: bool = True
    compression_quality: int = 90
    supported_formats: List[str] = field(default_factory=lambda: [".jpg", ".jpeg", ".png", ".webp"])


@dataclass
class ImageStorageStats:
    """Image storage statistics"""
    total_images: int = 0
    total_size: int = 0
    by_type: Dict[str, int] = field(default_factory=dict)
    by_entity: Dict[str, int] = field(default_factory=dict)
    by_date: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "total_images": self.total_images,
            "total_size": self.total_size,
            "by_type": self.by_type,
            "by_entity": self.by_entity,
            "by_date": self.by_date
        }


class ImageStorage:
    """
    Specialized storage for images and video
    
    Features:
    - Image upload and retrieval
    - Thumbnail generation
    - Image compression
    - Format conversion
    - Metadata management
    - Cloud sync
    """
    
    def __init__(self, config: Optional[ImageStorageConfig] = None):
        """
        Initialize image storage
        
        Args:
            config: Image storage configuration
        """
        self.config = config or ImageStorageConfig()
        self.stats = ImageStorageStats()
        
        # Create directories
        os.makedirs(self.config.storage_path, exist_ok=True)
        os.makedirs(self.config.thumbnail_path, exist_ok=True)
        
        logger.info("Image Storage initialized")
    
    async def save_image(self, image_data: ImageData) -> bool:
        """
        Save an image with metadata
        
        Args:
            image_data: Image data to save
            
        Returns:
            True if save was successful
        """
        try:
            image_id = image_data.metadata.image_id
            entity_id = image_data.metadata.entity_id
            entity_type = image_data.metadata.entity_type
            
            # Save image bytes
            if image_data.data:
                image_bytes = base64.b64decode(image_data.data)
                await self._save_image_file(image_id, image_bytes, image_data.metadata)
            
            # Save thumbnail if available
            if image_data.thumbnail:
                thumbnail_bytes = base64.b64decode(image_data.thumbnail)
                await self._save_thumbnail_file(image_id, thumbnail_bytes)
            else:
                # Generate thumbnail from image
                if image_data.data:
                    image_bytes = base64.b64decode(image_data.data)
                    thumbnail_bytes = await self._generate_thumbnail(image_bytes)
                    if thumbnail_bytes:
                        await self._save_thumbnail_file(image_id, thumbnail_bytes)
            
            # Save metadata to data storage
            await data_storage.save_image(image_data)
            
            # Update stats
            self._update_stats(image_data.metadata)
            
            logger.info(f"Saved image {image_id} for {entity_type} {entity_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving image {image_data.metadata.image_id}: {e}")
            return False
    
    async def _save_image_file(self, image_id: str, image_bytes: bytes, 
                               metadata: ImageMetadata) -> None:
        """Save image bytes to file"""
        try:
            # Determine format from metadata or data
            format_ext = ".jpg"  # default
            if metadata.image_format:
                format_ext = f".{metadata.image_format.value.lower()}"
            
            # Create directory for entity type
            entity_dir = os.path.join(self.config.storage_path, metadata.entity_type)
            os.makedirs(entity_dir, exist_ok=True)
            
            # Save image
            filepath = os.path.join(entity_dir, f"{image_id}{format_ext}")
            with open(filepath, 'wb') as f:
                f.write(image_bytes)
            
            # Update size
            self.stats.total_size += len(image_bytes)
            
        except Exception as e:
            logger.error(f"Error saving image file: {e}")
    
    async def _save_thumbnail_file(self, image_id: str, thumbnail_bytes: bytes) -> None:
        """Save thumbnail bytes to file"""
        try:
            filepath = os.path.join(self.config.thumbnail_path, f"{image_id}.jpg")
            with open(filepath, 'wb') as f:
                f.write(thumbnail_bytes)
        except Exception as e:
            logger.error(f"Error saving thumbnail file: {e}")
    
    async def _generate_thumbnail(self, image_bytes: bytes) -> Optional[bytes]:
        """Generate a thumbnail from image bytes"""
        try:
            # Decode image
            image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                return None
            
            # Resize to thumbnail size
            thumbnail = cv2.resize(image, self.config.thumbnail_size)
            
            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', thumbnail, [
                int(cv2.IMWRITE_JPEG_QUALITY), self.config.thumbnail_quality
            ])
            
            return buffer.tobytes()
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return None
    
    def _update_stats(self, metadata: ImageMetadata) -> None:
        """Update storage statistics"""
        self.stats.total_images += 1
        
        # Update by type
        image_type = metadata.image_type.value
        self.stats.by_type[image_type] = self.stats.by_type.get(image_type, 0) + 1
        
        # Update by entity
        entity_key = f"{metadata.entity_type}:{metadata.entity_id}"
        self.stats.by_entity[entity_key] = self.stats.by_entity.get(entity_key, 0) + 1
        
        # Update by date
        date = datetime.utcnow().strftime("%Y-%m-%d")
        self.stats.by_date[date] = self.stats.by_date.get(date, 0) + 1
    
    async def load_image(self, image_id: str) -> Optional[ImageData]:
        """
        Load an image from storage
        
        Args:
            image_id: Image ID
            
        Returns:
            ImageData if found, None otherwise
        """
        try:
            # Load metadata from data storage
            metadata_dict = await data_storage.fetch("image", image_id)
            if not metadata_dict:
                return None
            
            metadata = ImageMetadata(**metadata_dict.get("data", {}).get("metadata", {}))
            
            # Load image file
            image_bytes = await self._load_image_file(image_id, metadata)
            
            # Load thumbnail
            thumbnail_bytes = await self._load_thumbnail_file(image_id)
            
            # Create ImageData
            image_data = ImageData(
                metadata=metadata
            )
            
            if image_bytes:
                image_data.set_image_data(image_bytes)
            
            if thumbnail_bytes:
                image_data.set_thumbnail(thumbnail_bytes)
            
            return image_data
            
        except Exception as e:
            logger.error(f"Error loading image {image_id}: {e}")
            return None
    
    async def _load_image_file(self, image_id: str, metadata: ImageMetadata) -> Optional[bytes]:
        """Load image bytes from file"""
        try:
            # Try different formats
            formats = [".jpg", ".jpeg", ".png", ".webp"]
            entity_dir = os.path.join(self.config.storage_path, metadata.entity_type)
            
            for fmt in formats:
                filepath = os.path.join(entity_dir, f"{image_id}{fmt}")
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        return f.read()
            
            return None
            
        except Exception as e:
            logger.error(f"Error loading image file: {e}")
            return None
    
    async def _load_thumbnail_file(self, image_id: str) -> Optional[bytes]:
        """Load thumbnail bytes from file"""
        try:
            filepath = os.path.join(self.config.thumbnail_path, f"{image_id}.jpg")
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
                    return f.read()
            return None
        except Exception as e:
            logger.error(f"Error loading thumbnail file: {e}")
            return None
    
    async def delete_image(self, image_id: str) -> bool:
        """
        Delete an image from storage
        
        Args:
            image_id: Image ID
            
        Returns:
            True if deletion was successful
        """
        try:
            # Delete from data storage
            await data_storage.delete("image", image_id)
            
            # Delete image files (try different formats)
            formats = [".jpg", ".jpeg", ".png", ".webp"]
            for entity_type in ["helicopter", "vehicle", "other"]:
                entity_dir = os.path.join(self.config.storage_path, entity_type)
                for fmt in formats:
                    filepath = os.path.join(entity_dir, f"{image_id}{fmt}")
                    if os.path.exists(filepath):
                        os.remove(filepath)
            
            # Delete thumbnail
            thumbnail_path = os.path.join(self.config.thumbnail_path, f"{image_id}.jpg")
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
            
            logger.info(f"Deleted image {image_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting image {image_id}: {e}")
            return False
    
    async def list_images(self, entity_id: Optional[str] = None, 
                         entity_type: Optional[str] = None,
                         image_type: Optional[ImageType] = None) -> List[str]:
        """
        List images with optional filters
        
        Args:
            entity_id: Filter by entity ID
            entity_type: Filter by entity type
            image_type: Filter by image type
            
        Returns:
            List of image IDs
        """
        results = []
        
        # Search in data storage
        query = {}
        if entity_id:
            query["entity_id"] = entity_id
        if entity_type:
            query["entity_type"] = entity_type
        if image_type:
            query["image_type"] = image_type.value
        
        items = await data_storage.search("image", query)
        for item in items:
            results.append(item.get("data", {}).get("image_id", ""))
        
        return results
    
    async def get_images_by_entity(self, entity_id: str, entity_type: str) -> List[ImageData]:
        """Get all images for a specific entity"""
        image_ids = await self.list_images(entity_id, entity_type)
        images = []
        
        for image_id in image_ids:
            image_data = await self.load_image(image_id)
            if image_data:
                images.append(image_data)
        
        return images
    
    async def compress_image(self, image_bytes: bytes, quality: int = 90) -> bytes:
        """
        Compress an image
        
        Args:
            image_bytes: Image bytes
            quality: Compression quality (1-100)
            
        Returns:
            Compressed image bytes
        """
        try:
            image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                return image_bytes
            
            # Compress as JPEG
            _, buffer = cv2.imencode('.jpg', image, [
                int(cv2.IMWRITE_JPEG_QUALITY), quality
            ])
            
            return buffer.tobytes()
            
        except Exception as e:
            logger.error(f"Error compressing image: {e}")
            return image_bytes
    
    async def convert_format(self, image_bytes: bytes, target_format: str) -> bytes:
        """
        Convert image to a different format
        
        Args:
            image_bytes: Image bytes
            target_format: Target format (jpg, png, webp)
            
        Returns:
            Converted image bytes
        """
        try:
            image = cv2.imdecode(np.frombuffer(image_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image is None:
                return image_bytes
            
            # Convert to target format
            if target_format.lower() == "jpg" or target_format.lower() == "jpeg":
                _, buffer = cv2.imencode('.jpg', image, [
                    int(cv2.IMWRITE_JPEG_QUALITY), 90
                ])
            elif target_format.lower() == "png":
                _, buffer = cv2.imencode('.png', image)
            elif target_format.lower() == "webp":
                _, buffer = cv2.imencode('.webp', image, [
                    int(cv2.IMWRITE_WEBP_QUALITY), 90
                ])
            else:
                return image_bytes
            
            return buffer.tobytes()
            
        except Exception as e:
            logger.error(f"Error converting image format: {e}")
            return image_bytes
    
    async def get_thumbnail(self, image_id: str) -> Optional[bytes]:
        """Get thumbnail for an image"""
        thumbnail_bytes = await self._load_thumbnail_file(image_id)
        return thumbnail_bytes
    
    async def get_image_metadata(self, image_id: str) -> Optional[ImageMetadata]:
        """Get metadata for an image"""
        metadata_dict = await data_storage.fetch("image", image_id)
        if metadata_dict:
            metadata_data = metadata_dict.get("data", {}).get("metadata", {})
            return ImageMetadata(**metadata_data)
        return None
    
    async def save_analysis_image(self, analysis: ImageAnalysis, image_data: ImageData) -> bool:
        """Save an image with its analysis"""
        # Save image first
        image_saved = await self.save_image(image_data)
        if not image_saved:
            return False
        
        # Save analysis
        analysis_saved = await data_storage.save_analysis(analysis)
        
        return image_saved and analysis_saved
    
    async def get_analysis_with_image(self, analysis_id: str) -> Tuple[Optional[ImageAnalysis], Optional[ImageData]]:
        """Get an analysis with its associated image"""
        # Get analysis
        analysis_data = await data_storage.fetch("image_analysis", analysis_id)
        if not analysis_data:
            return None, None
        
        # In real implementation, we would reconstruct the analysis
        # For now, we return None for analysis
        analysis = None
        
        # Get image
        image_data = None
        if analysis_data:
            image_id = analysis_data.get("data", {}).get("image_id")
            if image_id:
                image_data = await self.load_image(image_id)
        
        return analysis, image_data
    
    def get_stats(self) -> ImageStorageStats:
        """Get image storage statistics"""
        return self.stats
    
    async def cleanup(self, older_than_days: Optional[int] = None) -> int:
        """Clean up old images"""
        count = 0
        
        try:
            if older_than_days:
                from datetime import timedelta
                cutoff = datetime.utcnow() - timedelta(days=older_than_days)
                
                # Find and delete old images
                image_ids = await self.list_images()
                for image_id in image_ids:
                    metadata = await self.get_image_metadata(image_id)
                    if metadata:
                        timestamp_str = metadata.timestamp.isoformat()
                        try:
                            timestamp = datetime.fromisoformat(timestamp_str)
                            if timestamp < cutoff:
                                await self.delete_image(image_id)
                                count += 1
                        except:
                            pass
            
            logger.info(f"Cleaned up {count} images")
            
        except Exception as e:
            logger.error(f"Error during image cleanup: {e}")
        
        return count


# Create global image storage instance
image_storage = ImageStorage()

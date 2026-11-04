"""
H Module - Helicopter Geographic Processing & Real-Time Control
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

This module provides complete infrastructure for helicopter geographic tracking,
real-time image processing, and cloud-based control system for fleet management.
"""

# Import all submodules
from . import models
from . import geographic
from . import processing
from . import control
from . import cloud
from . import api
from . import services

# Re-export key classes and instances for convenience
from .models import (
    Helicopter,
    Vehicle,
    HelicopterStatus,
    VehicleStatus,
    Location,
    ImageAnalysis,
    ImageMetadata
)

from .geographic import (
    GPSTracker,
    GeofencingSystem,
    gps_tracker,
    geofencing_system
)

from .processing import (
    AerialImageProcessor,
    VideoStreamProcessor,
    aerial_processor,
    video_processor
)

from .control import (
    FleetManager,
    MonitoringSystem,
    AlertSystem,
    fleet_manager,
    monitoring_system,
    alert_system
)

from .cloud import (
    CloudSync,
    DataStorage,
    ImageStorage,
    cloud_sync,
    data_storage,
    image_storage
)

from .services import (
    RealTimeService,
    HelicopterService,
    real_time_service,
    helicopter_service
)

__all__ = [
    # Models
    "Helicopter",
    "Vehicle",
    "HelicopterStatus",
    "VehicleStatus",
    "Location",
    "ImageAnalysis",
    "ImageMetadata",
    # Geographic
    "GPSTracker",
    "GeofencingSystem",
    "gps_tracker",
    "geofencing_system",
    # Processing
    "AerialImageProcessor",
    "VideoStreamProcessor",
    "aerial_processor",
    "video_processor",
    # Control
    "FleetManager",
    "MonitoringSystem",
    "AlertSystem",
    "fleet_manager",
    "monitoring_system",
    "alert_system",
    # Cloud
    "CloudSync",
    "DataStorage",
    "ImageStorage",
    "cloud_sync",
    "data_storage",
    "image_storage",
    # Services
    "RealTimeService",
    "HelicopterService",
    "real_time_service",
    "helicopter_service"
]

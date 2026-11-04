"""
H Module - Models Package
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Data models for helicopter and vehicle tracking, telemetry, and image analysis
"""

from .helicopter import (
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

from .vehicle import (
    Vehicle,
    VehicleStatus,
    VehicleType,
    FuelType,
    VehicleLocation,
    VehicleEngine,
    VehicleFuel,
    VehicleBattery,
    VehicleTires,
    VehicleBrakes,
    VehicleCamera,
    VehicleAnomaly,
    VehicleMaintenance,
    VehicleDriver,
    VehicleRoute
)

from .telemetry import (
    TelemetryPoint,
    TelemetryStream,
    TelemetryBatch,
    TelemetryStatistics,
    TelemetryAlert,
    TelemetryConfig,
    TelemetrySource,
    DataQuality
)

from .image_analysis import (
    ImageMetadata,
    DetectedObject,
    DetectedAnomaly,
    ImageAnalysis,
    ImageData,
    BatchAnalysis,
    AnalysisConfig,
    ImageType,
    ImageFormat,
    AnalysisType,
    AnalysisStatus,
    Severity
)

__all__ = [
    # Helicopter models
    "Helicopter",
    "HelicopterStatus",
    "HelicopterModel",
    "Location",
    "EngineTelemetry",
    "FuelSystem",
    "HydraulicSystem",
    "ElectricalSystem",
    "CameraSettings",
    "Mission",
    "Pilot",
    "MaintenanceLog",
    "Alert",
    # Vehicle models
    "Vehicle",
    "VehicleStatus",
    "VehicleType",
    "FuelType",
    "VehicleLocation",
    "VehicleEngine",
    "VehicleFuel",
    "VehicleBattery",
    "VehicleTires",
    "VehicleBrakes",
    "VehicleCamera",
    "VehicleAnomaly",
    "VehicleMaintenance",
    "VehicleDriver",
    "VehicleRoute",
    # Telemetry models
    "TelemetryPoint",
    "TelemetryStream",
    "TelemetryBatch",
    "TelemetryStatistics",
    "TelemetryAlert",
    "TelemetryConfig",
    "TelemetrySource",
    "DataQuality",
    # Image analysis models
    "ImageMetadata",
    "DetectedObject",
    "DetectedAnomaly",
    "ImageAnalysis",
    "ImageData",
    "BatchAnalysis",
    "AnalysisConfig",
    "ImageType",
    "ImageFormat",
    "AnalysisType",
    "AnalysisStatus",
    "Severity"
]

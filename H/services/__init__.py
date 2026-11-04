"""
H Module - Services Package
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Business logic services for helicopters and vehicles
"""

from .real_time_service import (
    RealTimeService,
    RealTimeDataProcessor,
    WebSocketClient,
    RealTimeEvent,
    real_time_service,
    real_time_processor
)
from .helicopter_service import (
    HelicopterService,
    HelicopterServiceConfig,
    FlightPlan,
    helicopter_service
)

__all__ = [
    "RealTimeService",
    "RealTimeDataProcessor",
    "WebSocketClient",
    "RealTimeEvent",
    "real_time_service",
    "real_time_processor",
    "HelicopterService",
    "HelicopterServiceConfig",
    "FlightPlan",
    "helicopter_service"
]

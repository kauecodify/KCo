"""
H Module - API Package
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

API routes for helicopter and fleet management
"""

from .helicopter_routes import router as helicopter_router
from .fleet_routes import router as fleet_router

__all__ = [
    "helicopter_router",
    "fleet_router"
]

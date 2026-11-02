"""
KCo AI Cloud Processing Module - Old But Gold TR8 IVSTO
AI-Powered Image Processing with Cloud Database Integration
KCo by Cília | Laboratory of K and RockNewVenture

This module provides AI-based image processing capabilities with automatic
cloud database storage for all vehicle analyses, indexed by vehicle ID.
"""

from .cloud_image_processor import CloudImageProcessor
from .vehicle_analysis_storage import VehicleAnalysisStorage

__all__ = ['CloudImageProcessor', 'VehicleAnalysisStorage']

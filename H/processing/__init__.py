"""
H Module - Processing Package
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Image and video processing for helicopters and vehicles
"""

from .aerial_image_processor import (
    AerialImageProcessor,
    AerialProcessingConfig,
    ProcessingResult
)
from .video_stream_processor import (
    VideoStreamProcessor,
    VideoStreamConfig,
    StreamStats,
    TrackedObject
)

# Global instances
aerial_processor = AerialImageProcessor()
video_processor = VideoStreamProcessor()

__all__ = [
    "AerialImageProcessor",
    "AerialProcessingConfig",
    "ProcessingResult",
    "VideoStreamProcessor",
    "VideoStreamConfig",
    "StreamStats",
    "TrackedObject",
    "aerial_processor",
    "video_processor"
]

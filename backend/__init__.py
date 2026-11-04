"""
KCo Backend Infrastructure - Old But Gold TR8 IVSTO
Pre-Seed: $30M+ USD Target

Architecture: Microservices with LOWDATAESC Integration
Focus: Fleet Management, Anomaly Detection, Image Processing, Helicopter Tracking

H Module Integration: Complete helicopter geographic processing and real-time control
"""

__version__ = "1.0.0"
__author__ = "KCo Engineering Team"

# Initialize H Module
import H
from H.control.fleet_manager import fleet_manager
from H.geographic.gps_tracker import gps_tracker
from H.control.monitoring import monitoring_system
from H.control.alert_system import alert_system
from H.cloud.cloud_sync import cloud_sync
from H.cloud.data_storage import data_storage
from H.cloud.image_storage import image_storage

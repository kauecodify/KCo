"""
LOWDATAESC Integration Service - Connects KCo with LOWDATAESC platform
Purpose: Cross-sector data sharing and anomaly correlation
"""

from typing import Dict, Any, List, Optional
import logging
import requests
import json
from datetime import datetime

from backend.config.settings import settings
from backend.models.fleet import Anomaly, Vehicle, TelemetryData
from backend.models.image import ImageAnalysisResult

logger = logging.getLogger(__name__)


class LOWDATAESCService:
    """Service for integrating with LOWDATAESC platform"""
    
    def __init__(self):
        self.base_url = settings.LOWDATAESC_API_URL
        self.api_key = settings.LOWDATAESC_API_KEY
        self.timeout = settings.LOWDATAESC_TIMEOUT
        self.session = requests.Session()
        
        # Set headers
        self.session.headers.update({
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "X-Client": "KCo-Fleet-Intelligence"
        })
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make HTTP request to LOWDATAESC API"""
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                json=data,
                timeout=self.timeout
            )
            
            response.raise_for_status()
            return response.json()
        
        except requests.exceptions.RequestException as e:
            logger.error(f"LOWDATAESC API request failed: {e}")
            raise Exception(f"LOWDATAESC API error: {e}")
    
    def send_anomaly_data(self, anomalies: List[Anomaly]) -> Dict[str, Any]:
        """Send anomaly data to LOWDATAESC for cross-sector analysis"""
        if not anomalies:
            return {"status": "skipped", "reason": "No anomalies to send"}
        
        # Prepare data for LOWDATAESC
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "source": "KCo-Fleet",
            "sector": "automotive",
            "anomalies": []
        }
        
        for anomaly in anomalies:
            payload["anomalies"].append({
                "id": anomaly.id,
                "vehicle_id": anomaly.vehicle_id,
                "type": anomaly.anomaly_type,
                "severity": anomaly.severity,
                "description": anomaly.description,
                "value": anomaly.value,
                "threshold": anomaly.threshold,
                "timestamp": anomaly.timestamp.isoformat(),
                "metadata": anomaly.metadata
            })
        
        # Send to LOWDATAESC
        result = self._make_request("POST", "api/v1/anomalies/batch", payload)
        
        logger.info(f"Sent {len(anomalies)} anomalies to LOWDATAESC")
        return result
    
    def store_image_analysis(self, result: ImageAnalysisResult) -> Dict[str, Any]:
        """Store image analysis result in LOWDATAESC"""
        payload = {
            "timestamp": result.analysis_timestamp.isoformat(),
            "source": "KCo-Image-Processing",
            "sector": "automotive",
            "image_id": result.image_id,
            "vehicle_id": result.vehicle_id,
            "analysis": {
                "detected_objects": result.detected_objects,
                "anomalies": result.anomalies,
                "damage_assessment": result.damage_assessment,
                "confidence_score": result.confidence_score,
                "categories": result.categories
            }
        }
        
        result = self._make_request("POST", "api/v1/images/analysis", payload)
        
        logger.info(f"Stored image analysis {result.image_id} in LOWDATAESC")
        return result
    
    def sync_data(self) -> Dict[str, Any]:
        """Sync all pending data with LOWDATAESC"""
        # In production, this would sync all pending data
        # For demo, return success
        
        payload = {
            "source": "KCo",
            "timestamp": datetime.utcnow().isoformat(),
            "data_types": ["telemetry", "anomalies", "images"]
        }
        
        result = self._make_request("POST", "api/v1/sync", payload)
        
        logger.info("Data sync with LOWDATAESC completed")
        return result
    
    def get_connected_sectors(self) -> List[str]:
        """Get list of connected sectors from LOWDATAESC"""
        result = self._make_request("GET", "api/v1/sectors")
        
        sectors = result.get("sectors", [])
        logger.info(f"Retrieved {len(sectors)} connected sectors from LOWDATAESC")
        
        return sectors
    
    def query_cross_sector_anomalies(self, vehicle_id: str, days: int = 7) -> Dict[str, Any]:
        """Query LOWDATAESC for cross-sector anomalies related to vehicle"""
        payload = {
            "vehicle_id": vehicle_id,
            "days": days,
            "sectors": ["automotive", "insurance", "transportation", "manufacturing"]
        }
        
        result = self._make_request("POST", "api/v1/anomalies/cross-sector", payload)
        
        logger.info(f"Queried cross-sector anomalies for vehicle {vehicle_id}")
        return result
    
    def get_sector_insights(self, sector: str = "automotive") -> Dict[str, Any]:
        """Get insights from specific sector"""
        result = self._make_request("GET", f"api/v1/sectors/{sector}/insights")
        
        logger.info(f"Retrieved insights for sector {sector}")
        return result
    
    def send_telemetry_batch(self, telemetry_data: List[TelemetryData]) -> Dict[str, Any]:
        """Send batch of telemetry data to LOWDATAESC"""
        if not telemetry_data:
            return {"status": "skipped", "reason": "No telemetry data to send"}
        
        payload = {
            "timestamp": datetime.utcnow().isoformat(),
            "source": "KCo-Telemetry",
            "sector": "automotive",
            "data": []
        }
        
        for telemetry in telemetry_data:
            payload["data"].append({
                "vehicle_id": telemetry.vehicle_id,
                "timestamp": telemetry.timestamp.isoformat(),
                "location": telemetry.location,
                "speed": telemetry.speed,
                "engine_rpm": telemetry.engine_rpm,
                "engine_temperature": telemetry.engine_temperature,
                "oil_pressure": telemetry.oil_pressure,
                "battery_voltage": telemetry.battery_voltage,
                "fuel_level": telemetry.fuel_level,
                "obd_codes": telemetry.obd_codes
            })
        
        result = self._make_request("POST", "api/v1/telemetry/batch", payload)
        
        logger.info(f"Sent {len(telemetry_data)} telemetry points to LOWDATAESC")
        return result
    
    def get_correlated_anomalies(self, anomaly_id: str) -> Dict[str, Any]:
        """Get anomalies correlated with specific anomaly from other sectors"""
        result = self._make_request("GET", f"api/v1/anomalies/{anomaly_id}/correlations")
        
        logger.info(f"Retrieved correlated anomalies for {anomaly_id}")
        return result
    
    def register_vehicle(self, vehicle: Vehicle) -> Dict[str, Any]:
        """Register vehicle in LOWDATAESC for tracking"""
        payload = {
            "vehicle_id": vehicle.id,
            "vin": vehicle.vin,
            "make": vehicle.make,
            "model": vehicle.model,
            "year": vehicle.year,
            "country": vehicle.country,
            "instrumented": vehicle.instrumented,
            "instrumentation_date": vehicle.instrumentation_date.isoformat() if vehicle.instrumentation_date else None
        }
        
        result = self._make_request("POST", "api/v1/vehicles", payload)
        
        logger.info(f"Registered vehicle {vehicle.id} in LOWDATAESC")
        return result

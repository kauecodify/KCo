"""
Anomaly Detection Service - Detects anomalies in vehicle telemetry and images
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from backend.models.fleet import TelemetryData, Anomaly
from backend.models.image import ImageAnalysisResult, DamageAssessment
from backend.config.settings import settings

logger = logging.getLogger(__name__)


class AnomalyDetectionService:
    """Service for detecting anomalies in vehicle data"""
    
    def __init__(self):
        self.anomalies: Dict[str, Anomaly] = {}
        self.thresholds = settings.ANOMALY_THRESHOLDS
    
    def detect_anomalies(self, telemetry: TelemetryData) -> List[Anomaly]:
        """Detect anomalies in telemetry data"""
        anomalies = []
        
        # Check engine temperature
        if telemetry.engine_temperature > self.thresholds.get("engine_temperature", 120):
            anomalies.append(Anomaly(
                vehicle_id=telemetry.vehicle_id,
                telemetry_id=telemetry.id,
                timestamp=telemetry.timestamp,
                anomaly_type="engine_overheating",
                severity="critical",
                description=f"Engine temperature {telemetry.engine_temperature} exceeds threshold",
                value=telemetry.engine_temperature,
                threshold=self.thresholds["engine_temperature"],
                metadata={"current_temp": telemetry.engine_temperature, "rpm": telemetry.engine_rpm}
            ))
        
        # Check oil pressure
        if telemetry.oil_pressure < self.thresholds.get("oil_pressure", 20) or telemetry.oil_pressure > self.thresholds.get("oil_pressure", 80):
            anomalies.append(Anomaly(
                vehicle_id=telemetry.vehicle_id,
                telemetry_id=telemetry.id,
                timestamp=telemetry.timestamp,
                anomaly_type="oil_pressure_abnormal",
                severity="high",
                description=f"Oil pressure {telemetry.oil_pressure} outside normal range",
                value=telemetry.oil_pressure,
                threshold=self.thresholds["oil_pressure"],
                metadata={"pressure": telemetry.oil_pressure}
            ))
        
        # Check battery voltage
        if telemetry.battery_voltage > self.thresholds.get("battery_voltage", 14.5):
            anomalies.append(Anomaly(
                vehicle_id=telemetry.vehicle_id,
                telemetry_id=telemetry.id,
                timestamp=telemetry.timestamp,
                anomaly_type="battery_overvoltage",
                severity="medium",
                description=f"Battery voltage {telemetry.battery_voltage} exceeds threshold",
                value=telemetry.battery_voltage,
                threshold=self.thresholds["battery_voltage"],
                metadata={"voltage": telemetry.battery_voltage}
            ))
        
        # Check fuel efficiency
        if telemetry.fuel_efficiency < self.thresholds.get("fuel_efficiency", 0.7):
            anomalies.append(Anomaly(
                vehicle_id=telemetry.vehicle_id,
                telemetry_id=telemetry.id,
                timestamp=telemetry.timestamp,
                anomaly_type="fuel_efficiency_low",
                severity="low",
                description=f"Fuel efficiency {telemetry.fuel_efficiency} below optimal",
                value=telemetry.fuel_efficiency,
                threshold=self.thresholds["fuel_efficiency"],
                metadata={"efficiency": telemetry.fuel_efficiency, "fuel_level": telemetry.fuel_level}
            ))
        
        # Check for OBD codes
        if telemetry.obd_codes:
            for code in telemetry.obd_codes:
                anomalies.append(Anomaly(
                    vehicle_id=telemetry.vehicle_id,
                    telemetry_id=telemetry.id,
                    timestamp=telemetry.timestamp,
                    anomaly_type="obd_code",
                    severity="high",
                    description=f"OBD code detected: {code}",
                    value=0,
                    threshold=0,
                    metadata={"obd_code": code}
                ))
        
        # Check vibration levels
        if telemetry.vibration:
            for axis, value in telemetry.vibration.items():
                if value > self.thresholds.get("vibration_level", 0.5):
                    anomalies.append(Anomaly(
                        vehicle_id=telemetry.vehicle_id,
                        telemetry_id=telemetry.id,
                        timestamp=telemetry.timestamp,
                        anomaly_type=f"excessive_vibration_{axis}",
                        severity="medium",
                        description=f"Vibration on {axis} axis: {value}",
                        value=value,
                        threshold=self.thresholds["vibration_level"],
                        metadata={"axis": axis, "value": value}
                    ))
        
        return anomalies
    
    def detect_image_anomalies(self, image_result: ImageAnalysisResult) -> List[Dict[str, Any]]:
        """Detect anomalies from image analysis"""
        anomalies = []
        
        # Check for detected anomalies in image
        for anomaly in image_result.anomalies:
            anomalies.append({
                "type": "image_anomaly",
                "anomaly_type": anomaly.get("type", "unknown"),
                "severity": anomaly.get("severity", "medium"),
                "description": anomaly.get("description", ""),
                "confidence": anomaly.get("confidence", 0.0),
                "image_id": image_result.image_id,
                "vehicle_id": image_result.vehicle_id,
                "timestamp": image_result.analysis_timestamp.isoformat()
            })
        
        # Check damage assessment
        if image_result.damage_assessment:
            for damage_type, assessment in image_result.damage_assessment.items():
                if assessment.get("severity") in ["high", "critical"]:
                    anomalies.append({
                        "type": "damage",
                        "anomaly_type": f"damage_{damage_type}",
                        "severity": assessment.get("severity", "high"),
                        "description": assessment.get("description", f"Damage detected: {damage_type}"),
                        "estimated_cost": assessment.get("estimated_repair_cost", 0.0),
                        "image_id": image_result.image_id,
                        "vehicle_id": image_result.vehicle_id,
                        "timestamp": image_result.analysis_timestamp.isoformat()
                    })
        
        return anomalies
    
    def get_anomalies(self, vehicle_id: Optional[str] = None, severity: Optional[str] = None, limit: int = 100) -> List[Anomaly]:
        """Get anomalies with optional filters"""
        anomalies = list(self.anomalies.values())
        
        if vehicle_id:
            anomalies = [a for a in anomalies if a.vehicle_id == vehicle_id]
        
        if severity:
            anomalies = [a for a in anomalies if a.severity == severity]
        
        return anomalies[-limit:]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get anomaly statistics"""
        anomalies = list(self.anomalies.values())
        
        by_severity = {}
        for severity in ["low", "medium", "high", "critical"]:
            by_severity[severity] = len([a for a in anomalies if a.severity == severity])
        
        by_type = {}
        for anomaly in anomalies:
            by_type[anomaly.anomaly_type] = by_type.get(anomaly.anomaly_type, 0) + 1
        
        return {
            "total_anomalies": len(anomalies),
            "by_severity": by_severity,
            "by_type": by_type,
            "recent_24h": len([a for a in anomalies if (datetime.utcnow() - a.timestamp).days < 1])
        }
    
    def resolve_anomaly(self, anomaly_id: str, resolution_notes: str = "") -> Optional[Anomaly]:
        """Mark anomaly as resolved"""
        anomaly = self.anomalies.get(anomaly_id)
        if not anomaly:
            return None
        
        anomaly.resolved = True
        anomaly.resolution_notes = resolution_notes
        anomaly.resolved_at = datetime.utcnow()
        
        logger.info(f"Resolved anomaly {anomaly_id}: {resolution_notes}")
        return anomaly

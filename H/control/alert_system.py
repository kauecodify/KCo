"""
H Module - Alert System
KCo by Cilia | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Comprehensive alert system for fleet management
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable, Set
import uuid
import json

from ..models.helicopter import Helicopter, HelicopterStatus
from ..models.vehicle import Vehicle, VehicleStatus
from ..models.telemetry import TelemetryAlert, TelemetrySource
from ..geographic.geofencing import GeofenceAlert
from .fleet_manager import FleetAlert
from .monitoring import MonitoringAlert

logger = logging.getLogger(__name__)


@dataclass
class AlertPriority(Enum):
    """Alert priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class AlertCategory(Enum):
    """Alert categories"""
    SAFETY = "safety"
    MAINTENANCE = "maintenance"
    OPERATIONAL = "operational"
    SECURITY = "security"
    SYSTEM = "system"
    GEOFENCE = "geofence"
    ANOMALY = "anomaly"
    CUSTOM = "custom"


@dataclass
class UnifiedAlert:
    """
    Unified alert object that consolidates all alert types
    
    Attributes:
        alert_id: Unique identifier
        alert_type: Type of alert
        category: Alert category
        priority: Alert priority
        severity: Severity level
        message: Alert message
        entity_id: ID of the entity
        entity_type: Type of entity
        timestamp: Timestamp of the alert
        acknowledged: Whether alert has been acknowledged
        acknowledged_by: Who acknowledged the alert
        acknowledged_at: When alert was acknowledged
        metadata: Additional metadata
        source: Source of the alert
    """
    alert_id: str
    alert_type: str
    category: AlertCategory = AlertCategory.OPERATIONAL
    priority: AlertPriority = AlertPriority.MEDIUM
    severity: str = "medium"
    message: str = ""
    entity_id: str = ""
    entity_type: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: str = "system"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type,
            "category": self.category.value,
            "priority": self.priority.value,
            "severity": self.severity,
            "message": self.message,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "timestamp": self.timestamp.isoformat(),
            "acknowledged": self.acknowledged,
            "acknowledged_by": self.acknowledged_by,
            "acknowledged_at": self.acknowledged_at.isoformat() if self.acknowledged_at else None,
            "metadata": self.metadata,
            "source": self.source
        }
    
    @classmethod
    def from_fleet_alert(cls, alert: FleetAlert) -> "UnifiedAlert":
        """Create from FleetAlert"""
        priority = AlertPriority.CRITICAL if alert.severity == "critical" else \
                  AlertPriority.HIGH if alert.severity == "high" else \
                  AlertPriority.MEDIUM if alert.severity == "medium" else \
                  AlertPriority.LOW
        
        category = AlertCategory.SYSTEM
        if alert.alert_type == "emergency":
            category = AlertCategory.SAFETY
        elif alert.alert_type == "status_change":
            category = AlertCategory.OPERATIONAL
        
        return cls(
            alert_id=alert.alert_id,
            alert_type=alert.alert_type,
            category=category,
            priority=priority,
            severity=alert.severity,
            message=alert.message,
            entity_id=alert.entity_id,
            entity_type=alert.entity_type,
            timestamp=alert.timestamp,
            acknowledged=alert.acknowledged,
            acknowledged_by=alert.acknowledged_by,
            acknowledged_at=alert.acknowledged_at,
            metadata=alert.metadata,
            source="fleet"
        )
    
    @classmethod
    def from_monitoring_alert(cls, alert: MonitoringAlert) -> "UnifiedAlert":
        """Create from MonitoringAlert"""
        priority = AlertPriority.CRITICAL if alert.severity == "critical" else \
                  AlertPriority.HIGH if alert.severity == "high" else \
                  AlertPriority.MEDIUM if alert.severity == "medium" else \
                  AlertPriority.LOW
        
        category = AlertCategory.SYSTEM
        if alert.alert_type == "speed_exceeded":
            category = AlertCategory.SAFETY
        elif alert.alert_type == "low_altitude" or alert.alert_type == "high_altitude":
            category = AlertCategory.SAFETY
        elif alert.alert_type == "geofence_exit":
            category = AlertCategory.GEOFENCE
        
        return cls(
            alert_id=alert.alert_id,
            alert_type=alert.alert_type,
            category=category,
            priority=priority,
            severity=alert.severity,
            message=alert.message,
            entity_id=alert.entity_id,
            entity_type=alert.entity_type,
            timestamp=alert.timestamp,
            acknowledged=False,
            metadata=alert.metadata,
            source="monitoring"
        )
    
    @classmethod
    def from_geofence_alert(cls, alert: GeofenceAlert) -> "UnifiedAlert":
        """Create from GeofenceAlert"""
        priority = AlertPriority.CRITICAL if alert.alert_type == "entry" else \
                  AlertPriority.MEDIUM
        
        return cls(
            alert_id=alert.alert_id,
            alert_type=alert.alert_type,
            category=AlertCategory.GEOFENCE,
            priority=priority,
            severity="medium",
            message=alert.message,
            entity_id=alert.entity_id,
            entity_type=alert.entity_type,
            timestamp=alert.timestamp,
            acknowledged=alert.acknowledged,
            acknowledged_by=alert.acknowledged_by,
            acknowledged_at=alert.acknowledged_at,
            metadata={"geofence_id": alert.geofence_id},
            source="geofencing"
        )
    
    @classmethod
    def from_telemetry_alert(cls, alert: TelemetryAlert) -> "UnifiedAlert":
        """Create from TelemetryAlert"""
        priority = AlertPriority.CRITICAL if alert.severity == "critical" else \
                  AlertPriority.HIGH if alert.severity == "high" else \
                  AlertPriority.MEDIUM
        
        category = AlertCategory.SYSTEM
        if alert.source == TelemetrySource.ENGINE:
            category = AlertCategory.MAINTENANCE
        elif alert.source == TelemetrySource.GPS:
            category = AlertCategory.OPERATIONAL
        
        return cls(
            alert_id=alert.alert_id,
            alert_type=alert.condition,
            category=category,
            priority=priority,
            severity=alert.severity,
            message=alert.message,
            entity_id=alert.entity_id,
            entity_type=alert.entity_type,
            timestamp=alert.timestamp,
            acknowledged=alert.acknowledged,
            acknowledged_by=alert.acknowledged_by,
            acknowledged_at=alert.acknowledged_at,
            metadata={"source": alert.source.value, "value": alert.value, "threshold": alert.threshold},
            source="telemetry"
        )


class AlertSystem:
    """
    Comprehensive alert system for fleet management
    
    Features:
    - Unified alert management
    - Alert categorization and prioritization
    - Alert escalation
    - Notification management
    - Alert history and analytics
    - Integration with all subsystems
    """
    
    def __init__(self):
        """Initialize alert system"""
        self.alerts: Dict[str, UnifiedAlert] = {}
        self.alert_history: List[UnifiedAlert] = []
        self.max_history = 10000
        self.callbacks: Dict[str, List[Callable]] = {
            "all": [],
            "critical": [],
            "high": [],
            "medium": [],
            "low": [],
            "info": []
        }
        self.escalation_rules: Dict[str, Dict[str, Any]] = {}
        self.notification_channels: Dict[str, Callable] = {}
        self.is_running = False
        
        logger.info("Alert System initialized")
    
    async def start(self) -> None:
        """Start alert system"""
        if self.is_running:
            logger.warning("Alert System is already running")
            return
        
        self.is_running = True
        logger.info("Alert System started")
    
    async def stop(self) -> None:
        """Stop alert system"""
        self.is_running = False
        logger.info("Alert System stopped")
    
    def add_alert(self, alert: UnifiedAlert) -> str:
        """
        Add a new alert to the system
        
        Args:
            alert: Alert to add
            
        Returns:
            Alert ID
        """
        alert_id = alert.alert_id
        self.alerts[alert_id] = alert
        self.alert_history.append(alert)
        
        # Limit history size
        if len(self.alert_history) > self.max_history:
            self.alert_history = self.alert_history[-self.max_history:]
        
        # Log alert
        logger.warning(f"Alert {alert.priority.value.upper()}: {alert.message}")
        
        # Notify callbacks
        self._notify_callbacks(alert)
        
        # Apply escalation rules
        self._apply_escalation_rules(alert)
        
        # Send notifications
        self._send_notifications(alert)
        
        return alert_id
    
    def add_fleet_alert(self, alert: FleetAlert) -> str:
        """Add a fleet alert"""
        unified = UnifiedAlert.from_fleet_alert(alert)
        return self.add_alert(unified)
    
    def add_monitoring_alert(self, alert: MonitoringAlert) -> str:
        """Add a monitoring alert"""
        unified = UnifiedAlert.from_monitoring_alert(alert)
        return self.add_alert(unified)
    
    def add_geofence_alert(self, alert: GeofenceAlert) -> str:
        """Add a geofence alert"""
        unified = UnifiedAlert.from_geofence_alert(alert)
        return self.add_alert(unified)
    
    def add_telemetry_alert(self, alert: TelemetryAlert) -> str:
        """Add a telemetry alert"""
        unified = UnifiedAlert.from_telemetry_alert(alert)
        return self.add_alert(unified)
    
    def create_alert(self, alert_type: str, message: str, entity_id: str = "",
                     entity_type: str = "", category: AlertCategory = AlertCategory.OPERATIONAL,
                     priority: AlertPriority = AlertPriority.MEDIUM,
                     severity: str = "medium", metadata: Optional[Dict[str, Any]] = None,
                     source: str = "system") -> str:
        """
        Create a new alert
        
        Args:
            alert_type: Type of alert
            message: Alert message
            entity_id: ID of the entity
            entity_type: Type of entity
            category: Alert category
            priority: Alert priority
            severity: Severity level
            metadata: Additional metadata
            source: Source of the alert
            
        Returns:
            Alert ID
        """
        alert_id = str(uuid.uuid4())
        alert = UnifiedAlert(
            alert_id=alert_id,
            alert_type=alert_type,
            category=category,
            priority=priority,
            severity=severity,
            message=message,
            entity_id=entity_id,
            entity_type=entity_type,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
            source=source
        )
        return self.add_alert(alert)
    
    def _notify_callbacks(self, alert: UnifiedAlert) -> None:
        """Notify all relevant callbacks"""
        # Notify all callbacks
        for callback in self.callbacks.get("all", []):
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Callback error: {e}")
        
        # Notify priority-specific callbacks
        priority_callbacks = self.callbacks.get(alert.priority.value, [])
        for callback in priority_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Priority callback error: {e}")
    
    def _apply_escalation_rules(self, alert: UnifiedAlert) -> None:
        """Apply escalation rules to the alert"""
        for rule_id, rule in self.escalation_rules.items():
            if self._rule_matches(rule, alert):
                self._execute_escalation(rule, alert)
    
    def _rule_matches(self, rule: Dict[str, Any], alert: UnifiedAlert) -> bool:
        """Check if an alert matches an escalation rule"""
        # Check category
        if "category" in rule and rule["category"] != alert.category.value:
            return False
        
        # Check priority
        if "priority" in rule and rule["priority"] != alert.priority.value:
            return False
        
        # Check alert type
        if "alert_type" in rule and rule["alert_type"] != alert.alert_type:
            return False
        
        # Check entity type
        if "entity_type" in rule and rule["entity_type"] != alert.entity_type:
            return False
        
        # Check severity
        if "severity" in rule and rule["severity"] != alert.severity:
            return False
        
        return True
    
    def _execute_escalation(self, rule: Dict[str, Any], alert: UnifiedAlert) -> None:
        """Execute escalation actions for a rule"""
        actions = rule.get("actions", [])
        
        for action in actions:
            if action == "notify_admin":
                self._notify_admin(alert)
            elif action == "notify_technician":
                self._notify_technician(alert)
            elif action == "notify_pilot":
                self._notify_pilot(alert)
            elif action == "create_ticket":
                self._create_ticket(alert)
            elif action == "log_to_database":
                self._log_to_database(alert)
    
    def _notify_admin(self, alert: UnifiedAlert) -> None:
        """Notify administrator"""
        logger.info(f"Notifying admin about alert: {alert.alert_id}")
        # Implementation would send email/SMS/push notification
    
    def _notify_technician(self, alert: UnifiedAlert) -> None:
        """Notify technician"""
        logger.info(f"Notifying technician about alert: {alert.alert_id}")
    
    def _notify_pilot(self, alert: UnifiedAlert) -> None:
        """Notify pilot"""
        logger.info(f"Notifying pilot about alert: {alert.alert_id}")
    
    def _create_ticket(self, alert: UnifiedAlert) -> None:
        """Create a support ticket"""
        logger.info(f"Creating ticket for alert: {alert.alert_id}")
    
    def _log_to_database(self, alert: UnifiedAlert) -> None:
        """Log alert to database"""
        logger.info(f"Logging alert to database: {alert.alert_id}")
    
    def _send_notifications(self, alert: UnifiedAlert) -> None:
        """Send notifications through registered channels"""
        for channel_id, channel_func in self.notification_channels.items():
            try:
                channel_func(alert)
            except Exception as e:
                logger.error(f"Notification channel error {channel_id}: {e}")
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str) -> bool:
        """
        Acknowledge an alert
        
        Args:
            alert_id: Alert ID
            acknowledged_by: Who acknowledged the alert
            
        Returns:
            True if alert was acknowledged
        """
        alert = self.alerts.get(alert_id)
        if alert:
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            logger.info(f"Acknowledged alert {alert_id} by {acknowledged_by}")
            return True
        return False
    
    def acknowledge_all_alerts(self, acknowledged_by: str) -> int:
        """Acknowledge all unacknowledged alerts"""
        count = 0
        for alert_id, alert in self.alerts.items():
            if not alert.acknowledged:
                self.acknowledge_alert(alert_id, acknowledged_by)
                count += 1
        return count
    
    def resolve_alert(self, alert_id: str, resolved_by: str, resolution: str = "") -> bool:
        """
        Resolve an alert
        
        Args:
            alert_id: Alert ID
            resolved_by: Who resolved the alert
            resolution: Resolution notes
            
        Returns:
            True if alert was resolved
        """
        alert = self.alerts.get(alert_id)
        if alert:
            alert.acknowledged = True
            alert.acknowledged_by = resolved_by
            alert.acknowledged_at = datetime.utcnow()
            alert.metadata["resolution"] = resolution
            alert.metadata["resolved_at"] = datetime.utcnow().isoformat()
            logger.info(f"Resolved alert {alert_id} by {resolved_by}")
            return True
        return False
    
    def get_alert(self, alert_id: str) -> Optional[UnifiedAlert]:
        """Get an alert by ID"""
        return self.alerts.get(alert_id)
    
    def get_alerts(self, acknowledged: Optional[bool] = None,
                   priority: Optional[AlertPriority] = None,
                   category: Optional[AlertCategory] = None,
                   entity_id: Optional[str] = None,
                   entity_type: Optional[str] = None,
                   limit: int = 100) -> List[UnifiedAlert]:
        """
        Get alerts with optional filters
        
        Args:
            acknowledged: Filter by acknowledged status
            priority: Filter by priority
            category: Filter by category
            entity_id: Filter by entity ID
            entity_type: Filter by entity type
            limit: Maximum number of alerts to return
            
        Returns:
            List of matching alerts
        """
        result = []
        for alert in self.alerts.values():
            if acknowledged is not None and alert.acknowledged != acknowledged:
                continue
            if priority and alert.priority != priority:
                continue
            if category and alert.category != category:
                continue
            if entity_id and alert.entity_id != entity_id:
                continue
            if entity_type and alert.entity_type != entity_type:
                continue
            result.append(alert)
        
        # Sort by timestamp (newest first)
        result.sort(key=lambda x: x.timestamp, reverse=True)
        
        return result[:limit]
    
    def get_active_alerts(self) -> List[UnifiedAlert]:
        """Get all active (unacknowledged) alerts"""
        return self.get_alerts(acknowledged=False)
    
    def get_critical_alerts(self) -> List[UnifiedAlert]:
        """Get all critical alerts"""
        return self.get_alerts(priority=AlertPriority.CRITICAL)
    
    def get_alerts_by_entity(self, entity_id: str) -> List[UnifiedAlert]:
        """Get all alerts for a specific entity"""
        return self.get_alerts(entity_id=entity_id)
    
    def get_alert_history(self, limit: int = 100) -> List[UnifiedAlert]:
        """Get alert history"""
        return self.alert_history[-limit:]
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        total = len(self.alerts)
        unacknowledged = len([a for a in self.alerts.values() if not a.acknowledged])
        
        by_priority = {}
        for priority in AlertPriority:
            by_priority[priority.value] = len([
                a for a in self.alerts.values() if a.priority == priority
            ])
        
        by_category = {}
        for category in AlertCategory:
            by_category[category.value] = len([
                a for a in self.alerts.values() if a.category == category
            ])
        
        by_entity_type = {}
        for alert in self.alerts.values():
            if alert.entity_type:
                by_entity_type[alert.entity_type] = by_entity_type.get(alert.entity_type, 0) + 1
        
        return {
            "total": total,
            "unacknowledged": unacknowledged,
            "by_priority": by_priority,
            "by_category": by_category,
            "by_entity_type": by_entity_type
        }
    
    def add_callback(self, callback: Callable, priority: Optional[AlertPriority] = None) -> None:
        """
        Add a callback for alerts
        
        Args:
            callback: Callback function
            priority: Specific priority to listen to, or None for all
        """
        if priority:
            self.callbacks.setdefault(priority.value, []).append(callback)
        else:
            self.callbacks["all"].append(callback)
        logger.info("Added alert callback")
    
    def remove_callback(self, callback: Callable, priority: Optional[AlertPriority] = None) -> None:
        """Remove a callback"""
        if priority:
            if priority.value in self.callbacks and callback in self.callbacks[priority.value]:
                self.callbacks[priority.value].remove(callback)
        else:
            if "all" in self.callbacks and callback in self.callbacks["all"]:
                self.callbacks["all"].remove(callback)
        logger.info("Removed alert callback")
    
    def add_escalation_rule(self, rule_id: str, conditions: Dict[str, Any],
                            actions: List[str]) -> None:
        """
        Add an escalation rule
        
        Args:
            rule_id: Rule identifier
            conditions: Conditions for the rule to match
            actions: Actions to take when rule matches
        """
        self.escalation_rules[rule_id] = {
            "conditions": conditions,
            "actions": actions
        }
        logger.info(f"Added escalation rule {rule_id}")
    
    def remove_escalation_rule(self, rule_id: str) -> None:
        """Remove an escalation rule"""
        if rule_id in self.escalation_rules:
            del self.escalation_rules[rule_id]
            logger.info(f"Removed escalation rule {rule_id}")
    
    def add_notification_channel(self, channel_id: str, channel_func: Callable) -> None:
        """Add a notification channel"""
        self.notification_channels[channel_id] = channel_func
        logger.info(f"Added notification channel {channel_id}")
    
    def remove_notification_channel(self, channel_id: str) -> None:
        """Remove a notification channel"""
        if channel_id in self.notification_channels:
            del self.notification_channels[channel_id]
            logger.info(f"Removed notification channel {channel_id}")
    
    def clear_alerts(self, older_than_days: Optional[int] = None) -> int:
        """Clear old alerts"""
        if older_than_days:
            from datetime import timedelta
            cutoff = datetime.utcnow() - timedelta(days=older_than_days)
            to_delete = [
                alert_id for alert_id, alert in self.alerts.items()
                if alert.timestamp < cutoff
            ]
        else:
            to_delete = list(self.alerts.keys())
        
        for alert_id in to_delete:
            del self.alerts[alert_id]
        
        logger.info(f"Cleared {len(to_delete)} alerts")
        return len(to_delete)
    
    def clear_history(self) -> None:
        """Clear alert history"""
        self.alert_history.clear()
        logger.info("Cleared alert history")


# Import Enum for type hints
from enum import Enum


# Create global alert system instance
alert_system = AlertSystem()

"""
Vehicle Analysis Storage - KCo Fleet Intelligence
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
KCo by Cília | Laboratory of K and RockNewVenture

Cloud-based storage for vehicle analysis data with vehicle ID indexing.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VehicleAnalysisStorage:
    """
    Vehicle Analysis Storage Manager
    
    Manages storage and retrieval of vehicle analysis data in cloud database,
    indexed by vehicle ID for efficient querying and analysis tracking.
    """
    
    def __init__(self, cloud_client=None):
        """
        Initialize the storage manager
        
        Args:
            cloud_client: Cloud database client with async support
        """
        self.cloud_client = cloud_client
        self.collection_name = "vehicle_analyses"
    
    async def save_analysis(
        self, 
        vehicle_id: str, 
        analysis_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Save analysis data for a vehicle
        
        Args:
            vehicle_id: Vehicle ID (e.g., "BR-001", "MX-001")
            analysis_data: Analysis results from AI processing
            metadata: Optional additional metadata
            
        Returns:
            Result with document ID and status
        """
        try:
            if not self.cloud_client:
                return {
                    "status": "error",
                    "error": "No cloud client configured",
                    "vehicle_id": vehicle_id
                }
            
            # Prepare document
            document = {
                "vehicle_id": vehicle_id,
                "analysis_id": str(uuid.uuid4()),
                "analysis_data": analysis_data,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "vehicle_analysis",
                "metadata": metadata or {}
            }
            
            # Add indexing fields for efficient querying
            document["indexes"] = {
                "vehicle_id": vehicle_id,
                "analysis_type": analysis_data.get("analysis_type", "full"),
                "timestamp": document["timestamp"],
                "damage_score": analysis_data.get("damage_assessment", {}).get("damage_score", 0)
            }
            
            # Save to cloud database
            result = await self.cloud_client.insert(self.collection_name, document)
            
            logger.info(f"Analysis saved to cloud for vehicle: {vehicle_id}")
            
            return {
                "status": "success",
                "id": result.get("id"),
                "analysis_id": document["analysis_id"],
                "vehicle_id": vehicle_id,
                "timestamp": document["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error saving analysis for vehicle {vehicle_id}: {e}")
            return {
                "status": "error",
                "error": str(e),
                "vehicle_id": vehicle_id
            }
    
    async def get_analysis(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific analysis by analysis ID
        
        Args:
            analysis_id: The analysis document ID
            
        Returns:
            Analysis document or None if not found
        """
        try:
            if not self.cloud_client:
                return None
            
            result = await self.cloud_client.get(self.collection_name, analysis_id)
            
            if result:
                logger.info(f"Retrieved analysis: {analysis_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting analysis {analysis_id}: {e}")
            return None
    
    async def get_vehicle_history(
        self, 
        vehicle_id: str, 
        limit: int = 10,
        sort_by: str = "timestamp",
        descending: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Get all analyses for a specific vehicle
        
        Args:
            vehicle_id: Vehicle ID to query
            limit: Maximum number of results to return
            sort_by: Field to sort by (default: timestamp)
            descending: Sort order (default: True for newest first)
            
        Returns:
            List of analysis documents
        """
        try:
            if not self.cloud_client:
                return []
            
            query = {"vehicle_id": vehicle_id}
            
            results = await self.cloud_client.query(
                self.collection_name, 
                query, 
                limit=limit,
                sort_by=sort_by,
                descending=descending
            )
            
            logger.info(f"Retrieved {len(results)} analyses for vehicle: {vehicle_id}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting history for vehicle {vehicle_id}: {e}")
            return []
    
    async def get_analyses_by_date_range(
        self,
        start_date: str,
        end_date: str,
        vehicle_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get analyses within a date range
        
        Args:
            start_date: ISO format start date
            end_date: ISO format end date
            vehicle_id: Optional vehicle ID filter
            limit: Maximum number of results
            
        Returns:
            List of analysis documents
        """
        try:
            if not self.cloud_client:
                return []
            
            query = {
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            if vehicle_id:
                query["vehicle_id"] = vehicle_id
            
            results = await self.cloud_client.query(
                self.collection_name,
                query,
                limit=limit,
                sort_by="timestamp",
                descending=True
            )
            
            logger.info(f"Retrieved {len(results)} analyses for date range: {start_date} to {end_date}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting analyses by date range: {e}")
            return []
    
    async def update_analysis_metadata(
        self,
        analysis_id: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update metadata for an existing analysis
        
        Args:
            analysis_id: Analysis document ID
            metadata: Metadata to update
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.cloud_client:
                return False
            
            update_data = {
                "metadata": metadata,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = await self.cloud_client.update(
                self.collection_name,
                analysis_id,
                update_data
            )
            
            if result.get("status") == "success":
                logger.info(f"Updated metadata for analysis: {analysis_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error updating analysis metadata {analysis_id}: {e}")
            return False
    
    async def delete_analysis(self, analysis_id: str) -> bool:
        """
        Delete an analysis from cloud database
        
        Args:
            analysis_id: Analysis document ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.cloud_client:
                return False
            
            result = await self.cloud_client.delete(self.collection_name, analysis_id)
            
            if result.get("status") == "success":
                logger.info(f"Deleted analysis: {analysis_id}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting analysis {analysis_id}: {e}")
            return False
    
    async def get_statistics(self, vehicle_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get statistics for analyses
        
        Args:
            vehicle_id: Optional vehicle ID filter
            
        Returns:
            Statistics dictionary
        """
        try:
            if not self.cloud_client:
                return {}
            
            query = {}
            if vehicle_id:
                query["vehicle_id"] = vehicle_id
            
            # Get all analyses for statistics
            analyses = await self.cloud_client.query(
                self.collection_name,
                query,
                limit=1000
            )
            
            if not analyses:
                return {
                    "total_analyses": 0,
                    "vehicle_id": vehicle_id or "all"
                }
            
            # Calculate statistics
            total_analyses = len(analyses)
            
            damage_scores = []
            anomaly_counts = []
            analysis_types = {}
            
            for analysis in analyses:
                data = analysis.get("analysis_data", {})
                damage_assessment = data.get("damage_assessment", {})
                anomalies = data.get("anomalies", {})
                
                damage_score = damage_assessment.get("damage_score", 0)
                damage_scores.append(damage_score)
                
                anomaly_count = anomalies.get("total_anomalies", 0)
                anomaly_counts.append(anomaly_count)
                
                analysis_type = data.get("analysis_type", "unknown")
                analysis_types[analysis_type] = analysis_types.get(analysis_type, 0) + 1
            
            # Calculate averages
            avg_damage_score = sum(damage_scores) / len(damage_scores) if damage_scores else 0
            avg_anomalies = sum(anomaly_counts) / len(anomaly_counts) if anomaly_counts else 0
            
            # Find min/max
            min_damage_score = min(damage_scores) if damage_scores else 0
            max_damage_score = max(damage_scores) if damage_scores else 0
            
            return {
                "vehicle_id": vehicle_id or "all",
                "total_analyses": total_analyses,
                "statistics": {
                    "damage_score": {
                        "average": round(avg_damage_score, 2),
                        "min": round(min_damage_score, 2),
                        "max": round(max_damage_score, 2)
                    },
                    "anomalies": {
                        "average": round(avg_anomalies, 2),
                        "total": sum(anomaly_counts)
                    },
                    "analysis_types": analysis_types
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {}
    
    async def search_analyses(
        self,
        query: Dict[str, Any],
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Search analyses with custom query
        
        Args:
            query: MongoDB-style query dictionary
            limit: Maximum number of results
            
        Returns:
            List of matching analysis documents
        """
        try:
            if not self.cloud_client:
                return []
            
            results = await self.cloud_client.query(
                self.collection_name,
                query,
                limit=limit
            )
            
            logger.info(f"Search returned {len(results)} results")
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching analyses: {e}")
            return []
    
    def get_cloud_client(self):
        """Get the cloud client instance"""
        return self.cloud_client
    
    def set_cloud_client(self, cloud_client):
        """Set the cloud client instance"""
        self.cloud_client = cloud_client

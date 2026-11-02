"""
Cloud Database Client - Firebase/Firestore/Supabase Client
KCo Fleet Intelligence Platform - Old But Gold TR8 IVSTO

Supports multiple cloud database providers:
- Firebase Firestore
- Supabase
- AWS DynamoDB
- MongoDB Atlas
"""

import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import uuid
import json
import logging
from abc import ABC, abstractmethod

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class CloudDatabaseClient(ABC):
    """Abstract base class for cloud database clients"""
    
    @abstractmethod
    async def connect(self):
        """Connect to the database"""
        pass
    
    @abstractmethod
    async def disconnect(self):
        """Disconnect from the database"""
        pass
    
    @abstractmethod
    async def insert(self, collection: str, data: Dict[str, Any]) -> str:
        """Insert document into collection"""
        pass
    
    @abstractmethod
    async def update(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Update document in collection"""
        pass
    
    @abstractmethod
    async def get(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document from collection"""
        pass
    
    @abstractmethod
    async def query(self, collection: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query documents from collection"""
        pass
    
    @abstractmethod
    async def delete(self, collection: str, doc_id: str) -> bool:
        """Delete document from collection"""
        pass


class FirebaseClient(CloudDatabaseClient):
    """Firebase Firestore client"""
    
    def __init__(self):
        self.initialized = False
        self.db = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Firebase"""
        try:
            import firebase_admin
            from firebase_admin import credentials, firestore
            
            # Check if already initialized
            if not firebase_admin._apps:
                # Load credentials from environment or file
                cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
                if cred_path and os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                else:
                    # Try to load from environment variables
                    cred_data = os.getenv("FIREBASE_CREDENTIALS")
                    if cred_data:
                        cred = credentials.Certificate(json.loads(cred_data))
                    else:
                        logger.warning("Firebase credentials not found")
                        return
                
                firebase_admin.initialize_app(cred)
            
            self.db = firestore.client()
            self.initialized = True
            logger.info("Firebase initialized successfully")
            
        except ImportError:
            logger.warning("Firebase not installed. Install with: pip install firebase-admin")
            self.initialized = False
        except Exception as e:
            logger.error(f"Error initializing Firebase: {e}")
            self.initialized = False
    
    async def connect(self):
        """Connect to Firebase"""
        if not self.initialized:
            self._initialize()
        return self.initialized
    
    async def disconnect(self):
        """Disconnect from Firebase"""
        # Firebase doesn't have explicit disconnect
        self.initialized = False
    
    async def insert(self, collection: str, data: Dict[str, Any]) -> str:
        """Insert document into Firebase collection"""
        if not self.initialized or not self.db:
            raise Exception("Firebase not initialized")
        
        try:
            # Add timestamp
            data["created_at"] = datetime.utcnow().isoformat()
            data["updated_at"] = datetime.utcnow().isoformat()
            
            # Generate ID if not provided
            if "id" not in data:
                data["id"] = str(uuid.uuid4())
            
            # Insert into Firestore
            doc_ref = self.db.collection(collection).document(data["id"])
            doc_ref.set(data)
            
            return data["id"]
            
        except Exception as e:
            logger.error(f"Error inserting into Firebase: {e}")
            raise
    
    async def update(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Update document in Firebase collection"""
        if not self.initialized or not self.db:
            raise Exception("Firebase not initialized")
        
        try:
            data["updated_at"] = datetime.utcnow().isoformat()
            
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.update(data)
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating Firebase document: {e}")
            return False
    
    async def get(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document from Firebase collection"""
        if not self.initialized or not self.db:
            raise Exception("Firebase not initialized")
        
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc = doc_ref.get()
            
            if doc.exists:
                return doc.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Error getting Firebase document: {e}")
            return None
    
    async def query(self, collection: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query documents from Firebase collection"""
        if not self.initialized or not self.db:
            raise Exception("Firebase not initialized")
        
        try:
            query = self.db.collection(collection)
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    query = query.where(field, "==", value)
            
            # Get all documents
            docs = query.stream()
            results = [doc.to_dict() for doc in docs]
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying Firebase: {e}")
            return []
    
    async def delete(self, collection: str, doc_id: str) -> bool:
        """Delete document from Firebase collection"""
        if not self.initialized or not self.db:
            raise Exception("Firebase not initialized")
        
        try:
            doc_ref = self.db.collection(collection).document(doc_id)
            doc_ref.delete()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting Firebase document: {e}")
            return False


class SupabaseClient(CloudDatabaseClient):
    """Supabase client"""
    
    def __init__(self):
        self.initialized = False
        self.client = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Supabase"""
        try:
            from supabase import create_client, Client
            
            url = os.getenv("SUPABASE_URL", settings.SUPABASE_URL)
            key = os.getenv("SUPABASE_KEY", settings.SUPABASE_KEY)
            
            if url and key:
                self.client = create_client(url, key)
                self.initialized = True
                logger.info("Supabase initialized successfully")
            else:
                logger.warning("Supabase URL or key not found")
                self.initialized = False
                
        except ImportError:
            logger.warning("Supabase not installed. Install with: pip install supabase")
            self.initialized = False
        except Exception as e:
            logger.error(f"Error initializing Supabase: {e}")
            self.initialized = False
    
    async def connect(self):
        """Connect to Supabase"""
        if not self.initialized:
            self._initialize()
        return self.initialized
    
    async def disconnect(self):
        """Disconnect from Supabase"""
        self.initialized = False
        self.client = None
    
    async def insert(self, collection: str, data: Dict[str, Any]) -> str:
        """Insert document into Supabase table"""
        if not self.initialized or not self.client:
            raise Exception("Supabase not initialized")
        
        try:
            data["created_at"] = datetime.utcnow().isoformat()
            data["updated_at"] = datetime.utcnow().isoformat()
            
            if "id" not in data:
                data["id"] = str(uuid.uuid4())
            
            response = self.client.table(collection).insert(data).execute()
            
            if response.data:
                return response.data[0]["id"]
            
            raise Exception("Failed to insert document")
            
        except Exception as e:
            logger.error(f"Error inserting into Supabase: {e}")
            raise
    
    async def update(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Update document in Supabase table"""
        if not self.initialized or not self.client:
            raise Exception("Supabase not initialized")
        
        try:
            data["updated_at"] = datetime.utcnow().isoformat()
            
            response = self.client.table(collection).update(data).eq("id", doc_id).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error updating Supabase document: {e}")
            return False
    
    async def get(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document from Supabase table"""
        if not self.initialized or not self.client:
            raise Exception("Supabase not initialized")
        
        try:
            response = self.client.table(collection).select("*").eq("id", doc_id).single().execute()
            
            if response.data:
                return response.data
            return None
            
        except Exception as e:
            logger.error(f"Error getting Supabase document: {e}")
            return None
    
    async def query(self, collection: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query documents from Supabase table"""
        if not self.initialized or not self.client:
            raise Exception("Supabase not initialized")
        
        try:
            query = self.client.table(collection).select("*")
            
            if filters:
                for field, value in filters.items():
                    query = query.eq(field, value)
            
            response = query.execute()
            
            if response.data:
                return response.data
            return []
            
        except Exception as e:
            logger.error(f"Error querying Supabase: {e}")
            return []
    
    async def delete(self, collection: str, doc_id: str) -> bool:
        """Delete document from Supabase table"""
        if not self.initialized or not self.client:
            raise Exception("Supabase not initialized")
        
        try:
            response = self.client.table(collection).delete().eq("id", doc_id).execute()
            
            return len(response.data) > 0
            
        except Exception as e:
            logger.error(f"Error deleting Supabase document: {e}")
            return False


class MongoDBClient(CloudDatabaseClient):
    """MongoDB Atlas client"""
    
    def __init__(self):
        self.initialized = False
        self.client = None
        self.db = None
        self._initialize()
    
    def _initialize(self):
        """Initialize MongoDB"""
        try:
            from pymongo import MongoClient
            
            connection_string = os.getenv("MONGODB_URI", settings.MONGODB_URI)
            database_name = os.getenv("MONGODB_NAME", "kco_ml")
            
            if connection_string:
                self.client = MongoClient(connection_string)
                self.db = self.client[database_name]
                self.initialized = True
                logger.info("MongoDB initialized successfully")
            else:
                logger.warning("MongoDB connection string not found")
                self.initialized = False
                
        except ImportError:
            logger.warning("PyMongo not installed. Install with: pip install pymongo")
            self.initialized = False
        except Exception as e:
            logger.error(f"Error initializing MongoDB: {e}")
            self.initialized = False
    
    async def connect(self):
        """Connect to MongoDB"""
        if not self.initialized:
            self._initialize()
        return self.initialized
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
        self.initialized = False
        self.client = None
        self.db = None
    
    async def insert(self, collection: str, data: Dict[str, Any]) -> str:
        """Insert document into MongoDB collection"""
        if not self.initialized or not self.db:
            raise Exception("MongoDB not initialized")
        
        try:
            data["created_at"] = datetime.utcnow()
            data["updated_at"] = datetime.utcnow()
            
            if "id" not in data:
                data["id"] = str(uuid.uuid4())
            
            result = self.db[collection].insert_one(data)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error inserting into MongoDB: {e}")
            raise
    
    async def update(self, collection: str, doc_id: str, data: Dict[str, Any]) -> bool:
        """Update document in MongoDB collection"""
        if not self.initialized or not self.db:
            raise Exception("MongoDB not initialized")
        
        try:
            data["updated_at"] = datetime.utcnow()
            
            result = self.db[collection].update_one(
                {"id": doc_id},
                {"$set": data}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error updating MongoDB document: {e}")
            return False
    
    async def get(self, collection: str, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document from MongoDB collection"""
        if not self.initialized or not self.db:
            raise Exception("MongoDB not initialized")
        
        try:
            result = self.db[collection].find_one({"id": doc_id})
            
            if result:
                # Convert ObjectId to string
                result["_id"] = str(result["_id"])
                return result
            return None
            
        except Exception as e:
            logger.error(f"Error getting MongoDB document: {e}")
            return None
    
    async def query(self, collection: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query documents from MongoDB collection"""
        if not self.initialized or not self.db:
            raise Exception("MongoDB not initialized")
        
        try:
            query = {}
            if filters:
                query = filters
            
            results = list(self.db[collection].find(query))
            
            # Convert ObjectId to string
            for result in results:
                result["_id"] = str(result["_id"])
            
            return results
            
        except Exception as e:
            logger.error(f"Error querying MongoDB: {e}")
            return []
    
    async def delete(self, collection: str, doc_id: str) -> bool:
        """Delete document from MongoDB collection"""
        if not self.initialized or not self.db:
            raise Exception("MongoDB not initialized")
        
        try:
            result = self.db[collection].delete_one({"id": doc_id})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting MongoDB document: {e}")
            return False


# Factory function
def get_cloud_database_client(provider: str = "firebase") -> CloudDatabaseClient:
    """Get cloud database client based on provider"""
    provider = provider.lower()
    
    if provider == "firebase":
        return FirebaseClient()
    elif provider == "supabase":
        return SupabaseClient()
    elif provider == "mongodb":
        return MongoDBClient()
    else:
        # Default to Firebase
        return FirebaseClient()


# Singleton instances
firebase_client = FirebaseClient()
supabase_client = SupabaseClient()
mongodb_client = MongoDBClient()

# Default client (can be configured via environment)
default_client = get_cloud_database_client(os.getenv("CLOUD_PROVIDER", "firebase"))

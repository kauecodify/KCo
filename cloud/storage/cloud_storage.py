"""
Cloud Storage Client - Firebase Storage / AWS S3 / Supabase Storage
KCo Fleet Intelligence Platform - Old But Gold TR8 IVSTO
"""

import os
import uuid
from typing import Dict, Any, Optional, Union, BinaryIO
from datetime import datetime
import logging
from abc import ABC, abstractmethod

from backend.config.settings import settings

logger = logging.getLogger(__name__)


class CloudStorageClient(ABC):
    """Abstract base class for cloud storage clients"""
    
    @abstractmethod
    async def upload_file(
        self,
        file: Union[BinaryIO, bytes, str],
        path: str,
        content_type: Optional[str] = None
    ) -> str:
        """Upload file to cloud storage"""
        pass
    
    @abstractmethod
    async def download_file(self, path: str) -> bytes:
        """Download file from cloud storage"""
        pass
    
    @abstractmethod
    async def delete_file(self, path: str) -> bool:
        """Delete file from cloud storage"""
        pass
    
    @abstractmethod
    async def get_file_url(self, path: str) -> str:
        """Get public URL for file"""
        pass
    
    @abstractmethod
    async def list_files(self, prefix: str = "") -> list:
        """List files in storage"""
        pass


class FirebaseStorageClient(CloudStorageClient):
    """Firebase Storage client"""
    
    def __init__(self):
        self.initialized = False
        self.bucket = None
        self._initialize()
    
    def _initialize(self):
        """Initialize Firebase Storage"""
        try:
            import firebase_admin
            from firebase_admin import storage
            
            # Firebase should be initialized in the database client
            if firebase_admin._apps:
                self.bucket = storage.bucket()
                self.initialized = True
                logger.info("Firebase Storage initialized successfully")
            else:
                logger.warning("Firebase not initialized. Initialize Firebase first.")
                self.initialized = False
                
        except ImportError:
            logger.warning("Firebase not installed. Install with: pip install firebase-admin")
            self.initialized = False
        except Exception as e:
            logger.error(f"Error initializing Firebase Storage: {e}")
            self.initialized = False
    
    async def upload_file(
        self,
        file: Union[BinaryIO, bytes, str],
        path: str,
        content_type: Optional[str] = None
    ) -> str:
        """Upload file to Firebase Storage"""
        if not self.initialized or not self.bucket:
            raise Exception("Firebase Storage not initialized")
        
        try:
            # Generate unique filename if not provided
            if not path or path == "/":
                path = f"uploads/{uuid.uuid4().hex}"
            
            blob = self.bucket.blob(path)
            
            # Upload file
            if isinstance(file, str):
                # File path
                blob.upload_from_filename(file, content_type=content_type)
            elif isinstance(file, bytes):
                # Bytes
                blob.upload_from_string(file, content_type=content_type)
            else:
                # File-like object
                blob.upload_from_file(file, content_type=content_type)
            
            # Make public
            blob.make_public()
            
            return path
            
        except Exception as e:
            logger.error(f"Error uploading to Firebase Storage: {e}")
            raise
    
    async def download_file(self, path: str) -> bytes:
        """Download file from Firebase Storage"""
        if not self.initialized or not self.bucket:
            raise Exception("Firebase Storage not initialized")
        
        try:
            blob = self.bucket.blob(path)
            return blob.download_as_bytes()
            
        except Exception as e:
            logger.error(f"Error downloading from Firebase Storage: {e}")
            raise
    
    async def delete_file(self, path: str) -> bool:
        """Delete file from Firebase Storage"""
        if not self.initialized or not self.bucket:
            raise Exception("Firebase Storage not initialized")
        
        try:
            blob = self.bucket.blob(path)
            blob.delete()
            return True
            
        except Exception as e:
            logger.error(f"Error deleting from Firebase Storage: {e}")
            return False
    
    async def get_file_url(self, path: str) -> str:
        """Get public URL for file"""
        if not self.initialized or not self.bucket:
            raise Exception("Firebase Storage not initialized")
        
        try:
            blob = self.bucket.blob(path)
            return blob.public_url
            
        except Exception as e:
            logger.error(f"Error getting Firebase Storage URL: {e}")
            raise
    
    async def list_files(self, prefix: str = "") -> list:
        """List files in Firebase Storage"""
        if not self.initialized or not self.bucket:
            raise Exception("Firebase Storage not initialized")
        
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
            
        except Exception as e:
            logger.error(f"Error listing Firebase Storage files: {e}")
            return []


class S3StorageClient(CloudStorageClient):
    """AWS S3 Storage client"""
    
    def __init__(self):
        self.initialized = False
        self.client = None
        self.bucket_name = None
        self._initialize()
    
    def _initialize(self):
        """Initialize AWS S3"""
        try:
            import boto3
            from botocore.exceptions import NoCredentialsError
            
            aws_access_key = os.getenv("AWS_ACCESS_KEY_ID", settings.AWS_ACCESS_KEY_ID)
            aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY", settings.AWS_SECRET_ACCESS_KEY)
            aws_region = os.getenv("AWS_REGION", settings.AWS_REGION)
            self.bucket_name = os.getenv("AWS_S3_BUCKET", settings.AWS_S3_BUCKET)
            
            if aws_access_key and aws_secret_key and self.bucket_name:
                self.client = boto3.client(
                    's3',
                    aws_access_key_id=aws_access_key,
                    aws_secret_access_key=aws_secret_key,
                    region_name=aws_region
                )
                self.initialized = True
                logger.info("AWS S3 Storage initialized successfully")
            else:
                logger.warning("AWS credentials or bucket name not found")
                self.initialized = False
                
        except ImportError:
            logger.warning("Boto3 not installed. Install with: pip install boto3")
            self.initialized = False
        except Exception as e:
            logger.error(f"Error initializing AWS S3: {e}")
            self.initialized = False
    
    async def upload_file(
        self,
        file: Union[BinaryIO, bytes, str],
        path: str,
        content_type: Optional[str] = None
    ) -> str:
        """Upload file to AWS S3"""
        if not self.initialized or not self.client or not self.bucket_name:
            raise Exception("AWS S3 not initialized")
        
        try:
            # Generate unique key if not provided
            if not path or path == "/":
                path = f"uploads/{uuid.uuid4().hex}"
            
            # Upload file
            if isinstance(file, str):
                # File path
                self.client.upload_file(file, self.bucket_name, path)
            elif isinstance(file, bytes):
                # Bytes
                self.client.put_object(
                    Bucket=self.bucket_name,
                    Key=path,
                    Body=file,
                    ContentType=content_type
                )
            else:
                # File-like object
                self.client.upload_fileobj(file, self.bucket_name, path)
            
            return path
            
        except Exception as e:
            logger.error(f"Error uploading to AWS S3: {e}")
            raise
    
    async def download_file(self, path: str) -> bytes:
        """Download file from AWS S3"""
        if not self.initialized or not self.client or not self.bucket_name:
            raise Exception("AWS S3 not initialized")
        
        try:
            response = self.client.get_object(Bucket=self.bucket_name, Key=path)
            return response['Body'].read()
            
        except Exception as e:
            logger.error(f"Error downloading from AWS S3: {e}")
            raise
    
    async def delete_file(self, path: str) -> bool:
        """Delete file from AWS S3"""
        if not self.initialized or not self.client or not self.bucket_name:
            raise Exception("AWS S3 not initialized")
        
        try:
            self.client.delete_object(Bucket=self.bucket_name, Key=path)
            return True
            
        except Exception as e:
            logger.error(f"Error deleting from AWS S3: {e}")
            return False
    
    async def get_file_url(self, path: str) -> str:
        """Get public URL for file"""
        if not self.initialized or not self.client or not self.bucket_name:
            raise Exception("AWS S3 not initialized")
        
        try:
            # Generate presigned URL
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': path},
                ExpiresIn=3600  # 1 hour
            )
            return url
            
        except Exception as e:
            logger.error(f"Error getting AWS S3 URL: {e}")
            raise
    
    async def list_files(self, prefix: str = "") -> list:
        """List files in AWS S3"""
        if not self.initialized or not self.client or not self.bucket_name:
            raise Exception("AWS S3 not initialized")
        
        try:
            response = self.client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append(obj['Key'])
            
            return files
            
        except Exception as e:
            logger.error(f"Error listing AWS S3 files: {e}")
            return []


class SupabaseStorageClient(CloudStorageClient):
    """Supabase Storage client"""
    
    def __init__(self):
        self.initialized = False
        self.client = None
        self.bucket_name = "kco-images"
        self._initialize()
    
    def _initialize(self):
        """Initialize Supabase Storage"""
        try:
            from supabase import create_client, Client
            
            url = os.getenv("SUPABASE_URL", settings.SUPABASE_URL)
            key = os.getenv("SUPABASE_KEY", settings.SUPABASE_KEY)
            
            if url and key:
                self.client = create_client(url, key)
                self.initialized = True
                logger.info("Supabase Storage initialized successfully")
            else:
                logger.warning("Supabase URL or key not found")
                self.initialized = False
                
        except ImportError:
            logger.warning("Supabase not installed. Install with: pip install supabase")
            self.initialized = False
        except Exception as e:
            logger.error(f"Error initializing Supabase Storage: {e}")
            self.initialized = False
    
    async def upload_file(
        self,
        file: Union[BinaryIO, bytes, str],
        path: str,
        content_type: Optional[str] = None
    ) -> str:
        """Upload file to Supabase Storage"""
        if not self.initialized or not self.client:
            raise Exception("Supabase Storage not initialized")
        
        try:
            # Generate unique path if not provided
            if not path or path == "/":
                path = f"uploads/{uuid.uuid4().hex}"
            
            # Upload file
            if isinstance(file, str):
                # File path
                with open(file, 'rb') as f:
                    data = self.client.storage.from_(self.bucket_name).upload(
                        path=path,
                        file=f,
                        file_options={"content-type": content_type}
                    )
            elif isinstance(file, bytes):
                # Bytes
                import io
                data = self.client.storage.from_(self.bucket_name).upload(
                    path=path,
                    file=io.BytesIO(file),
                    file_options={"content-type": content_type}
                )
            else:
                # File-like object
                data = self.client.storage.from_(self.bucket_name).upload(
                    path=path,
                    file=file,
                    file_options={"content-type": content_type}
                )
            
            return path
            
        except Exception as e:
            logger.error(f"Error uploading to Supabase Storage: {e}")
            raise
    
    async def download_file(self, path: str) -> bytes:
        """Download file from Supabase Storage"""
        if not self.initialized or not self.client:
            raise Exception("Supabase Storage not initialized")
        
        try:
            response = self.client.storage.from_(self.bucket_name).download(path)
            return response
            
        except Exception as e:
            logger.error(f"Error downloading from Supabase Storage: {e}")
            raise
    
    async def delete_file(self, path: str) -> bool:
        """Delete file from Supabase Storage"""
        if not self.initialized or not self.client:
            raise Exception("Supabase Storage not initialized")
        
        try:
            self.client.storage.from_(self.bucket_name).remove([path])
            return True
            
        except Exception as e:
            logger.error(f"Error deleting from Supabase Storage: {e}")
            return False
    
    async def get_file_url(self, path: str) -> str:
        """Get public URL for file"""
        if not self.initialized or not self.client:
            raise Exception("Supabase Storage not initialized")
        
        try:
            # Get public URL
            url = self.client.storage.from_(self.bucket_name).get_public_url(path)
            return url
            
        except Exception as e:
            logger.error(f"Error getting Supabase Storage URL: {e}")
            raise
    
    async def list_files(self, prefix: str = "") -> list:
        """List files in Supabase Storage"""
        if not self.initialized or not self.client:
            raise Exception("Supabase Storage not initialized")
        
        try:
            response = self.client.storage.from_(self.bucket_name).list(path=prefix)
            files = []
            for item in response:
                if item.metadata and 'name' in item.metadata:
                    files.append(item.metadata['name'])
            return files
            
        except Exception as e:
            logger.error(f"Error listing Supabase Storage files: {e}")
            return []


# Factory function
def get_cloud_storage_client(provider: str = "firebase") -> CloudStorageClient:
    """Get cloud storage client based on provider"""
    provider = provider.lower()
    
    if provider == "firebase":
        return FirebaseStorageClient()
    elif provider == "s3" or provider == "aws":
        return S3StorageClient()
    elif provider == "supabase":
        return SupabaseStorageClient()
    else:
        # Default to Firebase
        return FirebaseStorageClient()


# Singleton instances
firebase_storage = FirebaseStorageClient()
s3_storage = S3StorageClient()
supabase_storage = SupabaseStorageClient()

# Default storage client
default_storage = get_cloud_storage_client(os.getenv("CLOUD_STORAGE_PROVIDER", "firebase"))

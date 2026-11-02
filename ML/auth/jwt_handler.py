"""
JWT Authentication Handler for KCo
Old But Gold TR8 IVSTO
"""

import jwt
import datetime
import hashlib
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
import secrets

from backend.config.settings import settings


@dataclass
class TokenData:
    """Token data structure"""
    user_id: str
    email: str
    role: str
    country: str
    exp: datetime.datetime
    iat: datetime.datetime


class JWTHandler:
    """JWT Token Management"""
    
    def __init__(self, secret_key: Optional[str] = None, expire_hours: int = 24):
        self.secret_key = secret_key or settings.JWT_SECRET or settings.SECRET_KEY
        self.expire_hours = expire_hours or settings.JWT_EXPIRE_HOURS
        self.algorithm = "HS256"
    
    def _generate_secret(self) -> str:
        """Generate a secure secret key if not provided"""
        return secrets.token_urlsafe(64)
    
    def create_access_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT access token"""
        if not self.secret_key:
            self.secret_key = self._generate_secret()
        
        # Extract user data
        user_id = user_data.get("id", user_data.get("user_id"))
        email = user_data.get("email")
        role = user_data.get("role", "user")
        country = user_data.get("country", "br")
        
        # Create token payload
        payload = {
            "sub": str(user_id),
            "email": email,
            "role": role,
            "country": country,
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=self.expire_hours),
            "iss": "KCo-Auth",
            "aud": "KCo-API"
        }
        
        # Add custom claims
        if "company_id" in user_data:
            payload["company_id"] = user_data["company_id"]
        if "company_name" in user_data:
            payload["company_name"] = user_data["company_name"]
        
        # Generate token
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        return token
    
    def create_refresh_token(self, user_data: Dict[str, Any]) -> str:
        """Create JWT refresh token with longer expiration"""
        if not self.secret_key:
            self.secret_key = self._generate_secret()
        
        user_id = user_data.get("id", user_data.get("user_id"))
        
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "iat": datetime.datetime.utcnow(),
            "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
            "iss": "KCo-Auth",
            "aud": "KCo-Refresh"
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        return token
    
    def decode_token(self, token: str) -> Optional[TokenData]:
        """Decode and validate JWT token"""
        try:
            if not self.secret_key:
                self.secret_key = settings.SECRET_KEY
            
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            return TokenData(
                user_id=payload.get("sub"),
                email=payload.get("email", ""),
                role=payload.get("role", "user"),
                country=payload.get("country", "br"),
                exp=datetime.datetime.fromtimestamp(payload.get("exp")),
                iat=datetime.datetime.fromtimestamp(payload.get("iat"))
            )
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
        except Exception as e:
            print(f"Error decoding token: {e}")
            return None
    
    def verify_token(self, token: str) -> Tuple[bool, Optional[TokenData]]:
        """Verify token and return token data"""
        token_data = self.decode_token(token)
        
        if token_data is None:
            return False, None
        
        # Check if token is expired
        if token_data.exp < datetime.datetime.utcnow():
            return False, None
        
        return True, token_data
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA256 with salt"""
        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{hashed}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hashed password"""
        try:
            salt, hashed = hashed_password.split(":")
            new_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return new_hash == hashed
        except:
            return False
    
    def generate_api_key(self, user_id: str) -> str:
        """Generate API key for user"""
        timestamp = datetime.datetime.utcnow().timestamp()
        random_str = secrets.token_hex(32)
        api_key = hashlib.sha256(f"{user_id}:{timestamp}:{random_str}".encode()).hexdigest()
        return api_key
    
    def validate_api_key(self, api_key: str, stored_key: str) -> bool:
        """Validate API key"""
        return api_key == stored_key


# Singleton instance
jwt_handler = JWTHandler()

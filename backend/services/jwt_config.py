"""
JWT Configuration - KCo Fleet Intelligence
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
KCo by Cília | Laboratory of K and RockNewVenture

Centralized JWT configuration for authentication system.
"""

from datetime import timedelta
from typing import Dict, Any, Optional
import os


class JWTConfig:
    """
    JWT Configuration Manager
    
    Centralizes JWT settings for the authentication system.
    """
    
    def __init__(self):
        """Initialize JWT configuration from environment variables"""
        self.SECRET_KEY = os.getenv("JWT_SECRET", "kco-old-but-gold-tr8-ivsto-2024-cilia-lab")
        self.ALGORITHM = "HS256"
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_EXPIRE_MINUTES", "60"))
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_EXPIRE_DAYS", "7"))
        
        # Token types
        self.TOKEN_TYPE_ACCESS = "access"
        self.TOKEN_TYPE_REFRESH = "refresh"
        
        # KCo specific claims
        self.CLAIM_VEHICLE_ID = "vehicle_id"
        self.CLAIM_COMPANY = "company"
        self.CLAIM_COUNTRY = "country"
        self.CLAIM_ROLE = "role"
        self.CLAIM_PERMISSIONS = "permissions"
    
    def get_access_token_expiry(self) -> timedelta:
        """Get access token expiry duration"""
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    def get_refresh_token_expiry(self) -> timedelta:
        """Get refresh token expiry duration"""
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
    
    def get_kco_claims(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get KCo-specific JWT claims
        
        Args:
            user_data: User data dictionary
            
        Returns:
            Dictionary with KCo-specific claims
        """
        from backend.models.auth import ROLES, get_user_permissions
        
        claims = {
            self.CLAIM_COUNTRY: user_data.get("country", "br"),
            self.CLAIM_ROLE: user_data.get("role", "user"),
            self.CLAIM_COMPANY: user_data.get("company", "KCo"),
            self.CLAIM_VEHICLE_ID: user_data.get("vehicle_id", ""),
            self.CLAIM_PERMISSIONS: get_user_permissions(user_data.get("role", "user"))
        }
        
        return claims
    
    def create_token_payload(
        self,
        user_data: Dict[str, Any],
        token_type: str = "access"
    ) -> Dict[str, Any]:
        """
        Create JWT payload with KCo-specific claims
        
        Args:
            user_data: User data dictionary
            token_type: Type of token (access or refresh)
            
        Returns:
            Dictionary with JWT payload
        """
        import uuid
        from datetime import datetime, timezone
        
        now = datetime.now(timezone.utc)
        
        payload = {
            "sub": user_data.get("id", str(uuid.uuid4())),
            "email": user_data.get("email", ""),
            "name": user_data.get("name", ""),
            "iat": now,
            "jti": str(uuid.uuid4()),
            "token_type": token_type,
            "iss": "KCo by Cília",
            "aud": "KCo Fleet Intelligence"
        }
        
        # Add KCo-specific claims
        kco_claims = self.get_kco_claims(user_data)
        payload.update(kco_claims)
        
        # Set expiration based on token type
        if token_type == self.TOKEN_TYPE_ACCESS:
            payload["exp"] = now + self.get_access_token_expiry()
        else:
            payload["exp"] = now + self.get_refresh_token_expiry()
        
        return payload
    
    def get_token_headers(self) -> Dict[str, str]:
        """Get JWT headers"""
        return {
            "typ": "JWT",
            "alg": self.ALGORITHM,
            "iss": "KCo by Cília"
        }


# Singleton instance
jwt_config = JWTConfig()


def get_jwt_config() -> JWTConfig:
    """Get JWT configuration instance"""
    return jwt_config

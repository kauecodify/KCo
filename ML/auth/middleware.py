"""
Authentication Middleware for FastAPI
KCo Fleet Intelligence Platform
"""

from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
import logging

from backend.config.settings import settings
from ML.auth.jwt_handler import jwt_handler, TokenData

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()


class AuthMiddleware:
    """Authentication middleware for FastAPI"""
    
    def __init__(self):
        self.jwt_handler = jwt_handler
    
    async def verify_token(
        self,
        credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
    ) -> TokenData:
        """Verify JWT token and return token data"""
        if credentials is None:
            raise HTTPException(
                status_code=401,
                detail="Nao autorizado. Token ausente.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        token = credentials.credentials
        
        # Verify token
        is_valid, token_data = self.jwt_handler.verify_token(token)
        
        if not is_valid or token_data is None:
            raise HTTPException(
                status_code=401,
                detail="Token invalido ou expirado.",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return token_data
    
    async def get_current_user(
        self,
        token_data: TokenData = Depends(verify_token)
    ) -> Dict[str, Any]:
        """Get current user from token"""
        return {
            "user_id": token_data.user_id,
            "email": token_data.email,
            "role": token_data.role,
            "country": token_data.country
        }
    
    async def check_permission(
        self,
        required_roles: list,
        token_data: TokenData = Depends(verify_token)
    ) -> TokenData:
        """Check if user has required permissions"""
        if token_data.role not in required_roles:
            raise HTTPException(
                status_code=403,
                detail="Permissao negada. Role insuficiente."
            )
        return token_data
    
    async def check_country(
        self,
        required_countries: list,
        token_data: TokenData = Depends(verify_token)
    ) -> TokenData:
        """Check if user has access to required countries"""
        if token_data.country not in required_countries:
            raise HTTPException(
                status_code=403,
                detail="Acesso negado para este pais."
            )
        return token_data


# Dependency injection
def get_auth_middleware() -> AuthMiddleware:
    """Get auth middleware instance"""
    return AuthMiddleware()


# Shortcut dependencies
async def verify_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> TokenData:
    """Verify JWT token"""
    auth = AuthMiddleware()
    return await auth.verify_token(credentials)


async def get_current_user(
    token_data: TokenData = Depends(verify_token)
) -> Dict[str, Any]:
    """Get current user"""
    auth = AuthMiddleware()
    return await auth.get_current_user(token_data)


async def require_role(roles: list = ["admin"]):
    """Require specific role"""
    auth = AuthMiddleware()
    return await auth.check_permission(roles)


async def require_country(countries: list = ["br", "mx"]):
    """Require specific country"""
    auth = AuthMiddleware()
    return await auth.check_country(countries)


# FastAPI dependency for easy use
from fastapi import Depends as FastAPIDepends

get_current_user_dep = FastAPIDepends(get_current_user)
verify_token_dep = FastAPIDepends(verify_token)

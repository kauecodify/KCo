"""
KCo/ARG Backend - Seguranca e Autenticacao
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from backend.config import settings
import logging

logger = logging.getLogger(__name__)

# Configuracao de hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], default="pbkdf2_sha256")

# Configuracao de JWT
oauth2_scheme = HTTPBearer()


class Token(BaseModel):
    """Modelo de token JWT"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    refresh_token: Optional[str] = None


class TokenData(BaseModel):
    """Dados do token"""
    email: Optional[str] = None
    user_id: Optional[str] = None
    role: Optional[str] = None


class UserInDB(BaseModel):
    """Modelo de usuario no banco de dados"""
    email: str
    hashed_password: str
    disabled: Optional[bool] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verificar senha
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Gerar hash de senha
    """
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Criar token de acesso JWT
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    Criar token de refresh JWT
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(oauth2_scheme)) -> TokenData:
    """
    Obter usuario atual do token JWT
    """
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        token_data = TokenData(**payload)
        
        # Verificar se e token de acesso
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token invalido",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        return token_data
    except JWTError as e:
        logger.error(f"Erro ao decodificar token: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_current_active_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """
    Verificar se usuario esta ativo
    """
    # TODO: Verificar no banco de dados se o usuario esta ativo
    # Por enquanto, apenas retorna o usuario
    return current_user


async def get_current_admin_user(current_user: TokenData = Depends(get_current_user)) -> TokenData:
    """
    Verificar se usuario e administrador
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Necessario ser administrador."
        )
    return current_user


# Funcoes de permissao
class RoleChecker:
    """Verificador de permissoes por role"""
    
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles
    
    async def __call__(self, current_user: TokenData = Depends(get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Role nao autorizada."
            )
        return current_user


# Funcoes utilitarias
def get_role_checker(allowed_roles: list[str]):
    """
    Criar verificador de role
    """
    return RoleChecker(allowed_roles)


# Permissoes pre-definidas
ADMIN_ONLY = RoleChecker(["admin"])
SUPERVISOR_OR_ADMIN = RoleChecker(["admin", "supervisor"])
OPERATOR_OR_HIGHER = RoleChecker(["admin", "supervisor", "operator"])

"""
Authentication Models - User, Token, Role
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid


@dataclass
class User:
    """Represents a user in the system"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    password_hash: str = ""
    company: Optional[str] = None
    country: str = "br"  # br or mx
    role: str = "user"  # user, admin, manager
    status: str = "active"  # active, suspended, deleted
    email_verified: bool = False
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    push_notification_token: Optional[str] = None
    last_login: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()
    
    def to_dict(self, include_password: bool = False) -> Dict[str, Any]:
        data = {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "name": self.name,
            "company": self.company,
            "country": self.country,
            "role": self.role,
            "status": self.status,
            "email_verified": self.email_verified,
            "phone": self.phone,
            "avatar_url": self.avatar_url,
            "preferences": self.preferences,
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
        if include_password:
            data["password_hash"] = self.password_hash
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        user = cls(
            id=data.get("id", str(uuid.uuid4())),
            email=data.get("email", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            password_hash=data.get("password_hash", ""),
            company=data.get("company"),
            country=data.get("country", "br"),
            role=data.get("role", "user"),
            status=data.get("status", "active"),
            email_verified=data.get("email_verified", False),
            phone=data.get("phone"),
            avatar_url=data.get("avatar_url"),
            preferences=data.get("preferences", {}),
            push_notification_token=data.get("push_notification_token"),
            last_login=datetime.fromisoformat(data["last_login"]) if data.get("last_login") else None,
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.utcnow(),
            updated_at=datetime.fromisoformat(data["updated_at"]) if data.get("updated_at") else datetime.utcnow()
        )
        return user


@dataclass
class Token:
    """Represents an authentication token"""
    access_token: str = ""
    refresh_token: str = ""
    token_type: str = "bearer"
    expires_in: int = 3600
    user: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "access_token": self.access_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
            "expires_in": self.expires_in,
            "user": self.user
        }


@dataclass
class LoginRequest:
    """Login request model"""
    email: str = ""
    password: str = ""
    remember_me: bool = False
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LoginRequest":
        return cls(
            email=data.get("email", ""),
            password=data.get("password", ""),
            remember_me=data.get("remember_me", False)
        )


@dataclass
class RegisterRequest:
    """Registration request model"""
    email: str = ""
    first_name: str = ""
    last_name: str = ""
    password: str = ""
    company: Optional[str] = None
    country: str = "br"
    phone: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RegisterRequest":
        return cls(
            email=data.get("email", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            password=data.get("password", ""),
            company=data.get("company"),
            country=data.get("country", "br"),
            phone=data.get("phone")
        )


@dataclass
class PasswordResetRequest:
    """Password reset request model"""
    email: str = ""
    token: str = ""
    new_password: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PasswordResetRequest":
        return cls(
            email=data.get("email", ""),
            token=data.get("token", ""),
            new_password=data.get("new_password", "")
        )


# Role definitions
ROLES = {
    "admin": {
        "name": "Administrator",
        "permissions": ["*"],
        "description": "Full access to all features and data"
    },
    "manager": {
        "name": "Manager",
        "permissions": [
            "read:users", "create:users", "update:users",
            "read:vehicles", "create:vehicles", "update:vehicles",
            "read:anomalies", "read:reports",
            "read:financial", "read:strategy"
        ],
        "description": "Manage users and vehicles, view reports"
    },
    "user": {
        "name": "User",
        "permissions": [
            "read:vehicles", "read:anomalies",
            "create:images", "read:reports",
            "read:own_data"
        ],
        "description": "Basic user with limited access"
    },
    "guest": {
        "name": "Guest",
        "permissions": ["read:public_data"],
        "description": "Read-only access to public information"
    }
}


def check_permission(user_role: str, permission: str) -> bool:
    """Check if user has a specific permission"""
    role_info = ROLES.get(user_role, ROLES["guest"])
    if "*" in role_info["permissions"]:
        return True
    return permission in role_info["permissions"]


def get_user_permissions(user_role: str) -> List[str]:
    """Get all permissions for a user role"""
    role_info = ROLES.get(user_role, ROLES["guest"])
    return role_info.get("permissions", [])

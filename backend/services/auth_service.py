"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

Authentication Service - User Management, Login, Registration
"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD


import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
import uuid
import secrets
import hashlib

from backend.models.auth import User, Token, LoginRequest, RegisterRequest, check_permission, ROLES
from backend.config.settings import settings
from backend.services.lowdataesc_integration import LOWDATAESCService

logger = logging.getLogger(__name__)


# In-memory user store (in production, use database)
class UserStore:
    def __init__(self):
        self.users: Dict[str, User] = {}
        self._initialize_default_users()
    
    def _initialize_default_users(self):
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Initialize with default admin and demo users"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        # Admin user
        admin_password = "admin123"
        admin_hash = self._hash_password(admin_password)
        admin = User(
            id=str(uuid.uuid4()),
            email="admin@kco.ai",
            first_name="Admin",
            last_name="User",
            password_hash=admin_hash,
            company="KCo by Cília,
            country="br",
            role="admin",
            email_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.users[admin.email.lower()] = admin
        
        # Demo user for Brazil
        demo_br_password = "demo123"
        demo_br_hash = self._hash_password(demo_br_password)
        demo_br = User(
            id=str(uuid.uuid4()),
            email="demo@kco.ai",
            first_name="Demo",
            last_name="Brazil",
            password_hash=demo_br_hash,
            company="Localiza",
            country="br",
            role="user",
            email_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.users[demo_br.email.lower()] = demo_br
        
        # Demo user for Mexico
        demo_mx_password = "demo123"
        demo_mx_hash = self._hash_password(demo_mx_password)
        demo_mx = User(
            id=str(uuid.uuid4()),
            email="demo.mx@kco.ai",
            first_name="Demo",
            last_name="Mexico",
            password_hash=demo_mx_hash,
            company="AXA Mexico",
            country="mx",
            role="user",
            email_verified=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.users[demo_mx.email.lower()] = demo_mx
        
        logger.info(f"Initialized {len(self.users)} default users")
    
    def _hash_password(self, password: str) -> str:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Hash password using SHA256 with salt"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{hashed}"
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Verify password against hashed password"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        try:
            salt, hashed = hashed_password.split(":")
            new_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return new_hash == hashed
        except:
            return False
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Get user by email address"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        return self.users.get(email.lower())
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Get user by ID"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        for user in self.users.values():
            if user.id == user_id:
                return user
        return None
    
    def create_user(self, user: User) -> User:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Create a new user"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        user.email = user.email.lower()
        user.id = str(uuid.uuid4())
        user.created_at = datetime.utcnow()
        user.updated_at = datetime.utcnow()
        self.users[user.email] = user
        logger.info(f"Created user: {user.email}")
        return user
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Optional[User]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Update user information"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        user.updated_at = datetime.utcnow()
        logger.info(f"Updated user: {user.email}")
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Delete a user"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        user = self.get_user_by_id(user_id)
        if not user:
            return False
        
        del self.users[user.email.lower()]
        logger.info(f"Deleted user: {user.email}")
        return True
    
    def list_users(self, role: Optional[str] = None) -> List[User]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
List all users, optionally filtered by role"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        users = list(self.users.values())
        if role:
            users = [u for u in users if u.role == role]
        return users


class AuthService:
    """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Authentication service for user management"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

    
    def __init__(self):
        self.user_store = UserStore()
        self.lowdataesc = LOWDATAESCService()
        self._init_jwt_handler()
    
    def _init_jwt_handler(self):
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Initialize JWT handler"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        try:
            from ML.auth.jwt_handler import JWTHandler, jwt_handler
            self.jwt_handler = jwt_handler
        except ImportError:
            # Fallback to simple token generation
            self.jwt_handler = None
            logger.warning("JWT handler not available, using fallback")
    
    def login(self, login_request: LoginRequest) -> Tuple[bool, Optional[Token], Optional[str]]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        Authenticate user and return token
        
        Returns:
            Tuple of (success, token, error_message)
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        try:
            user = self.user_store.get_user_by_email(login_request.email)
            if not user:
                return False, None, "User not found"
            
            if not self.user_store.verify_password(login_request.password, user.password_hash):
                return False, None, "Invalid password"
            
            if user.status != "active":
                return False, None, "Account is not active"
            
            # Generate tokens
            access_token = self._generate_access_token(user)
            refresh_token = self._generate_refresh_token(user)
            
            # Update last login
            user.last_login = datetime.utcnow()
            user.updated_at = datetime.utcnow()
            
            # Create token response
            token = Token(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=3600,
                user=user.to_dict()
            )
            
            logger.info(f"User logged in: {user.email}")
            return True, token, None
            
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, None, str(e)
    
    def register(self, register_request: RegisterRequest) -> Tuple[bool, Optional[User], Optional[str]]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        Register a new user
        
        Returns:
            Tuple of (success, user, error_message)
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        try:
            # Check if user already exists
            existing_user = self.user_store.get_user_by_email(register_request.email)
            if existing_user:
                return False, None, "User already exists"
            
            # Validate email
            if "@" not in register_request.email:
                return False, None, "Invalid email address"
            
            # Validate password
            if len(register_request.password) < 6:
                return False, None, "Password must be at least 6 characters"
            
            # Create user
            password_hash = self.user_store._hash_password(register_request.password)
            user = User(
                email=register_request.email,
                first_name=register_request.first_name,
                last_name=register_request.last_name,
                password_hash=password_hash,
                company=register_request.company,
                country=register_request.country,
                role="user",
                email_verified=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            created_user = self.user_store.create_user(user)
            
            logger.info(f"User registered: {created_user.email}")
            return True, created_user, None
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, None, str(e)
    
    def _generate_access_token(self, user: User) -> str:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Generate access token for user"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        if self.jwt_handler:
            return self.jwt_handler.create_access_token(user.to_dict())
        
        # Fallback token generation
        import base64
        import json
        payload = {
            "sub": user.id,
            "email": user.email,
            "role": user.role,
            "country": user.country,
            "iat": datetime.utcnow().timestamp(),
            "exp": (datetime.utcnow() + timedelta(hours=24)).timestamp()
        }
        encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
        signature = hashlib.sha256((encoded + settings.SECRET_KEY).encode()).hexdigest()
        return f"{encoded}.{signature}"
    
    def _generate_refresh_token(self, user: User) -> str:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Generate refresh token for user"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        if self.jwt_handler:
            return self.jwt_handler.create_refresh_token(user.to_dict())
        
        # Fallback token generation
        import base64
        import json
        payload = {
            "sub": user.id,
            "type": "refresh",
            "iat": datetime.utcnow().timestamp(),
            "exp": (datetime.utcnow() + timedelta(days=7)).timestamp()
        }
        encoded = base64.urlsafe_b64encode(json.dumps(payload).encode()).decode()
        signature = hashlib.sha256((encoded + settings.SECRET_KEY).encode()).hexdigest()
        return f"{encoded}.{signature}"
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Validate access token and return user data"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        if self.jwt_handler:
            token_data = self.jwt_handler.decode_token(token)
            if token_data:
                user = self.user_store.get_user_by_id(token_data.user_id)
                if user:
                    return user.to_dict()
            return None
        
        # Fallback validation
        try:
            import base64
            import json
            parts = token.split(".")
            if len(parts) != 2:
                return None
            
            payload = json.loads(base64.urlsafe_b64decode(parts[0]).decode())
            expected_signature = hashlib.sha256((parts[0] + settings.SECRET_KEY).encode()).hexdigest()
            
            if parts[1] != expected_signature:
                return None
            
            if payload.get("exp") < datetime.utcnow().timestamp():
                return None
            
            user = self.user_store.get_user_by_id(payload.get("sub"))
            if user:
                return user.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None
    
    def refresh_token(self, refresh_token: str) -> Tuple[bool, Optional[Token], Optional[str]]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Refresh access token using refresh token"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        try:
            if self.jwt_handler:
                token_data = self.jwt_handler.decode_token(refresh_token)
                if not token_data or token_data.token_type != "refresh":
                    return False, None, "Invalid refresh token"
                
                user = self.user_store.get_user_by_id(token_data.user_id)
                if not user:
                    return False, None, "User not found"
                
                # Generate new tokens
                access_token = self._generate_access_token(user)
                new_refresh_token = self._generate_refresh_token(user)
                
                token = Token(
                    access_token=access_token,
                    refresh_token=new_refresh_token,
                    token_type="bearer",
                    expires_in=3600,
                    user=user.to_dict()
                )
                
                return True, token, None
            
            # Fallback implementation
            return False, None, "Token refresh not implemented in fallback mode"
            
        except Exception as e:
            logger.error(f"Token refresh error: {e}")
            return False, None, str(e)
    
    def get_current_user(self, token: str) -> Optional[User]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Get current user from token"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        user_data = self.validate_token(token)
        if user_data:
            return self.user_store.get_user_by_id(user_data.get("id"))
        return None
    
    def check_user_permission(self, token: str, permission: str) -> bool:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Check if user has specific permission"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        user = self.get_current_user(token)
        if not user:
            return False
        return check_permission(user.role, permission)
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Get user by ID"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        return self.user_store.get_user_by_id(user_id)
    
    def list_users(self, role: Optional[str] = None) -> List[Dict[str, Any]]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
List users with optional role filter"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        users = self.user_store.list_users(role)
        return [u.to_dict() for u in users]
    
    def update_user(self, user_id: str, updates: Dict[str, Any]) -> Tuple[bool, Optional[User], Optional[str]]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Update user information"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        try:
            user = self.user_store.update_user(user_id, updates)
            if user:
                return True, user, None
            return False, None, "User not found"
        except Exception as e:
            logger.error(f"Update user error: {e}")
            return False, None, str(e)
    
    def change_password(self, user_id: str, old_password: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Change user password"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        try:
            user = self.user_store.get_user_by_id(user_id)
            if not user:
                return False, "User not found"
            
            if not self.user_store.verify_password(old_password, user.password_hash):
                return False, "Old password is incorrect"
            
            if len(new_password) < 6:
                return False, "New password must be at least 6 characters"
            
            user.password_hash = self.user_store._hash_password(new_password)
            user.updated_at = datetime.utcnow()
            
            logger.info(f"Password changed for user: {user.email}")
            return True, None
            
        except Exception as e:
            logger.error(f"Change password error: {e}")
            return False, str(e)
    
    def request_password_reset(self, email: str) -> Tuple[bool, Optional[str]]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Request password reset (generates reset token)"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        try:
            user = self.user_store.get_user_by_email(email)
            if not user:
                return False, "User not found"
            
            # Generate reset token
            reset_token = secrets.token_urlsafe(32)
            user.preferences["reset_token"] = reset_token
            user.preferences["reset_token_expires"] = (datetime.utcnow() + timedelta(hours=1)).isoformat()
            user.updated_at = datetime.utcnow()
            
            # In production, send email with reset link
            logger.info(f"Password reset requested for: {user.email}")
            
            return True, None
            
        except Exception as e:
            logger.error(f"Password reset error: {e}")
            return False, str(e)
    
    def reset_password(self, email: str, token: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD
Reset password using reset token"""
KCo by Cília | Laboratory of K and RockNewVenture
Old But Gold TR8 IVSTO | Pre-Seed Target: $30M+ USD

        try:
            user = self.user_store.get_user_by_email(email)
            if not user:
                return False, "User not found"
            
            stored_token = user.preferences.get("reset_token")
            token_expires = user.preferences.get("reset_token_expires")
            
            if not stored_token or stored_token != token:
                return False, "Invalid reset token"
            
            if token_expires:
                expires_time = datetime.fromisoformat(token_expires)
                if datetime.utcnow() > expires_time:
                    return False, "Reset token has expired"
            
            if len(new_password) < 6:
                return False, "New password must be at least 6 characters"
            
            user.password_hash = self.user_store._hash_password(new_password)
            user.preferences.pop("reset_token", None)
            user.preferences.pop("reset_token_expires", None)
            user.updated_at = datetime.utcnow()
            
            logger.info(f"Password reset for user: {user.email}")
            return True, None
            
        except Exception as e:
            logger.error(f"Reset password error: {e}")
            return False, str(e)


# Singleton instance
auth_service = AuthService()

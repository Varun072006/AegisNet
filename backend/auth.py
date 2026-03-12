from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config import settings
from typing import List

security = HTTPBearer()

# Role definitions and permissions
ROLES = {
    "admin": ["manage_models", "view_analytics", "view_logs", "chat"],
    "developer": ["view_analytics", "chat"],
    "viewer": ["view_analytics"]
}

def verify_api_key(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Simple API Key verification."""
    if credentials.data != settings.default_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.data

def get_current_user_role(api_key: str = Depends(verify_api_key)):
    """Return the role associated with the API key."""
    # In production, this would be a DB lookup. 
    # For AegisNet v2, we treat the default key as 'admin'.
    return "admin"

def require_permission(permission: str):
    """Dependency to check if the current user has a specific permission."""
    def decorator(role: str = Depends(get_current_user_role)):
        if permission not in ROLES.get(role, []):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted for role: {role}",
            )
        return role
    return decorator

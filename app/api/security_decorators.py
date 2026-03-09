from __future__ import annotations

from functools import wraps
import hashlib

from fastapi import Depends, HTTPException, Security
from fastapi.security import APIKeyHeader

from app.models.auth import Role, User

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# SHA256 hashes for sample keys (replace with production store)
MOCK_USERS: dict[str, User] = {
    "246bb403d6082880ab88f8422b8540ff78b7ba0b2306157fa7022fefb3a4ecf7": User(
        id="user_admin",
        email="admin@legal-rag.com",
        role=Role.ADMIN,
        api_key_hash="246bb403d6082880ab88f8422b8540ff78b7ba0b2306157fa7022fefb3a4ecf7",
    ),
    "35cd23cc610c61fcd916f67d38579126fc26312d590fb51e18f837f074765110": User(
        id="user_query",
        email="user@legal-rag.com",
        role=Role.QUERY,
        api_key_hash="35cd23cc610c61fcd916f67d38579126fc26312d590fb51e18f837f074765110",
    ),
}


async def get_current_user(api_key: str = Security(api_key_header)) -> User:
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing X-API-Key header")

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    user = MOCK_USERS.get(key_hash)

    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid or inactive API key")

    return user


def require_role(*allowed_roles: Role):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, user: User = Depends(get_current_user), **kwargs):
            if user.role == Role.ADMIN:
                return await func(*args, user=user, **kwargs)

            if user.role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Forbidden. Required roles: {[r.value for r in allowed_roles]}",
                )

            return await func(*args, user=user, **kwargs)

        return wrapper

    return decorator

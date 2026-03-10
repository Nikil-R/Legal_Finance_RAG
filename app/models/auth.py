from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class Role(str, Enum):
    """User roles with hierarchical permissions."""

    ADMIN = "admin"
    INGEST = "ingest"
    QUERY = "query"
    READONLY = "readonly"


class User(BaseModel):
    """User account authenticated via API key."""

    id: str
    email: str
    role: Role
    api_key_hash: str
    rate_limit: int = 100
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        frozen = True

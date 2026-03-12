from app.api.routes.documents import router as documents_router
from app.api.routes.health import router as health_router
from app.api.routes.query import router as query_router
from app.api.routes.tools import router as tools_router
from app.api.routes.user_documents import router as user_documents_router

__all__ = [
    "documents_router",
    "health_router",
    "query_router",
    "tools_router",
    "user_documents_router",
]

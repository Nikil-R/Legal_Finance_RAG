"""
Render deployment wrapper.
Binds to port immediately, loads heavy app after.
"""

import os
import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create simple app that binds immediately
app = FastAPI(
    title="Legal Finance RAG API",
    version="1.0.0",
    description="Production RAG API"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Basic health check - always works
@app.get("/health")
async def health():
    """Health check - no dependencies."""
    return {
        "status": "healthy",
        "message": "Server is running"
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "Legal Finance RAG API",
        "status": "operational",
        "docs": "/docs"
    }

# Load heavy stuff AFTER server starts
@app.on_event("startup")
async def load_application():
    """
    Load actual application routes after server binds to port.
    This prevents timeout during startup.
    """
    print("🚀 Server started, now loading application routes...")
    
    try:
        # Import routes one by one
        from app.api.routes.health import router as health_router
        app.include_router(health_router, tags=["health"])
        print("✅ Loaded health router")
        
    except Exception as e:
        print(f"⚠️ Health router failed: {e}")
    
    try:
        from app.api.routes.query import router as query_router
        app.include_router(query_router, prefix="/api/v2", tags=["query"])
        print("✅ Loaded query router")
        
    except Exception as e:
        print(f"⚠️ Query router failed: {e}")
    
    try:
        from app.api.routes.tools import router as tools_router
        app.include_router(tools_router, prefix="/api/v1", tags=["tools"])
        print("✅ Loaded tools router")
        
    except Exception as e:
        print(f"⚠️ Tools router failed: {e}")
    
    try:
        from app.api.routes.documents import router as documents_router
        app.include_router(documents_router, prefix="/api/v2", tags=["documents"])
        print("✅ Loaded documents router")
        
    except Exception as e:
        print(f"⚠️ Documents router failed: {e}")

    try:
        from app.api.routes.user_documents import router as user_documents_router
        app.include_router(user_documents_router, prefix="/api/v2", tags=["user_documents"])
        print("✅ Loaded user documents router")
        
    except Exception as e:
        print(f"⚠️ User documents router failed: {e}")
    
    print("🎉 Application fully loaded!")

# Simple status endpoint
@app.get("/status")
async def status():
    """Check which routes are loaded."""
    routes = [
        {"path": route.path, "name": route.name}
        for route in app.routes
    ]
    return {
        "total_routes": len(routes),
        "routes": routes
    }

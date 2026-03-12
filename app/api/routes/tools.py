from fastapi import APIRouter, Depends
from typing import List, Dict, Any
from app.api.dependencies import get_tool_registry
from app.tools.registry import ToolRegistry
from app.api.security import AuthenticatedUser, require_role
from app.models.auth import Role

router = APIRouter(prefix="/tools", tags=["Tools"])

@router.get(
    "",
    summary="List available tools",
    description="Returns a list of all tools available for tool-augmented generation."
)
async def list_tools(
    user: AuthenticatedUser = Depends(require_role(Role.QUERY, Role.ADMIN)),
    registry: ToolRegistry = Depends(get_tool_registry)
) -> Dict[str, Any]:
    """
    Endpoint to list available tools.
    """
    tools = registry.list_tools()
    detailed_tools = registry.get_tool_definitions()
    
    return {
        "tools": detailed_tools,
        "summary": tools,
        "total": len(tools)
    }
